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

    async def display(self, curPaths: set[str], dds: dict[str, DispData]):
        """
        Async! lock! Sends dispdata to display
        First time or after view change all paths is send.
        Second time only one path is send.
        """
        async with self.lock:
            if not self.turnedOff:
                self.checkConnTask()
                if self.connTask is None:
                    try:
                        if self.isFullDD:
                            await self.disp_sendClearAll()
                            await ass.sleep(0.3)  # Cmd is after draw
                            bmsg = bytearray()
                            for p, dd in dds.items():
                                if p in self.view:
                                    pos = self.view[p][ff.pos.jId]
                                    bmsg.extend(dd.encode(pos))
                            await self.disp_sendMsg(bmsg)
                            # TODO Test show this is the loop speed
                            # seems high to me
                            await ass.sleep(0.500)
                            self.isFullDD = False
                        else:
                            bmsg = bytearray()
                            for path in curPaths:
                                if path in self.view:
                                    pos = self.view[path][ff.pos.jId]
                                    bmsg.extend(dds[path].encode(pos))
                            await self.disp_sendMsg(bmsg)

                    except bleak.BleakCharacteristicNotFoundError as ex:
                        txt = "Lost bluetooth connection: {}".format(ex)
                        self.status.setTxt(txt)

    async def disp_sendClearAll(self):
        cmdClear = bytearray('C', "ascii")
        await self.client.write_gatt_char(self.cmdCharId,
                                          cmdClear,
                                          response=True)

    async def disp_sendMsg(self, bmsg: bytearray) -> bytearray:
        if len(bmsg) > 0:
            print("Sending disp msg:{}".format(bmsg))
            await self.client.write_gatt_char(self.dataCharId,
                                              bmsg,
                                              response=False)

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


def pathsInView(view, paths) -> list[str]:
    viewPaths: list[str] = list()
    for path in paths:
        if path in view:
            viewPaths.append(path)
    return viewPaths



