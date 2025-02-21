import asyncio as ass
from websockets.asyncio import client as wsclient
from displays import Displays
from dispdata import DispData
from config import Config
from skdata import SkData
from status import Status
import json
import asyncudp
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
        if req.tp == gr.chgTab:
            id = req.id
            newTab = conf.getCurTabPaths(id)
            newTabId = conf.getCurTabId(id)
            txt = "Changing tab on display id: {} to tab: {}"
            status.setTxt(txt.format(id, newTabId))
            if displays.isIn(id):
                newTab = conf.getCurTabPaths(id)
                oldTab = displays.setTab(id, newTab)
                newSubSet = sub.add(set(newTab.keys()))
                unsubSet = sub.remove(set(oldTab.keys()))
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

        if req.tp == gr.disDisp:
            isDisable = conf.getMacs()[req.id]["isDisable"]
            isIn = displays.isIn(req.id)
            txt = "Display: {} was not disabled/enabled".format(id)
            if isIn and isDisable:
                status.removeOn(req.id)
                txt = "Disabling display: {}".format(id)
                tab = displays.getDispTab(req.id)
                await displays.removeBleDisp(req.id)
                unsubSet = sub.remove(set(tab.keys()))
                if len(unsubSet) > 0:
                    subSet = sub.subscribers()
                    await skSub(subSet, skData, ws)
            if not isIn and not isDisable:
                status.addOn(req.id)
                txt = "Enabling display: {}".format(id)
                macObj = conf.getMacs()[req.id]
                displays.addBleDisp(req.id, macObj)
                tab = conf.getCurTabPaths(req.id)
                _ = displays.setTab(req.id, tab)
                newSubSet = sub.add(set(tab.keys()))
                if len(newSubSet) > 0:
                    subSet = sub.subscribers()
                    await skSub(subSet, skData, ws)
            status.setTxt(txt)
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
            if conf.isDefined(id):
                isNew = displays.add(id, addr[0], addr[1])
                status.setTxt("New display added id: {}".format(id))
                if isNew:
                    req = gr.GuiReq(gr.chgTab, id)
                    await queue.put(req)
                    status.addOn(id)
            else:
                status.setTxt("Display: {} refused".format(id))
        except ass.CancelledError as ex:
            subSock.close()
            raise ex
