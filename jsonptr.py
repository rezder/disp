from guiflds import Fld
from typing import Self


class Ptr:
    def __init__(self, flds: list[Fld], keys: list[str] = []):
        self.flds: list[Fld] = flds
        self.keys: list[str] = keys
        if len(flds) != 0:
            self.lastFld = flds[-1]
        else:
            self.lastFld = None

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

    def getLastKey(self) -> str:
        key = None
        no = len(self.keys)
        if no != 0:
            key = self.keys[-1]
        else:
            raise Exception("No keys")
        return key

    def isTab(self) -> bool:  # TODO remove when no longer used
        res = False
        for ix in reversed(range(len(self.flds))):
            if self.flds[ix].isDict:
                if self.flds[ix].isKey:
                    res = True
                break
        return res

    def getValue(self, jsonObj: dict):
        if self.lastFld.isDict:
            raise Exception("No field pointer: {}".format(self.lastFld.jId))
        keyIx = 0
        for f in self.flds:
            jsonObj = jsonObj[f.jId]
            if f.isDict and f.isKey:
                jsonObj = jsonObj[self.keys[keyIx]]
                keyIx = keyIx + 1

        return jsonObj

    def getRow(self, jsonObj: dict) -> dict:
        if not self.lastFld.isKey:
            raise Exception("No row pointer {}".format(self.lastFld.jId))
        keyIx = 0
        for f in self.flds:
            jsonObj = jsonObj[f.jId]
            if f.isDict and f.isKey:
                jsonObj = jsonObj[self.keys[keyIx]]
                keyIx = keyIx + 1

        return jsonObj

    def getRows(self, jsonObj: dict) -> dict:
        """
        return rows even if points to a row
        """
        if not self.lastFld.isKey:
            raise Exception("No row pointer {}".format(self.lastFld.jId))
        keys = list(self.keys)
        no = 0
        for f in self.flds:
            if f.isDict and f.isKey:
                no = no + 1
        if len(keys) == no and no != 0:
            keys = keys[:-1]
        if len(keys) < no:
            for f in self.flds:
                keyIx = 0
                jsonObj = jsonObj[f.jId]
                if f.isDict and f.isKey and keyIx < len(keys):
                    jsonObj = jsonObj[self.keys[keyIx]]
        return jsonObj

    def getJsonObj(self, jsonObj: dict) -> dict:
        if not self.lastFld.isDict and self.lastFld.isKey:
            raise Exception("No object pointer")
        keyIx = 0
        for f in self.flds:
            jsonObj = jsonObj[f.jId]
            if f.isDict and f.isKey:
                jsonObj = jsonObj[self.keys[keyIx]]
        return jsonObj

    def path(self) -> str:
        res = ""
        keyIx = 0
        for f in self.flds:
            res = res + f.shortHeader
            if f.isDict and f.isKey and keyIx < len(self.keys):
                res = res + "->"
                res = res + f.shortHeader[:-1]
                res = res + ":"
                res = res + self.keys[keyIx]
                keyIx = keyIx+1
            if f is not self.lastFld:
                res = res + "->"
        return res

    def __eq__(self, o):
        if o is self:
            return True
        if type(o) is Self:
            if len(self.flds) != len(o.flds):
                return False
            if len(self.keys) != len(o.keys):
                return False
            for ix in range(len(self.flds)):
                if self.flds[ix] != o.flds[ix]:
                    return False
            for ix in range(len(self.keys)):
                if self.keys[ix] != o.keys[ix]:
                    return False

        return True

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
