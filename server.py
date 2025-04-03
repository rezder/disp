import threading
import asyncio as ass
from websockets.asyncio import client as wsclient
from websockets.exceptions import InvalidStatus
from functools import partial

import state
from displays import Displays
from config import Config
from skdata import SkData
from status import Status
import handler
import guirequest as gr

signalkUrl = "ws://localhost:3000/signalk/v1/stream?subscribe=none"
#  signalkUrl = "ws://localhost:3000/signalk/v1/stream"


class DispServer:
    """
    The display server handle all communications
    between arduino display and signalk server.
    I like functions so I split the methods in to functions
    So it is clear what data is used.
    """

    def __init__(self):
        self.status = Status()
        self.conf = Config()
        self.skData = SkData(self.conf, self.status)
        self.loop = None
        self.queue = None
        self.queueShutDownEvent = None

    async def _serve(self):
        """
        The primary async function.
        Listens for signalk data and gui signals.
        """
        await serve(self.status,
                    self.queueShutDownEvent,
                    self.queue,
                    self.skData,
                    self.conf)

    def _startAsync(self):
        """
        Setup the async loop
        """
        self.loop = ass.new_event_loop()
        ass.set_event_loop(self.loop)
        self.queue = ass.Queue(10)
        self.queueShutDownEvent = ass.Event()
        self.loop.run_until_complete(self._serve())

    def start(self) -> bool:

        """
        Starts the async thread with the signalk display
        server.
        """
        ok = False
        if not self.exist():
            ok = self.status.setStartServer()
            if ok:
                self.serverThread = threading.Thread(
                    target=self._startAsync)
                self.serverThread.start()
        return ok

    def exist(self) -> bool:
        """
        Returns if the asyncio server thread
        is started.
        """
        return self.loop is not None

    def stop(self) -> bool:
        """
        Send the stop signal to the async server
        """
        # self.queue.shutdown() methods comes in python 3.13
        ok = False
        if self.exist():
            ok = self.status.setStopServer()
            if ok:
                self.loop.call_soon_threadsafe(queueShutDown,
                                               self.queueShutDownEvent)
        else:
            ok = True
        return ok

    def stopClean(self) -> bool:
        """
        Check if the async server is stopped and
        if it is stopped do some cleanup.
        Cleanup removed the thread.
        """
        done = False
        if not self.exist():
            done = True
            self.conf.save()
        else:
            if not self.serverThread.is_alive():
                self.status.setServerDone()
                self.loop = None
                self.queue = None
                self.queueShutDownEvent = None
                self.serverThread = None
                self.skData.clearBuffers()
                done = True
                self.conf.save()
        return done

    def pause(self):
        """
        Not implemented I do not know if I need it.
        """
        pass

    def addNewUdpDisp(self, id: str) -> bool:
        """
        Adds a new display to the configuration
        only allowed if the async server is
        not running.
        """
        upd = False
        if not self.exist():
            if self.conf.dispAdd(id):
                upd = True
        return upd

    def addNewBleDisp(self, id: str, mac: str) -> bool:
        """
        Adds a new display with a mac address
        if not new only update mac address.
        return true if new. Server must
        not be running to succeed
        """
        upd = False
        if not self.exist():
            if self.conf.dispAdd(id):
                upd = True
            self.conf.dispUpdMac(id, mac)
        return upd

    def disableDisp(self, id: str, isDisable: bool) -> bool:
        """
        Disable a display. Not posible for udp displays.
        If server is busy with something else return
        false
        """
        ok = False
        if not self.exist():
            self.conf.dispSetBleDisable(id, isDisable)
            ok = True
        else:
            ok = self.status.setDisableDisp(id, isDisable)
            if ok:
                self.conf.dispSetBleDisable(id, isDisable)
                req = gr.GuiReq(gr.disDisp, id)
                _ = self.loop.call_soon_threadsafe(queueAdd,
                                                   self.queue,
                                                   req,
                                                   self.status)
        return ok

    def changeDisp(self, id, tabId) -> bool:
        """
        Change current tab used by display
        and inform the server that display have been
        change. If the server is running
        it may not be ready to recieve the msg
        if the that is the case not update.
        """
        ok = False
        if not self.exist():
            self.conf.dispSetTabId(id, tabId)
            ok = True
        else:
            ok = self.status.setChgTab(id, tabId)
            if ok:
                self.conf.dispSetTabId(id, tabId)
                req = gr.GuiReq(gr.chgTab, id)
                _ = self.loop.call_soon_threadsafe(queueAdd,
                                                   self.queue,
                                                   req,
                                                   self.status)
        return ok

    def alarmDisable(self, path: str, label: str, isDis: bool):
        ok = self.status.setAlarmDis(label, isDis)
        if ok:
            req = gr.GuiReq(gr.alarmDis, path)
            req.setData(isDis)
            _ = self.loop.call_soon_threadsafe(queueAdd,
                                               self.queue,
                                               req,
                                               self.status)

    def getStatus(self) -> (bool, str, int, int, set, list):
        return self.status.getStatus()

    def pathsSave(self, pathId, pathJson) -> tuple[bool,
                                                   set[str],
                                                   str,
                                                   dict]:
        """
        Saves a path setting.
        Validate before saving:
        Buffer frequenz must be less or equal to buffer size.
        Saving: save to file, update conf create new skData
        :param pathId: the path that is being saved
        :param pathJson: The path json object
        :returns:
        - isOk     - If path saved
        - errFlds  - List of json fld headers causing the error
        - errTxt   - Error text
        - pjjj -(pathsJson,alarmsJson,bigJson)
        """
        isOk = True
        errFlds = set()
        errTxt = ""
        pjjj = None
        # TODO one day translate json ids to gui flds
        # Make a function that translate marked text like
        # @path@ to Path. It just needs a dict of flds
        if not self.exist():
            fld = "bufFreq"
            if pathJson[fld] > pathJson["bufSize"]:
                isOk = False
                errFlds.add(fld)
                txt = "\nError! Buffer frequenze must"\
                    " not be bigger than buffer size"
                errTxt = errTxt + txt
        else:
            isOk = False
            errTxt = errTxt+"\nError! Server is running!"\
                " Do not update settings!"
        if isOk:
            self.conf.pathsSetPath(pathId, pathJson)
            self.conf.save()
            self.skData = SkData(self.conf, self.status)
            pjjj = self.conf.pathsGet(),
        return isOk, errFlds, errTxt, pjjj

    def pathsDelete(self, pathId):
        """
        Deletes a path setting.
        Validate before deleting:
        Reference paths must not be deleted,
        reference  tabs holds reference.
        deleting: save to file, update conf create new skData
        :param path: the path that is being saved
        :returns:
        - isOk     - If path deleted
        - errTxt   - Error text
        - pjj - pathsJson,alarmsJson,bigsJson
        """
        isOk = True
        errTxt = ""
        pjjj = None
        tabRefs, bigs, alarms = self.conf.pathsGetRefs(pathId)
        if len(tabRefs) > 0:
            isOk = False
            txt = "Error! Path: {} is reference on tabs:\n{}."
            errTxt = errTxt + txt.format(pathId, tabRefs)
        if len(bigs) > 0:
            isOk = False
            txt = ""
            if len(errTxt) > 0:
                txt = "\n"
            txt = "Error! Path: {} is reference on bigs:\n{}."
            errTxt = errTxt + txt.format(pathId, bigs)
        if len(alarms) > 0:
            isOk = False
            txt = ""
            if len(errTxt) > 0:
                txt = "\n"
            txt = "Error! Path: {} is reference on alarms:\n{}."
            errTxt = errTxt + txt.format(pathId, alarms)

        if isOk:
            self.conf.pathsDeletePath(pathId)
            self.conf.save()
            self.skData = SkData(self.conf, self.status)
            pjjj = self.conf.pathsGet()

        return isOk, errTxt, pjjj


async def serve(status: Status,
                done: ass.Event,
                queue: ass.Queue,
                skData: SkData,
                conf: Config):
    """
    The async task that handles the streams and gui request.
    It is one task group to handle all the signals at the same
    time most ofcourse from signal k.

    :parm status: The server status information use a thread lock.
    :param done: A async event to stop the server as the queue cant
    be closed before next python upgrade.
    :param queue: Async queue for the qui requests.
    :param skData: The signalk information.
    :param conf: Object holds the configured data.
    """
    displays = Displays(status)
    ids = displays.addBleDisps(conf.dispGetBles())
    for dpId in ids:
        req = gr.GuiReq(gr.chgTab, dpId)
        queue.put_nowait(req)
        status.addOn(dpId)
    exCb = partial(wsExceptionCb, done, status)  # Exception callback
    try:
        status.setTxt("Connecting to websocet")
        async for ws in wsclient.connect(signalkUrl,
                                         process_exception=exCb,
                                         open_timeout=5.0,
                                         close_timeout=10.0
                                         ):
            txt = "Connected to websocet"
            status.updateRunningStat(state.running, txt)

            tasks = [ass.create_task(done.wait(), name="Stop command")]
            msgTask = ass.create_task(handler.signalkMsg(ws,
                                                         displays,
                                                         skData,
                                                         status),
                                      name="Signal k")
            tasks.append(msgTask)
            tasks.append(ass.create_task(handler.guiMsg(ws,
                                                        queue,
                                                        skData,
                                                        conf,
                                                        status,
                                                        displays),
                                         name="Gui queue"))
            if conf.getSubUdpServerIsEnable():
                tasks.append(ass.create_task(handler.udpSubscribe(displays,
                                                                  conf,
                                                                  status,
                                                                  queue),
                                             name="Subscriber"))
            dones, runnings = await ass.wait(tasks,
                                             return_when=ass.FIRST_COMPLETED)

            # Cancel asyncio loops produce task errors
            # there is more incidents on it.
            # closing connection reduce errors.
            # could make my own loops.
            # This close ws remove h error from the msgTask
            if not msgTask.done():
                await ws.close()
                await msgTask
            else:
                await ws.close()

            await cleanTask(dones, runnings, status)
            if done.is_set() or True:  # TODO remove True for
                #                         restart after crash
                await skData.clearTask()
                ok = await displays.close()
                if not ok:
                    print("Some displays failed to turn off")
                status.setTxt("Async server done")
                # It leaves a pending task no name see
                # https://github.com/pytest-dev/pytest-asyncio/issues/759
                break
            else:
                txt = "Websocket down"
                status.updateRunningStat(state.conn, txt)

    except Exception as ex:
        _ = await displays.close()
        txt = "Failed in tasks with: {}".format(ex)
        status.updateRunningStat(state.broke, txt)

    if not done.is_set():
        txt = "Wifi connection failed"
        status.updateRunningStat(state.broke, txt)


async def cleanTask(dones, runnings, status):
    txt = "Task: {} finished closing server task"
    for t in dones:
        status.setTxt(txt.format(t.get_name()))
        ex = t.exception()
        if ex is not None:
            print("Task: {} failed with: {}".format(t.get_name(), ex))

    for t in runnings:
        print("canceling task: {}".format(t.get_name()))
        _ = t.cancel()

    for t in runnings:
        print("waiting for cancel task: {}".format(t.get_name()))
        try:
            await t
        except ass.CancelledError:
            pass


def queueAdd(queue, req: gr.GuiReq, status):
    """
    Adds to the change queue should run in the asyncio thread
    to make it thread safe.
    """
    try:
        queue.put_nowait(req)
    except ass.QueueFull:
        txt = "Queue is full failed to add to queue should not happen"
        status.setTxt(txt)


def queueShutDown(ev: ass.Event):
    """
    Sends the shoutdown signal to the asyncio server
    should run in the asyncio thread
    to make it thread safe.
    """
    print("setting shut down event")
    ev.set()


def wsExceptionCb(done: ass.Event,
                  status: Status,
                  exc: Exception) -> Exception | None:
    """
    Used by websocket client connection to handle exception
    when connecting.
    """
    if not done.is_set():
        txt = "Signal k server connection problem: {}"
        status.setTxt(txt.format(exc))

        if isinstance(exc, (EOFError, OSError, ass.TimeoutError)):
            status.setTxt(txt.format(exc))
            return None

        if isinstance(exc, InvalidStatus) and exc.response.status_code in [
                500,  # Internal Server Error
                502,  # Bad Gateway
                503,  # Service Unavailable
                504,  # Gateway Timeout
        ]:
            status.setTxt(txt.format(exc))
            return None

    return exc
