from config import Config
from jsonptr import Ptr
from flds import flds as ff
from flds import fldsDict as fd


def test(conf):
    flds = [fd.paths, ff.label]
    keys = ["navigation.courseRhumbline.nextPoint.distance"]
    ptr1 = Ptr(flds, keys)
    v = ptr1.getValue(conf)
    e = "DIS"
    if v != e:
        print("Expected {} got {}".format(e, v))
    flds = [fd.paths]
    ptr = Ptr(flds, keys)
    print(ptr1+ptr)

    print(ptr.getRow(conf))
    ptr = Ptr([fd.paths], [])
    print(ptr.getRows(conf))
    flds = [fd.tabs, fd.poss, ff.pos]
    keys = ["Default", "navigation.speedOverGround"]
    ptr = Ptr(flds, keys)
    v = ptr.getValue(conf)
    e = 1
    if v != e:
        print("Expected {} got {}".format(e, v))


def main():
    conf = Config(isDefault=True)
    d = conf.conf
    test(d)


if __name__ == "__main__":
    main()
