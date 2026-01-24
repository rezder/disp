import json
import os
import netifaces
import copy

from flds import flds as ff
from flds import fldsDict as fd
from jsonptr import Ptr, ErrPtr
from jsoflds import JsoDef, walkObj
import empty
import units


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
                    },
                "navigation.courseRhumbline.nextPoint.ID": {
                    "minPeriod": 4000,
                    "decimals": 0,
                    "label": "ID",
                    "units": 99,
                    "dispUnits": 99,
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
            "views": {
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
        self.oldConff = copy.deepcopy(self.conff)
        self.jsoDefs = createJsonDef()
        errTxt, errList = self.validate()
        if len(errList) != 0:
            raise Exception("Config load error: {}".format(errTxt))
        self.defaultView = "None"
        self.settFlds = [ff.broadCP, ff.interface, ff.dissub]

    def rollBack(self):
        self.conff = self.oldConff
        self.conf = self.conff[fd.conf.jId]
        self.oldConff = copy.deepcopy(self.conff)
    #  ##### Displays #################

    def dispIs(self, id) -> bool:
        return id in self.conf[fd.displays.jId]

    def dispIsBle(self, id) -> bool:
        return id in self.conf[fd.macs.jId]

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
        return copy.deepcopy(self.conf[fd.macs.jId])

    def dispGetView(self, dispId) -> tuple[str, dict]:
        viewId = self.conf[fd.displays.jId][dispId][ff.view.jId]
        view = self.conf[fd.views.jId][viewId][fd.poss.jId]
        return (viewId, view)

    def dispsGet(self) -> tuple[dict, dict, dict, dict]:
        """
        :returns:
        - displays
        - macs
        - views
        - paths
        """
        displays = copy.deepcopy(self.conf[fd.displays.jId])
        macs = self.dispGetBles()
        views = copy.deepcopy(self.conf[fd.views.jId])
        paths = self.pathsGet()[0]

        return displays, macs, views, paths

    def dispsSet(self, disps, macs, views):
        self.conf[fd.displays.jId] = copy.deepcopy(disps)
        self.conf[fd.macs.jId] = copy.deepcopy(macs)
        self.conf[fd.views.jId] = copy.deepcopy(views)

    def dispSetBleDisable(self, id: str, isDisable: bool):
        self.conf[fd.macs.jId][id][ff.disable.jId] = isDisable

    #  ################ Views ###########

    def viewsGetView(self, viewId) -> dict:
        return self.conf[fd.views.jId][viewId][fd.poss.jId]

    def viewsGetIds(self) -> list:
        return list(self.conf[fd.views.jId].keys())

    #  ############## Paths #################

    def pathsGet(self) -> tuple[dict, dict, dict]:
        """
        :returns: All the paths json objects
        - paths
        - alarms
        - bigs
        """
        paths = copy.deepcopy(self.conf[fd.paths.jId])
        alarms = copy.deepcopy(self.conf[fd.alarms.jId])
        bigs = copy.deepcopy(self.conf[fd.bigs.jId])
        return paths, alarms, bigs

        # TODO when should we copy
        # dont think gui ever modify
    def pathsSet(self, pathsJso, alarmsJso, bigsJso):
        self.conf[fd.paths.jId] = copy.deepcopy(pathsJso)
        self.conf[fd.alarms.jId] = copy.deepcopy(alarmsJso)
        self.conf[fd.bigs.jId] = copy.deepcopy(bigsJso)

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

    # ################ Sett ################

    def settingsSave(self, jsoObj):
        for f in self.settFlds:
            self.conf[f.jId] = jsoObj[f.jId]

    def settingsGet(self) -> dict:
        res = dict()
        for f in self.settFlds:
            res[f.jId] = self.conf[f.jId]
        return res

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
        self.oldConff = copy.deepcopy(self.conff)

    def validate(self) -> tuple[str, list[ErrPtr]]:
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

        return errTxt, errList


def valPaths(path, ptr, paths) -> list[ErrPtr]:
    errs = list()
    if path[ff.bufFreq.jId] > path[ff.bufSize.jId]:
        v = path[ff.bufFreq.jId]
        txt = "{}: {} should not be bigger than {}"
        err = ErrPtr(ptr+ff.bufFreq, v, txt,
                     ref=ptr+ff.bufSize)
        errs.append(err)
    if len(path[ff.label.jId]) > 3:
        label = path[ff.label.jId]
        txt = "{}: contains {} it is too long: max 3 char."
        err = ErrPtr(ptr+ff.label, label, txt)
        errs.append(err)
    if path[ff.skUnit.jId] == units.txt:
        if path[ff.dpUnit.jId] != units.txt:
            txt = " should be {}".format(units.shortTxt(units.txt))
            txt = "{}: "+txt
            err = ErrPtr(ptr+ff.dpUnit, None, txt, isVal=False)
            errs.append(err)
        if path[ff.bufSize.jId] != 0:
            v = path[ff.bufSize]
            txt = "{}: should be zero not {}"+txt
            err = ErrPtr(ptr+ff.bufSize, v, txt)
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
    cf.addFld(fd.views, empty.noEmpty)
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

    vf = JsoDef(fd.views)
    vf.addFld(ff.viewId, empty.noEmpty, isKey=True)
    vf.addFld(fd.poss, empty.ok)
    defs[vf.idFld.jId] = vf
    viewsPtr = Ptr([fd.conf, fd.views])

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
