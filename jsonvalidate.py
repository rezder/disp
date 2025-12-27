from guiflds import Fld

from jsonptr import Ptr, ErrPtr


def refCheck(obj: dict,
             refPtr: Ptr,
             tabPtr: Ptr,
             tabObj: dict) -> list[ErrPtr]:

    errPtrs: list[ErrPtr] = list()

    if refPtr.isTab():
        kTxt = "{} is missing from {}"
        txt = "{}:{} is missing from {}"
        for key, row in obj.items():
            rv = None
            if refPtr.lastFld.isDict:
                rv = key
            else:
                rv = row[refPtr.lastFld.jId]
            if rv is not None:  # Need value check first
                if rv not in tabObj.keys():
                    if refPtr.lastFld.isDict:
                        errPtr = ErrPtr(refPtr + key, None, kTxt,
                                        isVal=False, ref=tabPtr)
                    else:
                        errPtr = ErrPtr(refPtr + key, rv, txt, ref=tabPtr)
                    errPtrs.append(errPtr)
    else:
        rv = obj[refPtr.lastFld.jId]
        if rv is not None:  # Need value check first
            if rv not in tabObj.keys():
                errPtr = ErrPtr(refPtr, rv, txt, ref=tabPtr)
                errPtrs.append(errPtr)
    return errPtrs


def missExtFlds(obj: dict,
                objPtr: Ptr,
                flds: list[Fld],
                optFlds: list[Fld]) -> list[ErrPtr]:
    errPtrs: list[ErrPtr] = list()
    allFlds = list()
    for f in flds:
        allFlds.append(f.jId)
    for f in optFlds:
        allFlds.append(f.jId)
    mTxt = "Field {} is missing"
    uTxt = "{} has a unkown field: {}"
    if objPtr.lastFld.isKey:
        for k, d in obj.items():
            for f in flds:
                if f.jId not in d.keys():
                    errPtr = ErrPtr(objPtr + k + f, None, mTxt, isVal=False)
                    errPtrs.append(errPtr)
            for fid in d.keys():
                if fid not in allFlds:
                    errPtr = ErrPtr(objPtr + k, fid, uTxt)
                    errPtrs.append(errPtr)
    else:
        for f in flds:
            if f.jId not in obj.keys():
                errPtr = ErrPtr(objPtr + f, None, mTxt, isVal=False)
                errPtrs.append(errPtr)
            for fid in obj.keys():
                if fid not in allFlds:
                    errPtr = ErrPtr(objPtr, fid, uTxt)
                    errPtrs.append(errPtr)
    return errPtrs


def validateFlds(obj: dict,
                 objPtr: Ptr,
                 flds: list[Fld],
                 optFlds: list[Fld]) -> list[ErrPtr]:
    errPtrs: list[ErrPtr] = list()
    allFlds = list(flds)
    allFlds.extend(optFlds)
    mTxt = "Field: {} contain illegal value: {}"
    if objPtr.lastFld.isKey:
        for key, row in obj.items():
            if not keyCheck(key):
                errPtr = ErrPtr(objPtr + key, key, mTxt, isVal=True)
                errPtrs.append(errPtr)

            for f in flds:
                if f.jId in row.keys():
                    value = row[f.jId]
                    txtValue = "{}".format(value)
                    if not valueCheck(value, f):
                        errPtr = ErrPtr(objPtr + key + f,
                                        txtValue, mTxt, isVal=False)
                        errPtrs.append(errPtr)

    else:
        for f in flds:
            if f.jId in obj.keys():
                value = obj[f.jId]
                txtValue = "{}".format(value)
                if not valueCheck(value, f):
                    errPtr = ErrPtr(objPtr + f,
                                    txtValue, mTxt, isVal=False)
                    errPtrs.append(errPtr)

    return errPtrs


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
