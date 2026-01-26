import asyncio as ass
import bleak

from status import Status
from dispdata import DispData
from flds import flds as ff


class Display:

    def __init__(self, id: str, mac: str, status: Status):
        self.id = id
        self.macAddr = mac
        self.status = status
        self.client = bleak.BleakClient(self.macAddr)  # Tries for 10 seconds
        self.connTask = ass.create_task(self.client.connect(),
                                        name="Ble client conn")
        self.pauseCharId = bleak.uuids.normalize_uuid_32(102)
        self.dataCharId = bleak.uuids.normalize_uuid_32(101)
        self.cmdCharId = bleak.uuids.normalize_uuid_32(103)
        self.isFullDD = False
        self.view = {}
        self.turnedOff = False
        self.lock = ass.Lock()

    def __str__(self) -> str:
        txt = "Ble client id: {}, mac: {}".format(self.id, self.macAddr)
        return txt

    async def setView(self, view: dict):
        """
        Async lock set View
        """
        async with self.lock:
            self.view = view
            self.isFullDD = True

    def getView(self) -> dict:
        return self.view

    async def delayConnect(self):
        await ass.sleep(1)
        await self.client.connect()

    def checkConnTask(self):
        if self.connTask is not None:
            if self.connTask.done():
                if self.client.is_connected:
                    self.connTask = None
                    txt = "Display id {} connected"
                    self.status.setTxt(txt.format(self.id))
                    self.isFullDD = True
                else:
                    ex = self.connTask.exception()
                    if ex is not None:
                        txt = "Display id: {} ble connecting faild\nWith: {}"
                        self.status.setTxt(txt.format(self.id, ex))
                    else:
                        txt = "Connect task done without succes and no error?"
                        self.status.setTxt(txt)

                    self.connTask = ass.create_task(self.delayConnect())
        else:
            if not self.client.is_connected:
                self.connTask = ass.create_task(self.delayConnect())

    async def display(self, path: str, dds: dict[str, DispData]):
        """
        Async! lock! Sends dispdata to display
        First time or after view change all paths is send.
        Second time only one path is send.
        """
        async with self.lock:
            if not self.turnedOff and (path in self.view or self.isFullDD):
                self.checkConnTask()
                if self.connTask is None:
                    try:
                        buff = await self.client.read_gatt_char(self.pauseCharId)
                        isPaused = bool(int.from_bytes(buff))
                        if not isPaused:
                            if self.isFullDD:
                                poss: list[int] = list(range(4))
                                for p, dd in dds.items():
                                    pos = await self.disp_sendMsg(dd, p)
                                    await ass.sleep(0.100)
                                    if pos is not None:
                                        poss.remove(pos)
                                if len(poss) != 0:
                                    for pos in poss:
                                        await self.disp_sendClear(pos)
                                        await ass.sleep(0.100)
                                self.isFullDD = False
                            else:
                                await self.disp_sendMsg(dds[path], path)

                    except bleak.BleakCharacteristicNotFoundError as ex:
                        txt = "Lost bluetooth connection: {}".format(ex)
                        self.status.setTxt(txt)

    async def disp_sendClear(self, pos):
        buff = DispData.encodeClear(pos)
        # print("Sending disp msg:{}".format(buff))
        await self.client.write_gatt_char(self.dataCharId,
                                          buff,
                                          response=False)

    async def disp_sendMsg(self, dd: DispData, path: str) -> int | None:
        pos = None
        if path in self.view:
            pos = self.view[path][ff.pos.jId]
            buff = dd.encode(pos)
            #  TODO remove
            print("Sending disp msg:{}".format(buff))
            await self.client.write_gatt_char(self.dataCharId,
                                              buff,
                                              response=False)
        return pos

    async def turnOff(self):
        """
        **Async** Turns the display off
        """
        if not self.turnedOff:
            self.checkConnTask()
            if self.connTask is None:
                if self.client.is_connected:
                    cmdOff = bytearray('E', "ascii")
                    await self.client.write_gatt_char(self.cmdCharId,
                                                      cmdOff,
                                                      response=True)
                    await self.client.disconnect()
            else:
                if not self.connTask.done():
                    self.connTask.cancel()
                    try:
                        await self.connTask
                    except ass.CancelledError:
                        pass

                self.connTask = None
            self.turnedOff = True
