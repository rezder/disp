import time
from asyncudp import create_socket as udpSocket
import asyncio as ass

from status import Status
from dispdata import DispData
from flds import flds as ff


class Display:
    """
    Udp to control a display. it works together with udpsubscribe handler
    that takes incomming broadcast from the displays to establish
    a connection made for 4.2 e-paper. The udp is unreliable so signal
    can be missed and be doubled. The code should relect that.
    Ble is properly better and use less power but more complicated.

    """
    def __init__(self, id: str, ip: str, port: int, status: Status):
        self.addr = (ip, port)
        self.id = id
        self.status = status
        self.view = {}
        self.keepAliveTask = ass.create_task(self.keepAlive(),
                                             name="Keep Alive")
        self.keepAliveTime = 10.0
        self.actTs = time.monotonic()
        self.connTask = ass.create_task(udpSocket(remote_addr=self.addr),
                                        name="Udp connection")
        self.turnedOff = False
        self.isFullDD = False

    def __str__(self) -> str:
        txt = "Display: id:{}, on: {}, addr: {}"
        isOn = self.connTask is None
        res = txt.format(self.id, isOn, self.addr)
        return res

    async def keepAlive(self):
        cmd = 'K'
        sleep = self.keepAliveTime
        while True:
            await ass.sleep(sleep)
            ts = time.monotonic()
            sleep = self.keepAliveTime + self.actTs - ts
            if sleep < 0:
                self.checkConnTask()
                if self.connTask is None:
                    self.socket.sendto(bytearray(cmd, "ascii"), self.addr)
                    sleep = self.keepAliveTime
                    self.actTs = ts
                else:
                    sleep = self.keepAliveTime/2

    def setAddr(self, ip, port):
        self.addr = (ip, port)

    def setView(self, view: dict):
        self.view = view
        self.isFullDD = True

    def getView(self) -> dict:
        return self.view

    def checkConnTask(self):
        if self.connTask is not None and self.connTask.done():
            ex = self.connTask.exception()
            if ex is None:
                self.socket = self.connTask.result()
                self.connTask = None
                self.isFullDD = True
            else:
                txt = "Display id: {} udp connecting faild\nWith: {}"
                self.status.setTxt(txt.format(self.id, ex))
                self.connTask = ass.create_task(self.client.connect())

    def display(self, path: str, dds: dict[str, DispData]):
        if not self.turnedOff and (path in self.view or self.isFullDD):
            self.checkConnTask()
            if self.connTask is None:
                if self.isFullDD:
                    poss: list[int] = list(range(4))
                    time.sleep(0.5)
                    for p, dd in dds.items():
                        pos = self.disp_sendMsg(dd, p)
                        if pos is not None:
                            poss.remove(pos)
                    for pos in poss:
                        self.disp_sendClear(pos)
                        time.sleep(0.5)
                    self.isFullDD = False
                else:
                    _ = self.disp_sendMsg(dds[path], path)

    def disp_sendClear(self, pos):
        buff = DispData.encodeClear(pos)
        self.socket.sendto(buff, self.addr)
        self.actTs = time.monotonic()

    def disp_sendMsg(self, dd: DispData, path: str) -> int | None:
        pos = None
        if path in self.view:
            pos = self.view[path][ff.pos.jId]
            buff = dd.encode(pos)
            #  TODO remove
            print("Sending disp msg to udp:{}".format(buff))
            self.socket.sendto(buff, self.addr)
            self.actTs = time.monotonic()
        return pos

    async def _sendCmd(self, cmd, delay, times) -> bool:
        """
        Protocol cant handle multiple answers only lost anwsers.
        multiple anwser may get stock and read by next command
        maybe add the command to anwser.
        """
        res = False
        for i in range(0, times):
            print("sending cmd: {}".format(cmd), end="...")
            self.socket.sendto(bytearray(cmd, "ascii"), self.addr)
            print("cmd send: {}".format(cmd))
            ts = time.monotonic()
            self.actTs = ts
            try:
                txt = "waiting for {} seconds for cmd: {}"
                print(txt.format(float(delay), cmd))
                data, _ = await ass.wait_for(self.socket.recvfrom(),
                                             float(delay))
                ts = time.monotonic()-ts
                print("cmd: {} answer: {} at: {:.2f}".format(cmd, data, ts))
                if data == b'\x01':
                    res = True
                    break
                else:
                    break
            except TimeoutError:
                ts = time.monotonic()-ts
                txt = "timed out on cmd: {} try: {} time: {:.2f}"
                print(txt.format(cmd, i, ts))

        return res

    async def turnOff(self) -> bool:
        ok = True
        if not self.turnedOff:
            self.checkConnTask()
            if self.connTask is None:
                self.keepAliveTask.cancel()
                try:
                    await self.keepAliveTask
                    ex = self.keepAliveTask.exception()
                    if ex is not None:
                        print("Error on keep alive task: {}".format(ex))
                except ass.CancelledError:
                    pass
                self.keepAliveTask = None
                ok = await self._sendCmd('C', 2, 3)
                self.socket.close()
            else:
                if not self.connTask.done():
                    self.connTask.cancel()
                    try:
                        await self.connTask
                    except ass.CancelledError:
                        pass
                self.connTask = None
            self.turnedOff = True
        return ok
