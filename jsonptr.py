from guiflds import Fld
from typing import Self


class Ptr:
    def __init__(self, flds: list[Fld], keys: list[str]):
        self.flds = flds
        self.keys = keys
        self.lastFld = flds[-1]

    def __add__(self, o: Self | str | Fld) -> Self:
        if isinstance(o, str):
            flds = list(self.flds)
            keys = list(self.keys)
            keys.append(o)
        elif isinstance(o, Fld):
            flds = list(self.flds)
            keys = list(self.keys)
            flds.append(o)
        else:
            flds = list(self.flds)
            flds.extend(o.flds)
            keys = list(self.keys)
            keys.extend(o.keys)
        return Ptr(flds, keys)

    def isTab(self) -> bool:
        res = False
        for ix in reversed(range(len(self.flds))):
            print(ix)
            print(self.flds[ix])
            print(self.flds[ix].isKey)
            if self.flds[ix].isKey:
                res = True
                break
            elif self.flds[ix].isDict:
                res = False
                break
        return res

    def getValue(self, jsonObj: dict):
        if self.lastFld.isKey or self.lastFld.isDict:
            raise Exception("No field pointer: {}".format(self.lastFld.jId))
        keyIx = 0
        for f in self.flds:
            if f.isKey:
                jsonObj = jsonObj[self.keys[keyIx]]
                keyIx = keyIx + 1
            else:
                jsonObj = jsonObj[f.jId]

        return jsonObj

    def getRow(self, jsonObj: dict) -> dict:
        if not self.lastFld.isKey:
            raise Exception("No row pointer {}".format(self.lastFld.jId))
        keyIx = 0
        for f in self.flds:
            if f.isKey:
                jsonObj = jsonObj[self.keys[keyIx]]
            else:
                jsonObj = jsonObj[f.jId]

        return jsonObj

    def getJsonObj(self, jsonObj: dict) -> dict:
        if not self.lastFld.isDict:
            raise Exception("No object pointer")
        keyIx = 0
        for f in self.flds:
            if f.isKey:
                jsonObj = jsonObj[self.keys[keyIx]]
            else:
                jsonObj = jsonObj[f.jId]

        return jsonObj

    def path(self) -> str:
        res = ""
        keyIx = 0
        for f in self.flds:
            res = res + f.shortHeader
            if f.isKey and keyIx < len(self.keys):
                res = res + ":"
                res = res + self.keys[keyIx]
                keyIx = keyIx+1
            if f is not self.lastFld:
                res = res + "->"
        return res

    def __repr__(self) -> str:
        return self.path()


class ErrPtr:
    def __init__(self, ptr: Ptr, value, txt: str,
                 isVal: bool = True,
                 ref: Ptr = None):
        self.ptr = ptr
        self.value = value
        self.isVal = isVal
        self.txt = txt
        self.ref = ref

    def toStr(self) -> str:
        v = [self.ptr.path()]
        if self.isVal:
            v.append(self.value)
        if self.ref is not None:
            v.append(self.ref.path())

        return self.txt.format(*v)

    def __repr__(self) -> str:
        return self.toStr()
