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
        return id in self.conf[fd.displays.jId]

    def dispAdd(self, id) -> bool:  # TODO return defaultTab
        upd = False
        if id not in self.conf[fd.displays.jId]:
            self.conf[fd.displays.jId][id][ff.view.jId] = self.defaultTab
            upd = True
        return upd

    def dispUpdMac(self, id, mac) -> bool:
        upd = False
        mo = dict()
        mo[ff.addr.jId] = mac
        mo[ff.disable.jId] = False
        if id not in self.conf[fd.macs.jId]:
            self.conf[fd.macs.jId][id] = mo
            upd = True
        else:
            if self.conf[fd.macs.jId][id][ff.addr.jId] != mac:
                self.conf[fd.macs.jId][id] = mo
                upd = True
        return upd

    def dispGetBles(self) -> dict:
        return dict(self.conf[fd.macs.jId])

    def dispGetBle(self, dispId) -> dict:
        return self.conf[fd.macs.jId][dispId]

    def dispSetTabId(self, dispId, tabId):
        self.conf[fd.displays.jId][dispId][ff.view.jId] = tabId

    def dispGetTab(self, dispId) -> tuple[str, dict]:
        tabId = self.conf[fd.displays.jId][dispId][ff.view.jId]
        tab = dict(self.conf[fd.tabs.jId][tabId][fd.poss.jId])
        return (tabId, tab)

    def dispGet(self):
        viewids = dict()
        for k, d in self.conf[fd.displays.jId].items():
            viewids[k] = d[ff.view.jId]
        return viewids

    def dispSetBleDisable(self, id: str, isDisable: bool):
        self.conf[fd.macs.jId][id][ff.disable.jId] = isDisable

    #  ################ Tabs ###########

    def tabsGet(self) -> dict:
        return self.conf[fd.tabs.jId]

    def tabsGetTab(self, tabId) -> dict:
        return dict(self.conf[fd.tabs.jId][tabId][fd.poss.jId])

    def tabsGetIds(self) -> list:
        return list(self.conf[fd.tabs.jId].keys())

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
        for id, tab in self.conf[fd.tabs.jId].items():
            for tabPath in tab[fd.poss.jId].keys():
                if path == tabPath:
                    tabs.add(id)
        if path in self.conf[fd.bigs.jId]:
            inBigs = True

        if path in self.conf[fd.alarms.jId]:
            inAlarms = True
        return tabs, inBigs, inAlarms

    def pathsGet(self) -> tuple[dict, dict, dict]:
        """
        :returns: All the paths json objects
        - paths
        - alarms
        - bigs
        """
        return self.conf[fd.paths.jId], self.conf[fd.alarms.jId], self.conf[fd.bigs.jId]

    def pathsSetPath(self, pathId: str, pathJson: dict):
        self.conf[fd.paths.jId][pathId] = pathJson

    def pathsDeletePath(self, pathId: str):
        del self.conf[fd.paths.jId][pathId]

    def pathsGetAlarm(self, pathId) -> dict | None:
        res = None
        if pathId in self.conf[fd.alarms.jId].keys():
            res = self.conf[fd.alarms.jId][pathId]
        return res

    def pathsGetAlarms(self) -> dict:
        return self.conf[fd.alarms.jId]

    def pathsGetBigUnit(self, pathId) -> dict | None:
        res = None
        if pathId in self.conf[fd.bigs.jId].keys():
            res = self.conf[fd.bigs.jId][pathId]
        return res

    def pathsGetBigUnits(self) -> dict:
        return self.conf[fd.bigs.jId]

    # ############### Misc ##################

    def getBroadcastIp(self) -> str:
        b = None
        try:
            jsonObj = netifaces.ifaddresses(self.conf[ff.interface.jId])
            b = jsonObj[netifaces.AF_INET][0]["broadcast"]
        except (KeyError, ValueError) as ex:
            txt = "Fail to find broadcast ip for interface: {} error: {}"
            print(txt.format(self.conf[ff.interface.jId], ex))

        return b

    def getSubPort(self) -> int:
        return self.conf[ff.broadCP.jId]

    def getSubUdpServerIsEnable(self) -> bool:
        return not self.conf[ff.dissub.jId]

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


def valPaths(path, ptr, paths) -> list[ErrPtr]:
    errs = list()
    if path[ff.bufFreq.jId] > path[ff.bufSize.jId]:
        v = path[ff.bufFreq.jId]
        txt = "{}: {} should not be bigger than {}"
        err = ErrPtr(ptr+ff.bufFreq, v, txt,
                     ref=ptr+ff.bufSize)
        errs.append(err)
    return errs


def valAlarms(alarm, ptr, alarms) -> list[ErrPtr]:
    errs = list()
    if len(alarm) == 0:
        txt = "{} has no alarms"
        err = ErrPtr(ptr, None, txt, isVal=False)
        errs.append(err)
    return errs


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
    cf.addFld(ff.interface, empty.noEmpty)
    cf.addFld(ff.dissub, empty.ok)
    defs[cf.idFld.jId] = cf

    pf = JsoDef(fd.paths, valPaths)
    pf.addFld(ff.pathId, empty.noEmpty, isKey=True)
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
    bf.addFld(ff.pathId, empty.noEmpty, isKey=True, refPtr=pathsPtr)
    bf.addFld(ff.limit, empty.noZero)
    bf.addFld(ff.dpUnit, empty.ok)
    bf.addFld(ff.dec, empty.ok)
    defs[bf.idFld.jId] = bf

    af = JsoDef(fd.alarms, valAlarms)
    af.addFld(ff.pathId, empty.noEmpty, isKey=True, refPtr=pathsPtr)
    af.addFld(ff.min, empty.noNaN, isMan=False)
    af.addFld(ff.max, empty.noNaN, isMan=False)
    defs[af.idFld.jId] = af

    vf = JsoDef(fd.tabs)
    vf.addFld(ff.viewId, empty.noEmpty, isKey=True)
    vf.addFld(fd.poss, empty.ok)
    defs[vf.idFld.jId] = vf
    viewsPtr = Ptr([fd.conf, fd.tabs])

    pf = JsoDef(fd.poss)
    pf.addFld(ff.pathId, empty.noEmpty, isKey=True, refPtr=pathsPtr)
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
