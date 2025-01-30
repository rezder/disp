import time
from asyncudp import create_socket as udpSocket
import asyncio as ass
from config import Config
from status import Status
from dispdata import DispData


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
        self.on = False
        self.id = id
        self.status = status
        self.tab = Config.default()["tabs"]["None"]
        self.keepAliveTask = ass.create_task(self.keepAlive(),
                                             name="Keep Alive")
        self.keepAliveTime = 10.0
        self.actTs = time.monotonic()
        self.connTask = ass.create_task(udpSocket(remote_addr=self.addr),
                                        name="Udp connection")

    def __str__(self) -> str:
        txt = "Display: id:{}, on: {}, addr: {}"
        res = txt.format(self.id, self.on, self.addr)
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
                if self.on:
                    self.socket.sendto(bytearray(cmd, "ascii"), self.addr)
                    sleep = self.keepAliveTime
                    self.actTs = ts
                else:
                    sleep = self.keepAliveTime/2

    def setAddr(self, ip, port):
        self.addr = (ip, port)

    def setTab(self, tab: dict):
        self.tab = tab

    def getTab(self) -> dict:
        return self.tab

    def checkConnTask(self):
        if not self.on and self.connTask.done():
            ex = self.connTask.exception()
            if ex is None:
                self.socket = self.connTask.result()
                self.on = True
                self.connTask = None
            else:
                txt = "Display id: {} udp connecting faild\nWith: {}"
                self.status.setTxt(txt.format(self.id, ex))
                self.connTask = ass.create_task(self.client.connect())

    def display(self, dp: DispData, path: str):
        self.checkConnTask()
        if self.on:
            if path in self.tab:
                pos = self.tab[path]
                buff = dp.encode(pos)
                print("Sending disp msg:{}".format(buff))  # TODO remove
                self.socket.sendto(buff, self.addr)
                self.actTs = time.monotonic()

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
        self.checkConnTask()
        if self.on:
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
            if ok:
                self.on = False
            self.socket.close()
        else:
            if self.connTask is not None:
                if not self.connTask.done():
                    self.connTask.cancel()
                    try:
                        await self.connTask
                    except ass.CancelledError:
                        pass

                self.connTask = None
        return ok
