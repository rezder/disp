import asyncio as ass
from websockets.asyncio import client as wsclient
import json
import asyncudp

from displays import Displays
from dispdata import DispData
from config import Config
from skdata import SkData
from status import Status
import guirequest as gr


class Subscription:
    """
    Small subcription class to keep track of how
    many display use the same paths.
    """
    def __init__(self):
        self.list = dict()

    def subscribers(self) -> set:
        res = set()
        for (p, i) in self.list.items():
            if i > 0:
                res.add(p)
        return res

    def add(self, paths: set) -> set:
        res = set()
        for p in paths:
            if p in self.list.keys():
                self.list[p] = self.list[p]+1
                if self.list[p] == 1:
                    res.add(p)
            else:
                self.list[p] = 1
                res.add(p)
        return res

    def remove(self, paths: set) -> set:
        res = set()
        for p in paths:
            if p in self.list.keys():
                self.list[p] = self.list[p]-1
                if self.list[p] == 0:
                    res.add(p)
                if self.list[p] == -1:
                    self.list[p] = 0
        return res

    def __str__(self) -> str:
        res = "{}".format(self.list)
        return res


async def guiMsg(ws: wsclient.ClientConnection,
                 queue: ass.Queue[gr.GuiReq],
                 skData: SkData,
                 conf: Config,
                 status: Status,
                 displays: Displays):
    """
    Async handler of gui requst when the async
    server is running. Currently only
    change of display.
    """
    sub = Subscription()
    while True:

        req = await queue.get()
        if req.tp == gr.chgView:
            dispId = req.id
            if req.data is None:  # New
                newViewId, newView = conf.dispGetView(dispId)
            else:  # Change
                newViewId = req.data
                newView = conf.viewsGetView(newViewId)

            # conf read is a problem as it could be change
            # while wait on messages better to have all
            # info in queue. if display not in mod conf or
            # fail
            status.addDispOn(dispId, newViewId)
            txt = "Changing view on display: {} to view: {}"
            status.setTxt(txt.format(dispId, newViewId))
            oldView = displays.setView(dispId, newView)
            newSubSet = sub.add(set(newView.keys()))
            unsubSet = sub.remove(set(oldView.keys()))
            if len(newSubSet) > 0 or len(unsubSet) > 0:
                subSet = sub.subscribers()
                await skSub(subSet, skData, ws)

            status.setDoneCmd()
        if req.tp == gr.alarmDis:
            path = req.id
            isEnable = not req.data
            path = skData.getPath(path)
            path.setEnableAlarm(isEnable)
            atxt = "disable"
            if isEnable:
                atxt = "enable"
            txt = "Alarm on {} {}"
            status.setTxt(txt.format(path.label, atxt))
            status.setDoneCmd()


async def skSub(subSet: set,
                skData: SkData,
                ws: wsclient.ClientConnection):
    """
    Change signal k subsription.
    it is a seperate function to keep the await
    call together making it a task could split
    the calls apart.
    """

    await ws.send(skData.msgUnsubAll())
    if len(subSet) > 0:
        await ws.send(skData.msgSubPaths(subSet))


async def signalkMsg(ws, displays: Displays, skData, status):
    """
    Async function for handle websoket signal k incomming messages
    """
    async for jsonMsg in ws:
        inkMsgs = parseSkUpdates(jsonMsg, skData, status)
        for (m, p) in inkMsgs:
            await displays.display(m, p)


def parseSkUpdates(skMsg: str,
                   skData,
                   status: Status) -> list[tuple[DispData, str]]:
    """
    Parse the signal k websocet delta updates messages.

    :param skMsq: The signal k websocet json text message.
    :param skData: Signalk k information.
    :param status: Server status.
    :return: Returns a list of display messages.
    :rtype: list[bytes]
    """
    inkMsgs = list()
    jsObj = json.loads(skMsg)
    if "updates" in jsObj:
        for delta in jsObj["updates"]:
            # source can be used to filter unwanted sources
            # but subscribe msg could be changed to include
            # .values[$source]
            # if "source" in delta:
            #     print("source: {}".format(delta["source"]))
            #     if "label" in delta["source"]:
            #         print("label: {}".format(delta["source"]["label"]))

            for v in delta["values"]:
                try:
                    pathId = v["path"]
                    value = v["value"]
                    dispData = skData.getPath(pathId).createDispData(value)
                    if dispData is not None:
                        inkMsgs.append((dispData, pathId))
                except KeyError:
                    t = "Faild to find path: {} on display"
                    status.setTxt(t.format(v["path"]))
    else:
        status.setTxt("Signal k unprocced messages: {}".format(jsObj))

    return inkMsgs


async def udpSubscribe(displays: Displays,
                       conf: Config,
                       status: Status,
                       queue: ass.Queue):
    port = conf.getSubPort()
    ip = conf.getBroadcastIp()
    subSock = await asyncudp.create_socket(local_addr=(ip, port))
    status.setTxt("Broadcast subscriber :{}:{}".format(ip, port))
    while True:
        try:
            d, addr = await subSock.recvfrom()
            id = d.decode("ascii")
            id = id.strip()
            if conf.dispIs(id):
                isNew = displays.add(id, addr[0], addr[1])
                status.setTxt("New display added id: {}".format(id))
                if isNew:
                    req = gr.GuiReq(gr.chgView, id)
                    await queue.put(req)
            else:
                status.setTxt("Display: {} refused".format(id))
        except ass.CancelledError as ex:
            subSock.close()
            raise ex
