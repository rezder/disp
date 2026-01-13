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
from jsonptr import ErrPtr

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
        self.loop = None
        self.queue = None
        self.queueShutDownEvent = None

    async def _serve(self, rconf: Config):
        """
        The primary async function.
        Listens for signalk data and gui signals.
        """
        skData = SkData(rconf, self.status)
        await serve(self.status,
                    self.queueShutDownEvent,
                    self.queue,
                    skData,
                    rconf)

    def _startAsync(self, rconf: Config):
        """
        Setup the async loop
        """
        self.loop = ass.new_event_loop()
        ass.set_event_loop(self.loop)
        self.queue = ass.Queue(10)
        self.queueShutDownEvent = ass.Event()
        self.loop.run_until_complete(self._serve(rconf))

    def start(self) -> tuple[bool, Config]:

        """
        Starts the async thread with the signalk display
        server.
        """
        ok = False
        rconf = None
        if not self.exist():
            ok = self.status.setStartServer()
            if ok:
                rconf = Config()
                self.serverThread = threading.Thread(
                    target=self._startAsync, args=(rconf,))
                self.serverThread.start()
        return ok, rconf

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
        else:
            if not self.serverThread.is_alive():
                self.status.setServerDone()
                self.loop = None
                self.queue = None
                self.queueShutDownEvent = None
                self.serverThread = None
                done = True
        return done

    def pause(self):
        """
        Not implemented I do not know if I need it.
        """
        pass

    def newDispIdValidation(self,
                            dispId: str,
                            isMacVal: bool = False) -> tuple[bool, str]:
        isOk = True
        errMsg = None
        if dispId == "":
            isOk = False
            errMsg = "Display id is empty"
        else:
            isDisp = self.conf.dispIs(dispId)
            isMac = self.conf.dispIsBle(dispId)
            isUpd = isDisp and not isMac
            if isMacVal:
                if isUpd:
                    isOk = False
                    errMsg = "Display: {} is an Udp display".format(dispId)
            else:
                if isMac:
                    isOk = False
                    errMsg = "Display: {} is an Ble display".format(dispId)
        return isOk, errMsg

    def chgDispView(self, dispId, viewId) -> bool:
        """
        Send message to Change view on active display.
        Server may not be ready to recieve the msg
        return true if messages send.
        """
        ok = self.status.setChgView(dispId, viewId)
        if ok:
            req = gr.GuiReq(gr.chgView, dispId)
            req.setData(viewId)
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

    def pathsSave(self,
                  pathsJso: dict,
                  alarmsJso: dict,
                  bigsJso: dict) -> tuple[str, list[ErrPtr]]:
        self.conf.pathsSet(pathsJso, alarmsJso, bigsJso)
        errTxt, errPtrs = self.conf.validate()
        if len(errPtrs) != 0:
            self.conf.rollBack()
        else:
            self.conf.save()
        return errTxt, errPtrs

    def displaysSave(self, disps, macs, views) -> tuple[str, list[ErrPtr]]:
        self.conf.dispsSet(disps, macs, views)
        errTxt, errPtrs = self.conf.validate()
        if len(errPtrs) != 0:
            self.conf.rollBack()
        else:
            self.conf.save()
        return errTxt, errPtrs

    def settingsSave(self, jsoObj) -> tuple[str, list[ErrPtr]]:
        self.conf.settingsSave(jsoObj)
        errTxt, errPtrs = self.conf.validate()
        if len(errPtrs) != 0:
            self.conf.rollBack()
        else:
            self.conf.save()
        return errTxt, errPtrs


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
        req = gr.GuiReq(gr.chgView, dpId)
        queue.put_nowait(req)
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
