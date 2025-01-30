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

    def setTab(self, id: str, newTab: dict):
        disp = None
        if id in self.udpDisps:
            disp = self.udpDisps.get(id)
        else:
            disp = self.bleDisps.get(id)
        oldTab = disp.getTab()
        disp.setTab(newTab)
        return oldTab

    def addBleDisp(self, disps: dict) -> set:
        """
        Construct and add the ids to the displays.
        :return: The added id as a set
        :rtype: set[str]
        """
        for (id, mac) in disps.items():
            d = ble.Display(id, mac, self.status)
            self.bleDisps[id] = d
        return set(disps.keys())

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
