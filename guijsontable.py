import tkinter as tk
from functools import partial
import guiflds as gf
from guiflddefs import FldDef, Fld


# Row = type(dict[str, gf.GuiFld]) did not work with the editor


class Table:
    def __init__(self,
                 parent: tk.Frame,
                 sortGuiFldDef: FldDef,
                 rowClickCb,
                 tabFldDefs: list[FldDef],
                 showCb=None):
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.showCb = showCb

        self.tabFldDefs: dict[str, FldDef] = dict()
        self.primeFldDef = None
        for v in tabFldDefs:
            self.tabFldDefs[v.fld.jId] = v
            if v.fld.isPrime:
                self.primeFldDef = v

        self.links: dict[str, list[FldDef]] = dict()
        self.calcFlds: list[FldDef] = list()
        for k, fldDef in self.tabFldDefs.items():
            if fldDef.linkDef is not None:
                linkJId = fldDef.linkDef.linkFld.jId
                cl = self.links.get(linkJId, list())
                cl.append(fldDef)
            if not fldDef.isJson:
                self.calcFlds.append(fldDef)

        self.sortFld = sortGuiFldDef.fld
        self.rowsNo = 0
        self.newRowsNo = 0
        self.columnsNo = len(self.tabFldDefs)

        self.rowClickCb = rowClickCb

        self.delKeys: list[str] = list()
        self.headFlds: list[gf.FldLabelHead] = list()
        self.rowsFlds: dict[str | int, dict[str, gf.GuiFld]] = dict()
        self.unUsedRows: list[dict[str, gf.GuiFld]] = list()
        self.keyId = None
        columNo = 0
        for tabFldDef in self.tabFldDefs.values():
            headFld = gf.FldLabelHead(self.mainFrame,
                                      tabFldDef.fld)
            if tabFldDef.isVis:
                headFld.mainFrame.grid(row=0, column=columNo)
                columNo = columNo+1
            else:
                headFld.setVis(False)
            if tabFldDef.fld.isKey:
                self.keyId = tabFldDef.fld.jId
            self.headFlds.append(headFld)

    def addNewRow(self):
        _ = self.createRow(self.newRowsNo)
        self.newRowsNo = self.newRowsNo+1

    def createRow(self, id) -> dict[str, gf.GuiFld]:
        row: dict[str, gf.GuiFld] = dict()
        columnNo = 0
        try:
            row = self.unUsedRows.pop(0)
            for id, guiFld in row.items():
                if guiFld.isVis:
                    guiFld.mainFrame.grid(row=self.rowsNo+1,
                                          column=columnNo,
                                          sticky=guiFld.fld.align)
                    columnNo = columnNo+1
                else:
                    guiFld.setVis(False)
        except IndexError:
            for tabFldDef in self.tabFldDefs.values():
                guiFld = tabFldDef.createFld(self.mainFrame, isTab=True)
                if guiFld.isVis:
                    guiFld.mainFrame.grid(row=self.rowsNo+1,
                                          column=columnNo,
                                          sticky=guiFld.fld.align)
                    columnNo = columnNo+1
                else:
                    guiFld.setVis(False)
                row[guiFld.id] = guiFld
            for k, v in self.links.items():
                masterFld = row[k]
                for slaveFld in v:
                    masterFld.jsonFilter.setSlave(slaveFld)
        self.rowsNo = self.rowsNo + 1
        self.rowsFlds[id] = row
        return row

    def removeRows(self):
        delkeys = list()
        for k, row in self.rowsFlds.items():
            self.unUsedRows.append(row)
            delkeys.append(k)
            for guiFld in row.values():
                guiFld.clear()
                if guiFld.isVis:
                    guiFld.unbind("<ButtonRelease-1>")
                    guiFld.mainFrame.grid_forget()
        for d in delkeys:
            del self.rowsFlds[d]
        self.rowsNo = 0

    def show_AddPrimeCp(self, jsonsObj: dict) -> dict:
        res = dict()
        for k, v in jsonsObj.items():
            newItemJson = None
            if type(v) is dict:
                newItemJson = dict(v)
            else:
                newItemJson = dict()
                newItemJson[self.primeFldDef.fld.jId] = v
            res[k] = newItemJson
        return res

    def show_AddCalc(self, jsonsObj):
        if len(self.calcFlds) > 0 and self.showCb is not None:
            for k, itemJson in jsonsObj.items():
                for fldDef in self.calcFlds:
                    id = fldDef.fld.jId
                    itemJson[id] = self.showCb(k, fldDef.fld, itemJson)

    def show(self, jsonObj: dict):
        jsonObj = self.show_AddPrimeCp(jsonObj)
        self.show_AddCalc(jsonObj)

        #  sort
        self.newRowsNo = 0
        self.delKeys.clear()
        sjsonObj = None
        k = self.sortFld.jId
        if not self.sortFld.isKey:
            k = self.sortFld.jId
            sjsonObj = dict(sorted(jsonObj.items(),
                                   key=lambda item: item[1][k]))
        else:
            sjsonObj = dict(sorted(jsonObj.items(), key=lambda item: item[0]))

        self.removeRows()
        rowNo = 0
        for k, v in sjsonObj.items():
            row = self.createRow(k)
            for guiFld in row.values():
                if guiFld.id in v.keys():
                    if guiFld.isVis:
                        guiFld.bind("<ButtonRelease-1>",
                                    partial(self.rowcb, k, guiFld.id))
                    guiFld.show(v[guiFld.id])
                else:
                    if guiFld.fld.isKey:
                        if guiFld.isVis:
                            guiFld.bind("<ButtonRelease-1>",
                                        partial(self.rowcb, k, guiFld.id))
                        guiFld.show(k)
                    else:
                        guiFld.clear()
            rowNo = rowNo + 1
            self.rowsFlds[k] = row

    def setFld(self, fld: Fld, key: str, value):
        self.rowsFlds[key][fld.jId].show(value)

    def getFld(self, fld: Fld, key):
        return self.rowsFlds[key][fld.jId].get()

    def rowcb(self, path, head, event):
        self.rowClickCb(path, head)

    def get(self) -> tuple[dict, list[str], list[tuple[str, str]]]:
        jsonObj = None
        chgkeys: list[tuple[str, str]] = list()
        if self.validate():
            jsonObj = dict()
            for k, row in self.rowsFlds.items():
                item = dict()
                newk = row[self.keyId].get()
                if k != newk:
                    chgkeys.append((k, newk))
                for fldId, guiFld in row.items():
                    if guiFld.isJson:
                        data = guiFld.get()
                        if data is None:
                            if guiFld.fld.isPrime:
                                item = data
                            else:
                                item[fldId] = data
                jsonObj[newk] = item

        return jsonObj, self.delKeys, chgkeys

    def validate(self) -> bool:
        isOk = True
        for k, row in self.rowsFlds.items():
            for guiFld in row.values():
                fldOk = guiFld.validate()
                if not fldOk:
                    print(guiFld.fld.header)
                isOk = isOk and fldOk
        if not isOk:
            keys = dict()
            for k, row in self.rowsFlds.items():
                row[self.keyId].setError(False)
                if row[self.keyId] in keys:
                    keys[self.keyId].append(k)
                else:
                    ll = list()
                    ll.append(k)
                    keys[self.keyId] = ll
            for k, keyList in keys.items():
                if len(keyList) > 1:
                    isOk = False
                    for key in keyList:
                        self.rowsFlds[key][self.keyId].setError(True)

        return isOk
