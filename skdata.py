import units
import json
import asyncio as ass
from status import Status
from status import AlarmMsg


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
                ex = self.alarmTask.exception()
                if ex is not None:
                    print(ex)


class Buffer:
    """
    Small buffer to smoth the signalk data and
    slow it down for the e-paper screen.
    """
    def __init__(self, size, freqNo):
        self.size = size
        self.freqNo = freqNo
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
                self.buff = None

        self.sum = 0.0
        self.no = 0
        self.ix = 0
        self.fregIx = 0
        self.last = None

    def add(self, value: float, dec: int) -> (bool, float):
        if self.size > 1:
            if self.buf[self.ix] is not None:
                self.sum = self.sum - self.buf[self.ix]
                self.no = self.no - 1
            if value is not None:
                self.sum = self.sum + value
                self.no = self.no + 1
            self.buf[self.ix] = value
            self.ix = self.ix + 1
            if self.ix == self.size:
                self.ix = 0

            self.fregIx = self.fregIx + 1
            if self.fregIx == self.freqNo:
                if self.no != 0:
                    v = (self.sum/self.no)
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


class PathData:

    def __init__(self, pathJson, path, status):
        self.path = path
        self.minPeriod = pathJson["minPeriod"]
        self.decimals = pathJson["decimals"]
        self.dispUnits = pathJson["dispUnits"]
        self.label = pathJson["label"]
        self.fn = units.conversion(pathJson["units"], pathJson["dispUnits"])
        self.buffer = Buffer(pathJson["bufSize"], pathJson["bufFreq"])
        self.largeValue = 0
        self.largePathData = None
        self.largePath = None
        if "largeValue" in pathJson:
            self.largeValue = pathJson["largeValue"]
            self.largePath = pathJson["largePath"]
        max = None
        min = None
        isMax = "max" in pathJson
        isMin = "min" in pathJson
        if isMax:
            max = pathJson["max"]
        if isMin:
            min = pathJson["min"]
        if isMin or isMax:
            alarm = Alarm(path, self.label, max, min, 5, status)
            self.alarm = alarm
        else:
            self.alarm = None

    def setLargePathData(self, pd):
        self.largePathData = pd

    def setEnableAlarm(self, isEnable: bool):
        self.alarm.setEnable(isEnable)


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
    def __init__(self, pathsJson: dict, status):
        self.paths: dict[str, PathData] = dict()
        for (p, d) in pathsJson.items():
            self.paths[p] = PathData(d, p, status)
        for d in self.paths.values():
            if d.largePath is not None:
                d.largePathData = self.paths[d.largePath]

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

    def getPathsData(self, path) -> PathData:
        return self.paths[path]

    async def clearTask(self):
        for pd in self.paths.values():
            if pd.alarm is not None:
                await pd.alarm.clearTask()

    def clearBuffers(self):
        for po in self.paths.values():
            po.buffer.clear()
