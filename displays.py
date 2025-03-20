import udp
import ble
from status import Status
from dispdata import DispData


class Displays:
    """
    Displays holds the displays that is on or
    soon will be on(the may be connecting)
    There is two types udp and ble.
    The differ only in add methods and
    display methods as one is async.
    both types could be more general.
    """

    def __init__(self, status: Status):
        self.udpDisps = dict()
        self.bleDisps = dict()
        self.status = status

    def isIn(self, id) -> bool:
        res = id in self.udpDisps or id in self.bleDisps
        return res

    def setTab(self, id: str, newTab: dict) -> dict:
        disp = self.getDisp(id)
        oldTab = disp.getTab()
        disp.setTab(newTab)
        return oldTab

    def getDisp(self, id):
        """
        Returns a display ble or udp if the
        display id match a display else None
        :param id: The id of display
        :return: udpDisplay/bleDisplay/None
        """
        disp = None
        if id in self.udpDisps:
            disp = self.udpDisps.get(id)
        else:
            disp = self.bleDisps.get(id)
        return disp

    def getDispTab(self, id):
        disp = self.getDisp(id)
        tab = disp.getTab()
        return tab

    def addBleDisps(self, disps: dict) -> set:
        """
        Construct and add the ids to the displays.
        :return: The added id as a set
        :rtype: set[str]
        """
        ids = set()
        # I think only one Ble connection can be created at the time
        # as BleakClient does a scann before it connect.
        # If the first display fails to connect it blocks
        # for everybody else. bleak.exc.BleakDBusError
        # with the org.bluez.Error.InProgress in the
        # ex.dbus_error field.
        # I would expect that when the connection fails
        # to connect after 10 seconds
        # the other connection jumps the queue but that
        # does not happens. Add a delay to the connect
        # task it seems to work
        for (id, macObj) in disps.items():
            if not macObj["isDisable"]:
                self.addBleDisp(id, macObj)
                ids.add(id)
        return ids

    def addBleDisp(self, id, macObj):
        """
        Construct and add a ble displays.
        """
        d = ble.Display(id, macObj["addr"], self.status)
        self.bleDisps[id] = d

    async def removeBleDisp(self, id):
        d = self.bleDisps[id]
        del self.bleDisps[id]
        await d.turnOff()

    def add(self, id, ip, port) -> bool:
        isNew = True
        if id in self.udpDisps:
            isNew = False
            self.udpDisps[id].setAddr(ip, port)
        else:
            isNew = True
            d = udp.Display(id, ip, port, self.status)
            self.udpDisps[id] = d
        return isNew

    async def display(self, dp: DispData, path: str):
        for ud in self.udpDisps.values():
            ud.display(dp, path)
        for dd in self.bleDisps.values():
            await dd.display(dp, path)

    async def close(self) -> bool:
        ok = True
        for ud in self.udpDisps.values():
            dok = await ud.turnOff()
            ok = ok and dok
        for dd in self.bleDisps.values():
            await dd.turnOff()
        return ok

    def __str__(self) -> str:
        txt = "Udp displays {}\nBle displays{}"
        res = txt.format(self.udpDisps, self.bleDisps)
        return res
