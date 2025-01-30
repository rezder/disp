import asyncio as ass
import bleak
from status import Status
from config import Config
from dispdata import DispData


class Display:

    def __init__(self, id: str, mac: str, status: Status):
        self.id = id
        self.macAddr = mac
        self.status = status
        self.client = bleak.BleakClient(self.macAddr)
        self.connTask = ass.create_task(self.client.connect(),
                                        name="Ble client conn")
        self.on = False
        self.pauseCharId = bleak.uuids.normalize_uuid_32(102)
        self.dataCharId = bleak.uuids.normalize_uuid_32(101)
        self.cmdCharId = bleak.uuids.normalize_uuid_32(103)
        self.tab = Config.default()["tabs"]["None"]

    def __str__(self) -> str:
        txt = "Ble client id: {}, mac: {}".format(self.id, self.macAddr)
        return txt

    def setTab(self, tab: dict):
        self.tab = tab

    def getTab(self) -> dict:
        return self.tab

    def checkConnTask(self):
        if not self.on and self.connTask.done():
            if self.client.is_connected:
                self.on = True
                self.connTask = None
                self.status.setTxt("Display id {} connected".format(self.id))
            else:
                ex = self.connTask.exception()
                if ex is not None:
                    txt = "Display id: {} ble connecting faild\nWith: {}"
                    self.status.setTxt(txt.format(self.id, ex))
                else:
                    txt = "Connecting task done without succes and no error?"
                    self.status.setTxt(txt)

                self.connTask = ass.create_task(self.client.connect())

    async def display(self, dp: DispData, path: str):
        self.checkConnTask()
        if self.on and path in self.tab:
            isPaused = await self.client.read_gatt_char(self.pauseCharId)
            if not isPaused:
                pos = self.tab[path]
                buff = dp.encode(pos)
                print("Sending disp msg:{}".format(buff))  # TODO remove
                await self.client.write_gatt_char(self.dataCharId,
                                                  buff,
                                                  response=False)

    async def turnOff(self):
        """
        **Async** Turns the display off
        """
        self.checkConnTask()
        if self.on:
            if self.client.is_connected:
                cmdOff = bytearray('E', "ascii")
                await self.client.write_gatt_char(self.cmdCharId,
                                                  cmdOff,
                                                  response=True)
                await self.client.disconnect()
            self.on = False
        else:
            if self.connTask is not None:
                if not self.connTask.done():
                    self.connTask.cancel()
                    try:
                        await self.connTask
                    except ass.CancelledError:
                        pass

                self.connTask = None
