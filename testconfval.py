from config import Config
from flds import flds

from guiflds import Fld


def test(conf):
    txt = conf.validate()
    print(txt)
    ll = [flds.bufFreq, flds.bufSize]
    t0 = Fld.txtList(ll, 0)
    t1 = Fld.txtList(ll, 1)
    t2 = Fld.txtList(ll, 2)
    print(t0)
    print(t1)
    print(t2)


def main():
    conf = Config(isDefault=True)
    test(conf)


if __name__ == "__main__":
    main()
