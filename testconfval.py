from config import Config
from flds import flds

from guiflds import Fld


def test(conf):
    txt = conf.validate()
    print("Errors")
    print(txt)

    ll = [flds.bufFreq, flds.bufSize, flds.broadCP]
    t0 = Fld.txtList(ll, 0)
    t1 = Fld.txtList(ll, 1)
    t2 = Fld.txtList(ll, 2)
    print("Tre lists of fields:")
    print(t0)
    print(t1)
    print(t2)


def main():
    conf = Config(isDefault=False)  # TODO change to TRUE for stable results
    #  TODO make test conf with errrors filename is hardcoded in init
    test(conf)


if __name__ == "__main__":
    main()
