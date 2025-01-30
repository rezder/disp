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
            "interface": "wlp2s0"
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

    def __init__(self):
        self.fileName = "./dispserver.json"
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
        self.conf["macs"][id] = mac

    def getMacs(self) -> dict:
        return dict(self.conf["macs"])

    def setCurTabId(self, tabId, id):
        self.conf["curTabs"][id] = tabId

    def getCurTabId(self, id) -> str:
        tabId = self.conf["curTabs"][id]
        return tabId

    def getCurTabPaths(self, id) -> dict:
        ll = dict(self.conf["tabs"][self.conf["curTabs"][id]])
        return ll

    def getCurTabs(self):
        return dict(self.conf["curTabs"])

    def getTabPaths(self, tabId) -> dict:
        return dict(self.conf["tabs"][tabId])

    def getTabNames(self) -> list:
        return list(self.conf["tabs"].keys())

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
