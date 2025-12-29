import json
import os
import netifaces
from flds import flds as ff
from flds import fldsDict as fd
from jsonptr import Ptr, ErrPtr
from jsoflds import JsoDef, walkObj
import empty


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
                "None": {"poss": {}},
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
        self.jsoDefs = createJsonDef()

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
        ptrs = walkObj(self.conff, self.jsoDefs)
        for ptr in ptrs:
            errs = self.jsoDefs[ptr.lastFld.jId].validate(self.conff, ptr)
            errList.extend(errs)
        errTxt = ""
        errNo = len(errList)
        if errNo != 0:
            errTxt = "{} contain {} errors!".format(fd.conf.header, errNo)
            for e in errList:
                errTxt = errTxt + "\n" + e.toStr()

        return errTxt


def createJsonDef() -> dict[str, JsoDef]:
    defs: dict[str, JsoDef] = dict()
    cf = JsoDef(fd.conf)
    cf.addFld(fd.paths, empty.noEmpty)
    cf.addFld(fd.alarms, empty.noEmpty)
    cf.addFld(fd.bigs, empty.noEmpty)
    cf.addFld(fd.tabs, empty.noEmpty)
    cf.addFld(fd.displays, empty.noEmpty)
    cf.addFld(fd.macs, empty.noEmpty)
    cf.addFld(ff.broadCP, empty.noZero)
    cf.addFld(ff.intface, empty.noEmpty)
    cf.addFld(ff.dissub, empty.ok)
    defs[cf.idFld.jId] = cf

    pf = JsoDef(fd.paths)
    pf.addFld(ff.path, empty.noEmpty, isKey=True)
    pf.addFld(ff.minPer, empty.noZero)
    pf.addFld(ff.dec, empty.ok)
    pf.addFld(ff.skUnit, empty.ok)
    pf.addFld(ff.dpUnit, empty.ok)
    pf.addFld(ff.label, empty.noEmpty)
    pf.addFld(ff.bufSize, empty.ok)
    pf.addFld(ff.bufFreq, empty.ok)
    defs[pf.idFld.jId] = pf
    pathsPtr = Ptr([fd.conf, fd.paths])

    bf = JsoDef(fd.bigs)
    bf.addFld(ff.path, empty.noEmpty, isKey=True, refPtr=pathsPtr)
    bf.addFld(ff.limit, empty.noZero)
    bf.addFld(ff.dpUnit, empty.ok)
    bf.addFld(ff.dec, empty.ok)
    defs[bf.idFld.jId] = bf

    af = JsoDef(fd.alarms)
    af.addFld(ff.path, empty.noEmpty, isKey=True, refPtr=pathsPtr)
    af.addFld(ff.min, empty.noNaN, isMan=False)
    af.addFld(ff.max, empty.noNaN, isMan=False)
    defs[af.idFld.jId] = af

    vf = JsoDef(fd.tabs)
    vf.addFld(ff.viewId, empty.noEmpty, isKey=True)
    vf.addFld(fd.poss, empty.ok)
    defs[vf.idFld.jId] = vf
    viewsPtr = Ptr([fd.conf, fd.tabs])

    pf = JsoDef(fd.poss)
    pf.addFld(ff.path, empty.noEmpty, isKey=True, refPtr=pathsPtr)
    pf.addFld(ff.pos, empty.ok)
    defs[pf.idFld.jId] = pf

    disf = JsoDef(fd.displays)
    disf.addFld(ff.dispId, empty.noEmpty, isKey=True)
    disf.addFld(ff.view, empty.noEmpty, refPtr=viewsPtr)
    defs[disf.idFld.jId] = disf
    dispPtr = Ptr([fd.conf, fd.displays])

    mf = JsoDef(fd.macs)
    mf.addFld(ff.dispId, empty.noEmpty, isKey=True, refPtr=dispPtr)
    mf.addFld(ff.addr, empty.noEmpty)
    mf.addFld(ff.disable, empty.ok)
    defs[mf.idFld.jId] = mf
    return defs
