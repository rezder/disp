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
                    "bufFreq": 0
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
                    "bufFreq": 0
                    }
                },
            "bigs": {
                "navigation.courseRhumbline.nextPoint.distance": {
                    "limit": 999,
                    "dispUnits": 1,
                    "decimals": 1
                }
            },
            "alarms": {
                "environment.depth.belowTransducer": {
                    "min": 5.0
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
            "displays": {},
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
                f.write(json.dumps(conf, indent=2))
        with open(fileName, "r") as f:
            conf = json.load(f)
        return conf

    def __init__(self, isDefault=False):
        self.fileName = "./data/dispserver.json"
        if isDefault:
            self.conf = Config.default()
        else:
            self.conf = Config.load(self.fileName)
        self.defaultTab = "None"

    #  ##### Displays #################

    def dispIs(self, id) -> bool:
        return id in self.conf["displays"]

    def dispAdd(self, id) -> bool:
        upd = False
        if id not in self.conf["displays"]:
            self.conf["displays"][id] = self.defaultTab
            upd = True
        return upd

    def dispUpdMac(self, id, mac):
        mo = dict()
        mo["addr"] = mac
        mo["isDisable"] = False
        self.conf["macs"][id] = mo

    def dispGetBles(self) -> dict:
        return dict(self.conf["macs"])

    def dispGetBle(self, dispId) -> dict:
        return self.conf["macs"][dispId]

    def dispSetTabId(self, dispId, tabId):
        self.conf["displays"][dispId] = tabId

    def dispGetTab(self, dispId) -> tuple[str, dict]:
        tabId = self.conf["displays"][dispId]
        tab = dict(self.conf["tabs"][tabId])
        return (tabId, tab)

    def dispGet(self):
        return dict(self.conf["displays"])

    def dispSetBleDisable(self, id: str, isDisable: bool):
        self.conf["macs"][id]["isDisable"] = isDisable

    #  ################ Tabs ###########

    def tabsGet(self) -> dict:
        return self.conf["tabs"]

    def tabsGetTab(self, tabId) -> dict:
        return dict(self.conf["tabs"][tabId])

    def tabsGetIds(self) -> list:
        return list(self.conf["tabs"].keys())

    #  ############## Paths #################

    def pathsGetRefs(self, path: str) -> tuple[list[str], bool, bool]:
        """
        return reference to path.
        :returns:
        - tabs     - reference on displays tab
        - inBigs   - if it have a big unit
        - inAlarms = if it have an alarm
        """
        tabs = set()
        inBigs = False
        inAlarms = False
        for id, tab in self.conf["tabs"].items():
            for tabPath, pos in tab.items():
                if path == tabPath:
                    tabs.add(id)
        if path in self.conf["bigs"]:
            inBigs = True

        if path in self.conf["alarms"]:
            inAlarms = True
        return tabs, inBigs, inAlarms

    def pathsGet(self) -> tuple[dict, dict, dict]:
        """
        :returns: All the paths json objects
        - paths
        - alarms
        - bigs
        """
        return self.conf["paths"], self.conf["alarms"], self.conf["bigs"]

    def pathsSetPath(self, pathId: str, pathJson: dict):
        self.conf["paths"][pathId] = pathJson

    def pathsDeletePath(self, pathId: str):
        del self.conf["paths"][pathId]

    def pathsGetAlarm(self, pathId) -> dict | None:
        res = None
        if pathId in self.conf["alarms"].keys():
            res = self.conf["alarms"][pathId]
        return res

    def pathsGetAlarms(self) -> dict:
        return self.conf["alarms"]

    def pathsGetBigUnit(self, pathId) -> dict | None:
        res = None
        if pathId in self.conf["bigs"].keys():
            res = self.conf["bigs"][pathId]
        return res

    def pathsGetBigUnits(self) -> dict:
        return self.conf["bigs"]

    # ############### Misc ##################

    def getBroadcastIp(self) -> str:
        b = None
        try:
            jsonObj = netifaces.ifaddresses(self.conf["interface"])
            b = jsonObj[netifaces.AF_INET][0]["broadcast"]
        except (KeyError, ValueError) as ex:
            txt = "Fail to find broadcast ip for interface: {} error: {}"
            print(txt.format(self.conf["interface"], ex))

        return b

    def getSubPort(self) -> int:
        return self.conf["broadcastPort"]

    def getSubUdpServerIsEnable(self) -> bool:
        return not self.conf["disableSubServer"]

    def save(self):
        with open(self.fileName, "w") as f:
            f.write(json.dumps(self.conf, indent=2))
