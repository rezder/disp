import math

from guiflds import Fld
from jsonptr import Ptr, ErrPtr
import empty


class ObjFld():
    def __init__(self,
                 fld: Fld,  # Maybe it should be a field for Ptr
                 empty: int,
                 refPtr: Ptr,
                 isKey: bool = False
                 ):
        self.fld = fld
        self.empty = empty
        self.refPtr = refPtr
        self.isKey = isKey
        self.jId = fld.jId

    def __repr__(self):
        txt = "{} empty:{},ref:{}, key:{}"
        return txt.format(self.jId,
                          empty.numToTxt(self.empty),
                          self.refPtr, self.isKey)


class JsoDef:

    def __init__(self, idFld: Fld, valCb=None):
        self.idFld = idFld
        self.isTab = idFld.isKey
        self.allFlds: list[ObjFld] = list()
        self.allFldIds: list[str] = list()
        self.flds: list[ObjFld] = list()
        self.keyFld = None
        self.refs: list[ObjFld] = list()
        self.cb = valCb

    def addFld(self, fld: Fld,
               empty: int = empty.ok,
               refPtr: Ptr | None = None,
               isKey: bool = False,
               isMan: bool = True,
               ):
        objFld = ObjFld(fld, empty, refPtr, isKey)
        if isKey:
            self.keyFld = objFld
        else:
            self.allFlds.append(objFld)
            self.allFldIds.append(objFld.jId)
            if isMan:
                self.flds.append(objFld)
        if refPtr is not None:
            self.refs.append(objFld)

    def validate(self, obj: dict, curPtr: Ptr) -> list[ErrPtr]:
        errPtrs: list[ErrPtr] = list()
        curObj = None
        if self.isTab:
            curObj = curPtr.getRow(obj)
        else:
            curObj = curPtr.getJsonObj(obj)
        mTxt = "Field {} is missing"
        uTxt = "{} has a unkown field: {}"
        for f in self.flds:
            if f.jId not in curObj.keys():
                errPtr = ErrPtr(curPtr + f.fld, None, mTxt, isVal=False)
                errPtrs.append(errPtr)
        for fid in curObj.keys():
            if fid not in self.allFldIds:
                errPtr = ErrPtr(curPtr, fid, uTxt)
                errPtrs.append(errPtr)

        kTxt = "Field: {} contain illegal value!"
        mTxt = "Field: {} contains illegal value: {}"
        if self.isTab:
            key = curPtr.getLastKey()
            if not keyCheck(key):
                errPtr = ErrPtr(curPtr, None, kTxt, isVal=False)
                errPtrs.append(errPtr)
        for f in self.allFlds:
            if f.jId in curObj.keys():
                value = curObj[f.jId]
                txtValue = "{}".format(value)
                if not valueCheck(value, f.fld):
                    errPtr = ErrPtr(curPtr + f.fld,
                                    txtValue, mTxt, isVal=True)
                    errPtrs.append(errPtr)
                else:
                    if not emptyCheck(value, f):
                        errPtr = ErrPtr(curPtr + f.fld,
                                        txtValue, mTxt, isVal=True)
                        errPtrs.append(errPtr)

        if len(errPtrs) == 0:
            kTxt = "{} is missing from {}"
            mTxt = "{Field: {}:{} is missing from{}"
            for rf in self.refs:
                rv = None
                if rf.fld.isKey:
                    rv = curPtr.getLastKey()
                else:
                    rv = curObj[rf.jId]
                if rv not in rf.refPtr.getRows(obj).keys():
                    if rf.isKey:
                        errPtr = ErrPtr(curPtr, None, kTxt,
                                        ref=rf.refPtr, isVal=False)
                        errPtrs.append(errPtr)
                    else:
                        errPtr = ErrPtr(curPtr+rf.fld,
                                        rv, mTxt, ref=rf.refPtr)
                        errPtrs.append(errPtr)

        if len(errPtrs) == 0 and self.cb is not None:
            if self.isTab:
                errs = self.cb(curObj, curPtr, curPtr.getRows(obj))
                errPtrs.extend(errs)
            else:
                errs = self.cb(curObj, curPtr)
                errPtrs.extend(errs)

        return errPtrs


def emptyCheck(value, f: ObjFld):
    """ Only run if no value error
    type is ok no None
    """
    isOk = True
    if type(value) is str:
        if value == "" and f.empty == empty.noEmpty:
            isOk = False
    if type(value) is float:
        if math.isnan(value):
            if f.empty in [empty.noNaN, empty.noNaNZero]:
                isOk = False
        elif value == 0.0 and f.empty == empty.noZero:
            isOk = False
    if type(value) is int and f.empty == empty.noZero and value == 0:
        isOk = False
    return isOk


def valueCheck(val, fld: Fld) -> bool:
    isOk = True
    if type(val) is not fld.fType:
        isOk = False
    elif fld.isDom:
        try:
            fld.toStr(val)
        except KeyError:
            isOk = False
    return isOk


def keyCheck(key) -> bool:
    isOk = True
    if type(key) is not str:
        isOk = False
    elif len(key) == 0:
        isOk = False
    return isOk


def walkObj(obj: dict, jsoDefs: dict[str, JsoDef]) -> list[Ptr]:
    ptrList: list[Ptr] = list()
    curPtr = Ptr([])
    walkObj_recursiv(obj, jsoDefs, curPtr, ptrList)

    return ptrList


def walkObj_recursiv(obj: dict,
                     jsoDefs: dict[str, JsoDef],
                     curPtr: Ptr,
                     ptrList: list[Ptr]):

    for fid, v in obj.items():
        if type(v) is dict:
            if fid in jsoDefs.keys():
                objFld = jsoDefs[fid].idFld
                if objFld.isKey:
                    #  TODO what about empty tables I can catch them here
                    for key in obj[fid].keys():
                        curKeyPtr = curPtr + objFld + key
                        ptrList.append(curKeyPtr)
                        walkObj_recursiv(obj[fid][key], jsoDefs, curKeyPtr, ptrList)
                else:
                    curPtr = curPtr + objFld
                    ptrList.append(curPtr)
                    walkObj_recursiv(obj[fid], jsoDefs, curPtr, ptrList)
            else:
                raise Exception("Missing obj: {}".format(fid))
