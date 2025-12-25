import json
import os
import netifaces
from flds import flds as ff
from flds import fldsDict as fd
import jsonvalidate as val
from jsonptr import Ptr, ErrPtr
from flds import flds as ff
from flds import fldsDict as fd


class Config:
    """
    The server configuraion it is json object.
    that is saved in ./dispserver.json
    It does not hold the signal k paths configuration
    That a seperate file.
    """
    def default() -> dict:
        conf = {"conf": {
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
                "Default": {"poss": {
                    "environment.depth.belowTransducer": {"pos": 0},
                    "navigation.speedOverGround": {"pos": 1},
                    "navigation.courseOverGroundTrue": {"pos": 2},
                    "navigation.speedThroughWater": {"pos": 3}}},
                "Route1": {"poss": {
                    "environment.depth.belowTransducer": {"pos": 0},
                    "navigation.courseOverGroundTrue": {"pos": 1},
                    "navigation.courseRhumbline.crossTrackError": {"pos": 2},
                    "navigation.courseRhumbline.nextPoint.bearingTrue": {"pos": 3}}},
                "Route2": {"poss": {
                    "environment.depth.belowTransducer": {"pos": 0},
                    "navigation.courseRhumbline.crossTrackError": {"pos": 1},
                    "navigation.courseRhumbline.nextPoint.bearingTrue": {"pos": 2},
                    "navigation.courseRhumbline.nextPoint.distance": {"pos": 3}}}
            },
            "displays": {},
            "macs": {},
            "broadcastPort": 9090,
            "interface": "wlp2s0",
            "disableSubServer": False
        }}
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
            self.conff = Config.default()
            self.conf = self.conff[fd.conf.jId]
        else:
            self.conff = Config.load(self.fileName)
            self.conf = self.conff[fd.conf.jId]
        self.defaultTab = "None"

    #  ##### Displays #################

    def dispIs(self, id) -> bool:
        return id in self.conf["displays"]

    def dispAdd(self, id) -> bool:  # TODO return defaultTab
        upd = False
        if id not in self.conf["displays"]:
            self.conf["displays"][id]["view"] = self.defaultTab
            upd = True
        return upd

    def dispUpdMac(self, id, mac) -> bool:
        upd = False
        mo = dict()
        mo["addr"] = mac
        mo["isDisable"] = False
        if id not in self.conf["macs"]:
            self.conf["macs"][id] = mo
            upd = True
        else:
            if self.conf["macs"][id]["addr"] != mac:
                self.conf["macs"][id] = mo
                upd = True
        return upd

    def dispGetBles(self) -> dict:
        return dict(self.conf["macs"])

    def dispGetBle(self, dispId) -> dict:
        return self.conf["macs"][dispId]

    def dispSetTabId(self, dispId, tabId):
        self.conf["displays"][dispId]["view"] = tabId

    def dispGetTab(self, dispId) -> tuple[str, dict]:
        tabId = self.conf["displays"][dispId]["view"]
        tab = dict(self.conf["tabs"][tabId]["poss"])
        return (tabId, tab)

    def dispGet(self):
        viewids = dict()
        for k, d in self.conf["displays"].items():
            viewids[k] = d["view"]
        return viewids

    def dispSetBleDisable(self, id: str, isDisable: bool):
        self.conf["macs"][id]["isDisable"] = isDisable

    #  ################ Tabs ###########

    def tabsGet(self) -> dict:
        return self.conf["tabs"]

    def tabsGetTab(self, tabId) -> dict:
        return dict(self.conf["tabs"][tabId]["poss"])

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
            for tabPath in tab["poss"].keys():
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
            f.write(json.dumps(self.conff, indent=2))

    def validate(self) -> str:
        errList: list[ErrPtr] = list()
        # =============  Conf =====================
        flds = [fd.paths, fd.alarms, fd.bigs, fd.tabs,
                fd.displays, fd.macs, ff.broadCP,
                ff.intface, ff.dissub, ff.limit]
        optFlds = []
        confPtr = Ptr([fd.conf], [])
        el = val.missExtFlds(self.conf, confPtr, flds, optFlds)
        errList.extend(el)

        # =============  Paths =====================
        joPaths = self.conf[fd.paths.jId]
        # keyFld = ff.path
        # dictFld = fd.paths
        flds = [ff.minPer, ff.dec, ff.skUnit, ff.dpUnit,
                ff.label, ff.bufSize, ff.bufFreq, ff.limit]
        optFlds = []
        pathsPtr = Ptr([fd.paths, ff.path], [])
        el = val.missExtFlds(joPaths, pathsPtr, flds, optFlds)
        errList.extend(el)

        # ============= Bigs =====================
        joBigs = self.conf[fd.bigs.jId]
        # keyFld = ff.path
        # dictFld = fd.bigs
        flds = [ff.limit, ff.dpUnit, ff.dec]
        optFlds = []
        bigsPtr = Ptr([fd.bigs, ff.path], [])
        el = val.missExtFlds(joBigs, bigsPtr, flds, optFlds)
        errList.extend(el)
        pathsPtr = Ptr([fd.paths], [])  # no keyfld on dist ptr ??
        el = val.refCheck(joBigs, bigsPtr, pathsPtr, joPaths)
        errList.extend(el)

        # ============= Alarms =====================
        joAlarms = self.conf[fd.alarms.jId]
        #  keyFld = ff.path
        #  dictFld = fd.alarms
        flds = []
        optFlds = [ff.max, ff.min]

        alarmsPtr = Ptr([fd.alarms, ff.path], [])
        el = val.missExtFlds(joAlarms, alarmsPtr, flds, optFlds)
        errList.extend(el)

        pathsPtr = Ptr([fd.paths], [])  # no keyfld on dist ptr ??
        el = val.refCheck(joAlarms, alarmsPtr, pathsPtr, joBigs)
        errList.extend(el)  # should be joPaths just for error TODO

        # =============  End  =====================
        errTxt = ""
        errNo = len(errList)
        if errNo != 0:
            errTxt = "{} contain {} errors!".format(fd.conf.header, errNo)
            for e in errList:
                errTxt = errTxt + "\n" + e.toStr()

        return errTxt
