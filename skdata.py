import math
import json
import asyncio as ass

import units
from status import Status
from status import AlarmMsg
from dispdata import DispData
from config import Config


class Alarm:
    def __init__(self,
                 path: str,
                 label: str,
                 max: float,
                 min: float,
                 minTime: float,
                 status: Status):
        self.max = max
        self.min = min
        self.isEnable = True
        self.minTime = minTime
        self.isTriped = False
        self.value = None
        self.alarmTask = None
        self.status = status
        self.path = path
        self.label = label

    def setEnable(self, isEnable: bool):
        self.isEnable = isEnable

    def eval(self, value: float) -> bool:
        res = False
        self.value = value
        if self.isEnable:
            if self.isTriped:
                res = True
            else:
                if self.evalMaxMin_(value):
                    res = True
                    self.tripp(value)
        return res

    def evalMaxMin_(self, value: float) -> bool:
        res = False
        if self.max is not None and value > self.max:
            res = True
        elif self.min is not None and value < self.min:
            res = True
        return res

    def tripp(self, value):
        self.isTriped = True
        self.alarmTask = ass.create_task(self.alarm(), name="Alarm task")
        msg = AlarmMsg(self.path, True, self.label, value)
        self.status.alarmSet(msg)

    def untripp(self):
        self.isTriped = False
        msg = AlarmMsg(self.path, False, self.label)
        self.status.alarmSet(msg)

    async def alarm(self):
        while True:
            await ass.sleep(self.minTime)
            if not self.isEnable or not self.evalMaxMin_(self.value):
                self.untripp()
                break

    async def clearTask(self):
        if self.alarmTask is not None:
            if not self.alarmTask.done():
                self.alarmTask.cancel()
                try:
                    await self.alarmTask
                except ass.CancelledError:
                    pass
            else:
                try: 
                    ex = self.alarmTask.exception()
                    if ex is not None:
                        print(ex)
                except ass.CancelledError:
                    pass


class Buffer:
    """
    Small buffer to smoth the signalk data and
    slow it down for the e-paper screen.
    """
    def __init__(self, size, freqNo, dpUnit):
        self.size = size
        self.freqNo = freqNo
        self.compassVal = 0
        if dpUnit == units.deg:
            self.compassVal = 180
        elif dpUnit == units.rad:
            self.compassVal = math.pi
        if size > 1:
            self.buf = [None, None]
            if size > 2:
                for i in range(3, size+1):
                    self.buf.append(None)
        self.sum = 0.0
        self.no = 0
        self.ix = 0
        self.fregIx = 0
        self.last = None

    def __str__(self) -> str:
        txt = "Size:{},FreqNo:{},Sum:{},No:{},Ix:{},fregIx:{},Last:{},Buff:{}"
        return txt.format(self.size, self.freqNo, self.sum,
                          self.no, self.ix,
                          self.fregIx, self.last, self.buf)

    def clear(self):
        if self.size > 1:
            for i in range(self.size):
                self.buf[i] = None

        self.sum = 0.0
        self.no = 0
        self.ix = 0
        self.fregIx = 0
        self.last = None

    def compassAddToBuf(self, value):
        if self.no > 0:
            for ix in range(self.size):
                if self.buf[ix] is not None:
                    self.buf[ix] = self.buf[ix] + value
            self.sum = self.sum+value*self.no

    def compassModAvg(self, v):
        if v >= 2*self.compassVal:
            v = v-2*self.compassVal
            self.compassAddToBuf(-2*self.compassVal)
        if v < 0:
            v = v+2*self.compassVal
            self.compassAddToBuf(2*self.compassVal)
        return v

    def compassModifyVal(self, value):
        newVal = value
        if self.no > 0:
            diff = (self.sum/self.no) - value
            if diff > self.compassVal:
                newVal = value + 2*self.compassVal
            if diff <= -self.compassVal:
                newVal = value - 2*self.compassVal
        return newVal

    def add(self, value: float, dec: int) -> (bool, float):
        if self.size > 1:
            if value is not None:
                if self.compassVal != 0:
                    value = self.compassModifyVal(value)
                self.sum = self.sum + value
                self.no = self.no + 1
            if self.buf[self.ix] is not None:
                self.sum = self.sum - self.buf[self.ix]
                self.no = self.no - 1
            self.buf[self.ix] = value
            self.ix = self.ix + 1
            if self.ix == self.size:
                self.ix = 0

            self.fregIx = self.fregIx + 1
            if self.fregIx == self.freqNo:
                if self.no != 0:
                    v = self.sum/self.no
                    if self.compassVal != 0:
                        v = self.compassModAvg(v)
                    v = round(v, dec)
                    if self.last != v:
                        res = (True, v)
                        self.last = v
                    else:
                        res = (False, v)
                else:  # Calc Value is None
                    if self.last is None:
                        res = (False, None)
                    else:
                        self.last = None
                        res = (True, None)
                self.fregIx = 0
            else:
                res = (False, None)
        else:  # No buffer
            if value is not None:
                vRound = round(value, dec)
                if vRound != self.last:
                    res = (True, vRound)
                    self.last = vRound
                else:  # Equal
                    res = (False, vRound)
            else:  # value is None
                if self.last is None:
                    res = (False, None)
                else:
                    self.last = None
                    res = (True, None)

        return res


class PathBig:
    def __init__(self,
                 label,
                 decimals,
                 unit,
                 dpUnit,
                 bufSize,
                 bufFreq):
        self.decimals = decimals
        self.dispUnits = dpUnit
        self.fn = units.conversion(unit, dpUnit)
        self.buffer = Buffer(bufSize, bufFreq, dpUnit)
        self.label = label

    def createDispData(self, value):
        dd = None
        v = None
        if value is not None:
            v = self.fn(value)
        isUpdate, bv = self.buffer.add(v, self.decimals)
        if isUpdate:
            dd = DispData(bv, self.decimals, self.label, self.dispUnits, False)
        return dd, bv


class Path(PathBig):
    def __init__(self, path, pathJson, bigJson):
        self.id = path
        self.minPeriod = pathJson["minPeriod"]
        super().__init__(pathJson["label"],
                         pathJson["decimals"],
                         pathJson["units"],
                         pathJson["dispUnits"],
                         pathJson["bufSize"],
                         pathJson["bufFreq"])

        self.pathBig = None
        self.bigValue = None
        if bigJson is not None:
            self.bigValue = bigJson["limit"]
            self.pathBig = PathBig(pathJson["label"],
                                   bigJson["decimals"],
                                   pathJson["units"],
                                   bigJson["dispUnits"],
                                   pathJson["bufSize"],
                                   pathJson["bufFreq"])
        self.alarm = None

    def createDispData(self, value) -> DispData | None:
        dd, bv = super().createDispData(value)
        if dd is not None:
            if self.alarm is not None:
                isAlarm = self.alarm.eval(bv)
                dd.isAlarm = isAlarm
        if self.pathBig is not None:
            bigDd, bigBv = self.pathBig.createDispData(value)
            if bv is not None and self.bigValue < abs(bv):
                if bigDd is not None:
                    bigDd.isAlarm = dd.isAlarm
                    self.buffer.last = self.pathBig.buffer.last
                    dd = bigDd
            else:
                self.pathBig.buffer.last = self.buffer.last

        return dd

    def setEnableAlarm(self, isEnable: bool):
        self.alarm.setEnable(isEnable)

    def setAlarm(self, alarmJson: dict, status):
        max = None
        min = None
        isMax = "max" in alarmJson
        isMin = "min" in alarmJson
        if isMax:
            max = alarmJson["max"]
        if isMin:
            min = alarmJson["min"]

        alarm = Alarm(self.id, self.label, max, min, 5, status)
        self.alarm = alarm


class SkData:
    """
    The displays Signal k config data. configured in the
    ./skdata.json file.
    The sub messages do not filter on source but
    they could navigation.speedThroughWater.values[n2kFromFile.43]
    by adding ,values[source key].
    Did not see the logic in the key construction must find
    it in signal k server it is the $source $ indicate a
    pointer and that have a dot notaion. May have to add it later if
    I get multible source problems.
    """
    def __init__(self, conf: Config, status):
        self.paths: dict[str, Path] = dict()
        pathsJson, _, _ = conf.pathsGet()
        for (p, d) in pathsJson.items():
            big = conf.pathsGetBigUnit(p)
            path = Path(p, d, big)
            alarmJson = conf.pathsGetAlarm(p)
            if alarmJson is not None:
                path.setAlarm(alarmJson, status)
            self.paths[p] = path

    def msgUnsubAll(self) -> str:
        jsonDict = {
            "context": "*",
            "unsubscribe": [
                {
                    "path": "*"
                }
            ]
        }
        txt = json.dumps(jsonDict)
        return txt

    def msgUnsubPaths(self, paths) -> str:
        raise Exception("Signal k does not allow this for now")
        unsubJson = {
            "context": "vessels.self",
            "unsubscribe": [
            ]
        }
        for p in paths:
            pj = SkData._defaultUnSub()
            pj["path"] = p
            unsubJson["unsubscribe"].append(pj)
        txt = json.dumps(unsubJson)
        return txt

    def _defaultUnSub() -> dict:
        subJson = {
            "path": "x"
        }
        return subJson

    def msgSubPaths(self, paths) -> str:
        subJson = {
            "context": "vessels.self",
            "subscribe": [
            ]
        }
        for p in paths:
            pj = SkData._defaultSub()
            pj["path"] = p
            pj["minPeriod"] = self.paths[p].minPeriod
            subJson["subscribe"].append(pj)

        txt = json.dumps(subJson)
        return txt

    def _defaultSub() -> dict:
        subJson = {
            "path": "x",
            "format": "delta",
            "policy": "instant",
            "minPeriod": 1000
        }
        return subJson

    def getPath(self, path) -> Path:
        return self.paths[path]

    async def clearTask(self):
        for pd in self.paths.values():
            if pd.alarm is not None:
                await pd.alarm.clearTask()

    def clearBuffers(self):
        for po in self.paths.values():
            po.buffer.clear()
