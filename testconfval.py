import config
from flds import flds as ff
from flds import fldsDict as fd
from jsoflds import walkObj

from guiflds import Fld


def test(conf):
    txt, errList = conf.validate()
    print("Errors")
    print(txt)

    ll = [ff.bufFreq, ff.bufSize, ff.broadCP]
    t0 = Fld.txtList(ll, 0)
    t1 = Fld.txtList(ll, 1)
    t2 = Fld.txtList(ll, 2)
    print("Tre lists of fields:")
    print(t0)
    print(t1)
    print(t2)


def main():
    conf = config.Config(isDefault=False)  # TODO change to TRUE for stable results
    #  TODO make test conf with errrors filename is hardcoded in init
    test(conf)
    conff = config.Config.load("./data/testserver.json")
    ptrs = walkObj(conff, conf.jsoDefs)
    print(len(ptrs))
    errs = list()
    for ptr in ptrs:
        err = conf.jsoDefs[ptr.lastFld.jId].validate(conff, ptr)
        errs.extend(err)
    errTxt = ""
    errNo = len(errs)
    if errNo != 0:
        errTxt = "{} contain {} errors!".format(fd.conf.header, errNo)
        for e in errs:
            errTxt = errTxt + "\n" + e.toStr()

    print(errTxt)


if __name__ == "__main__":
    main()
