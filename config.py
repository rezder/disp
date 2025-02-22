import json
import os
import netifaces


class Config:
    """
    The server configuraion it is json object.
    that is saved in ./dispserver.json
    It does not hold the signal k paths configuration
    That a seperate file.
    """
    def default() -> dict:
        conf = {
            "paths": {
                "environment.depth.belowTransducer": {
                    "minPeriod": 1000,
                    "decimals": 1,
                    "units": 0,
                    "dispUnits": 0,
                    "label": "DBT",
                    "bufSize": 0,
                    "bufFreq": 0,
                    "min": 5.0
                },
                "navigation.speedOverGround": {
                    "minPeriod": 500,
                    "decimals": 1,
                    "units": 10,
                    "dispUnits": 11,
                    "label": "SOG",
                    "bufSize": 4,
                    "bufFreq": 4
                    },
                "navigation.courseOverGroundTrue": {
                    "minPeriod": 500,
                    "decimals": 0,
                    "units": 20,
                    "dispUnits": 21,
                    "label": "COG",
                    "bufSize": 4,
                    "bufFreq": 4
                    },
                "navigation.speedThroughWater": {
                    "minPeriod": 2000,
                    "decimals": 1,
                    "units": 10,
                    "dispUnits": 11,
                    "label": "STW",
                    "bufSize": 0,
                    "bufFreq": 0
                    },
                "navigation.courseRhumbline.crossTrackError": {
                    "minPeriod": 4000,
                    "decimals": 0,
                    "units": 0,
                    "dispUnits": 0,
                    "label": "XTE",
                    "bufSize": 0,
                    "bufFreq": 0
                    },
                "navigation.courseRhumbline.nextPoint.bearingTrue": {
                    "minPeriod": 500,
                    "decimals": 0,
                    "units": 20,
                    "dispUnits": 21,
                    "label": "BEA",
                    "bufSize": 4,
                    "bufFreq": 4
                    },
                "navigation.courseRhumbline.nextPoint.distance": {
                    "minPeriod": 4000,
                    "decimals": 0,
                    "units": 0,
                    "dispUnits": 0,
                    "label": "DIS",
                    "bufSize": 0,
                    "bufFreq": 0,
                    "bigValue": 999,
                    "bigDispUnit": 1,
                    "bigDecimals": 1
                    }
                },
            "tabs": {
                "None": {},
                "Default": {
                    "environment.depth.belowTransducer": 0,
                    "navigation.speedOverGround": 1,
                    "navigation.courseOverGroundTrue": 2,
                    "navigation.speedThroughWater": 3},
                "Route1": {
                    "environment.depth.belowTransducer": 0,
                    "navigation.courseOverGroundTrue": 1,
                    "navigation.courseRhumbline.crossTrackError": 2,
                    "navigation.courseRhumbline.nextPoint.bearingTrue": 3},
                "Route2": {
                    "environment.depth.belowTransducer": 0,
                    "navigation.courseRhumbline.crossTrackError": 1,
                    "navigation.courseRhumbline.nextPoint.bearingTrue": 2,
                    "navigation.courseRhumbline.nextPoint.distance": 3}
            },
            "curTabs": {},
            "macs": {},
            "broadcastPort": 9090,
            "interface": "wlp2s0",
            "disableSubServer": False
        }
        return conf

    def load(fileName) -> dict:
        if not os.path.isfile(fileName):
            conf = Config.default()
            with open(fileName, "w") as f:
                f.write(json.dumps(conf))
        with open(fileName, "r") as f:
            conf = json.load(f)
        return conf

    def __init__(self, isDefault=False):
        self.fileName = "./dispserver.json"
        if isDefault:
            self.conf = Config.default()
        else:
            self.conf = Config.load(self.fileName)
        self.defaultTab = "None"

    def getSubPort(self) -> int:
        return self.conf["broadcastPort"]

        return self.defaultTab

    def isDefined(self, id) -> bool:
        return id in self.conf["curTabs"]

    def addDisp(self, id) -> bool:
        upd = False
        if id not in self.conf["curTabs"]:
            self.conf["curTabs"][id] = self.defaultTab
            upd = True
        return upd

    def addMac(self, id, mac):
        mo = dict()
        mo["addr"] = mac
        mo["isDisable"] = False
        self.conf["macs"][id] = mo

    def getMacs(self) -> dict:
        return dict(self.conf["macs"])

    def setCurTabId(self, tabId, id):
        self.conf["curTabs"][id] = tabId

    def setBleDispDisable(self, id: str, isDisable: bool):
        self.conf["macs"][id]["isDisable"] = isDisable

    def getCurTabId(self, id) -> str:
        tabId = self.conf["curTabs"][id]
        return tabId

    def getPathsJson(self) -> dict:
        """
        :returns: All the paths json object
        """
        return dict(self.conf["paths"])

    def getTabsJson(self) -> dict:
        return self.conf["tabs"]

    def getCurTabPaths(self, id) -> dict:
        ll = dict(self.conf["tabs"][self.conf["curTabs"][id]])
        return ll

    def getCurTabs(self):
        return dict(self.conf["curTabs"])

    def getTabPaths(self, tabId) -> dict:
        return dict(self.conf["tabs"][tabId])

    def getTabNames(self) -> list:
        return list(self.conf["tabs"].keys())

    def getSubUdpServerIsEnable(self) -> bool:
        return not self.conf["disableSubServer"]

    def getPathsRefs(self, path: str) -> list[str]:
        tabs = set()
        for id, tab in self.conf["tabs"].items():
            for tabPath, pos in tab.items():
                if path == tabPath:
                    tabs.add(id)
        return tabs

    def setPath(self, pathId: str, pathJson: dict):
        self.conf["paths"][pathId] = pathJson

    def deletePath(self, pathId: str):
        del self.conf["paths"][pathId]

    def getBroadcastIp(self) -> str:
        b = None
        try:
            jsonObj = netifaces.ifaddresses(self.conf["interface"])
            b = jsonObj[netifaces.AF_INET][0]["broadcast"]
        except (KeyError, ValueError) as ex:
            txt = "Fail to find broadcast ip for interface: {} error: {}"
            print(txt.format(self.conf["interface"], ex))

        return b

    def save(self):
        with open(self.fileName, "w") as f:
            f.write(json.dumps(self.conf, indent=2))
