from skdata import SkData
from handler import createDispMsq, parseSkUpdates
from status import Status
from config import Config
from skdata import Buffer
from dispdata import DispData


def main():
    status = Status()
    conf = Config()
    skData = SkData(conf.getPathsJson(), status)
    print(skData.msgUnsubAll())
    paths = ["environment.depth.belowTransducer",
             "navigation.courseRhumbline.crossTrackError"]

    print(skData.msgUnsubPaths(paths))

    path = "environment.depth.belowTransducer"
    value = 7.0
    # for i in range(2):
    # createDispMsq(skData, path, value)
    dd = createDispMsq(skData, path, value)
    print(dd.encode(2))

    path = "navigation.speedOverGround"
    value = 10.0
    for i in range(3):
        createDispMsq(skData, path, value)
    dd = createDispMsq(skData, path, value)
    print(dd.encode(1))

    path = "navigation.courseOverGroundTrue"
    value = 3.14
    for i in range(3):
        createDispMsq(skData, path, value)
    dd = createDispMsq(skData, path, value)
    print(dd.encode(0))
    path = "navigation.courseRhumbline.crossTrackError"
    value = -122
    dd = createDispMsq(skData, path, value)
    print(dd.encode(3))
    path = "navigation.courseRhumbline.crossTrackError"
    value = 122
    dd = createDispMsq(skData, path, value)
    print(dd.encode(2))
    value = 1928
    dd = createDispMsq(skData, path, value)
    print(dd.encode(1))
    path = "navigation.courseRhumbline.nextPoint.distance"
    value = 1600
    dd = createDispMsq(skData, path, value)
    print("Expect 0.9 nm")
    print(dd.encode(3))
    value = 1000
    dd = createDispMsq(skData, path, value)
    print("Expect 0.5 nm")
    print(dd.encode(1))
    with open("./testskdata.json", "r") as f:
        skMsg = f.read()
        print(skMsg)
        bb = parseSkUpdates(skMsg, skData, status)
        print(bb)

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
        if value != 1.5:
            print("expect 1.5 got {}".format(value))
    if b.fregIx != 0 or b.ix != 0 or b.sum != 4.5 or b.no != 3:
        print("Failed add")

    print(conf.getBroadcastIp())
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
    path = "environment.depth.belowTransducer"
    paths, tabs = conf.getPathsRefs(path)
    print(paths)
    print(tabs)
    if len(paths) != 0:
        print("Expected  no reference in paths: {}".format(paths))
    if len(tabs) != 0:
        print("expected path references in tabs: {}".format(tabs))
    path = "1"
    paths, tabs = conf.getPathsRefs(path)
    print(paths)
    print(tabs)
    if len(paths) != 1:
        print("Expected on referense in paths: {}".format(paths))
    if len(tabs) != 0:
        print("expected  zero path references in tabs: {}".format(tabs))


if __name__ == "__main__":
    main()
