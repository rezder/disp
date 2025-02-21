from skdata import SkData
from status import Status
from config import Config
from skdata import Buffer
from dispdata import DispData
from handler import parseSkUpdates


def px(v, exp, isRaise=True):
    if v != exp:
        txt = "Expected:{} got: {}".format(exp, v)
        if isRaise:
            raise Exception(txt)
        else:
            print("Expected:{} got: {}".format(exp, v))


def testSubSk(skData):
    print(skData.msgUnsubAll())


def testPathNoBuffer(pathId,
                     value,
                     exp,
                     pos,
                     skData):
    path = skData.getPath(pathId)
    dd = path.createDispData(value)
    print(dd.value)
    print(dd.encode(pos))
    px(dd.value, exp)
    return dd


def testPathBuffer(pathId, values, exp, pos, skData: SkData):
    path = skData.getPath(pathId)
    size = path.buffer.size
    freq = path.buffer.freqNo

    if size != len(values):
        print("Error data is not usefull")
    else:
        for i in range(len(values)):
            v = values[i]
            dd = path.createDispData(v)
            print(path.buffer)
            if i != freq-1:
                if dd is not None:
                    print("Error expected None got {}".format(dd))
            else:
                print(dd.value)
                print(dd.encode(pos))
                px(dd.value, exp)


def testPathCreateMsg(skData: SkData, status: Status, conf: Config):
    path = "environment.depth.belowTransducer"
    value = 7.0
    exp = 7.0
    pos = 2
    testPathNoBuffer(path, value, exp, pos, skData)

    path = "navigation.speedOverGround"
    values = [10.0, 5.0, 10.0, 3.0]
    pos = 3
    exp = 13.6
    testPathBuffer(path, values, exp, pos, skData)
    path = "navigation.courseOverGroundTrue"
    values = [3.12, 3.12, 3.14, 3.14]
    pos = 0
    exp = 179
    testPathBuffer(path, values, exp, pos, skData)
    skData.clearBuffers()
    values = [6.24, 6.24, 0, 0]
    pos = 0
    exp = 0
    try:
        testPathBuffer(path, values, exp, pos, skData)
    except Exception:
        print("Error Avg cours does not work")

    path = "navigation.courseRhumbline.crossTrackError"
    value = -122
    exp = -122
    pos = 3
    testPathNoBuffer(path, value, exp, pos, skData)

    value = 122
    exp = 122
    pos = 2
    testPathNoBuffer(path, value, exp, pos, skData)

    value = 1928
    exp = 1928
    pos = 1
    testPathNoBuffer(path, value, exp, pos, skData)

    path = "navigation.courseRhumbline.nextPoint.distance"
    value = 1600
    pos = 3
    exp = 0.9
    testPathNoBuffer(path, value, exp, pos, skData)

    value = 1000
    pos = 1
    exp = 0.5
    testPathNoBuffer(path, value, exp, pos, skData)

    with open("./testskdata.json", "r") as f:
        skMsg = f.read()
        bb = parseSkUpdates(skMsg, skData, status)
        print(bb)


def testBuffer():
    b = Buffer(4, 4)
    isUpdate, value = b.add(1.5, 1)
    if isUpdate:
        print("expexted false")
    isUpdate, value = b.add(None, 1)
    if isUpdate:
        print("expexted false")
    isUpdate, value = b.add(1.5, 1)
    if isUpdate:
        print("expexted false")
    isUpdate, value = b.add(1.5, 1)
    if not isUpdate:
        print("expexted true")
    else:
        px(value, 1.5)
        if b.fregIx != 0 or b.ix != 0 or b.sum != 4.5 or b.no != 3:
            print("Failed add")


def testDispDataEncoding():
    pos = 1
    dp = DispData(1.2, 1, "SOG", 0, False)
    buff = dp.encode(pos)
    print(buff)
    dpcopy = DispData.decode(buff)
    if dpcopy.value != dp.value:
        print("should only be a rounding error: ")
        print(dpcopy.value, dp.value)

    print(dpcopy.encode(pos))

    if dp.encode(pos) != dpcopy.encode(pos):
        print("decoded copy deviates")


def testPathRefSearch(conf: Config):
    path = "environment.depth.belowTransducer"
    tabs = conf.getPathsRefs(path)
    print(tabs)
    if len(tabs) != 0:
        print("expected path references in tabs: {}".format(tabs))


def main():
    print("###################################################Start test"
          "###################################################")
    status = Status()
    conf = Config(isDefault=True)
    skData = SkData(conf.getPathsJson(), status)

    testSubSk(skData)
    testPathCreateMsg(skData, status, conf)
    testBuffer()

    print(conf.getBroadcastIp())

    testDispDataEncoding()
    testPathRefSearch(conf)


if __name__ == "__main__":
    main()
