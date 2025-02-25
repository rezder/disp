import tkinter as tk
from functools import partial
import guijson as gj

Row = type(dict[str, gj.Fld])


class TabFldDef:
    def __init__(self,
                 fldDef: gj.FldDef,
                 width: int,
                 fldClass,
                 isVis: bool = True,
                 options:  list | None = None,
                 optJson: dict | None = None,
                 optJsonHead: str | None = None,
                 defaultVal=None,
                 isMan: bool = True,
                 isKey: bool = False,
                 isJson: bool = True
                 ):
        self.fldDef = fldDef
        self.width = width
        self.fldClass = fldClass
        self.isVis = isVis
        self.options = options
        self.optJson = optJson
        self.optJsonHead = optJsonHead
        self.defaultVal = defaultVal
        self.isMan = isMan
        self.isKey = isKey
        self.isJson = isJson
        self.delkeys: list[str] = list()

    def createFld(self, parent: tk.Frame) -> gj.Fld:
        fld = None
        if self.fldClass == gj.FldLabel:
            fld = gj.FldLabel(parent,
                              self.fldDef,
                              self.width,
                              noCap=True,
                              isMan=self.isMan,
                              default=self.defaultVal)
        elif self.fldClass == gj.FldEntry:
            fld = gj.FldEntry(parent,
                              self.fldDef,
                              self.width,
                              noCap=True,
                              isMan=self.isMan,
                              default=self.defaultVal)
        elif self.fldClass == gj.FldOpt:
            fld = gj.FldOpt(parent,
                            self.fldDef,
                            self.width,
                            self.options,
                            self.defaultVal,
                            noCap=True
                            )
        elif self.fldClass == gj.FldOptJson:
            fld = gj.FldOptJson(parent,
                                self.fldDef,
                                self.width,
                                self.optJson,
                                self.optJsonHead,
                                self.defaultVal,
                                noCap=True
                                )
        return fld


class Table:
    def __init__(self,
                 parent: tk.Frame,
                 sortFldDef: TabFldDef,
                 rowClickCb,
                 tabFldDefs: list[TabFldDef]):
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)

        self.tabFldDefs = tabFldDefs
        self.sortFldDef = sortFldDef.fldDef
        self.rowsNo = 0
        self.newRowsNo = 0
        self.columnsNo = len(self.tabFldDefs)

        self.rowClickCb = rowClickCb

        self.delKeys: list[str] = list()
        self.headFlds: list[gj.FldLabelHead] = list()
        self.rowsFlds: dict[str | int, Row] = dict()
        self.unUsedRows: list[Row] = list()
        self.keyId = None
        columNo = 0
        for tabFldDef in self.tabFldDefs:
            headFld = gj.FldLabelHead(self.mainFrame,
                                      tabFldDef.fldDef,
                                      tabFldDef.width)
            if tabFldDef.isVis:
                headFld.mainFrame.grid(row=0, column=columNo)
                columNo = columNo+1
            else:
                headFld.setVis(False)
            if tabFldDef.fldDef.isKey:
                self.keyId = tabFldDef.fldDef.jsonHead
            self.headFlds.append(headFld)

    def addNewRow(self):
        _ = self.createRow(self.newRowsNo)
        self.newRowsNo = self.newRowsNo+1

    def createRow(self, id) -> Row:
        row: Row = dict()
        columnNo = 0
        try:
            row = self.unUsedRows.pop(0)
            for id, fld in row.items():
                if fld.isVis:
                    fld.mainFrame.grid(row=self.rowsNo+1,
                                       column=columnNo,
                                       sticky=fld.fldDef.align)
                    columnNo = columnNo+1
                else:
                    fld.setVis(False)
        except IndexError:
            for tabFldDef in self.tabFldDefs:
                fld = tabFldDef.createFld(self.mainFrame)
                if fld.isVis:
                    fld.mainFrame.grid(row=self.rowsNo+1,
                                       column=columnNo,
                                       sticky=fld.fldDef.align)
                    columnNo = columnNo+1
                else:
                    fld.setVis(False)
                row[fld.id] = fld
        self.rowsNo = self.rowsNo + 1
        self.rowsFlds[id] = row
        return row

    def removeRows(self):
        delkeys = list()
        for k, row in self.rowsFlds.items():
            self.unUsedRows.append(row)
            delkeys.append(k)
            for fld in row.values():
                fld.clear()
                if fld.isVis:
                    fld.unbind("<ButtonRelease-1>")
                    fld.mainFrame.grid_forget()
        for d in delkeys:
            del self.rowsFlds[d]
        self.rowsNo = 0

    def show(self, jsonObj: dict):
        #  sort
        self.newRowsNo = 0
        self.delKeys.clear()
        sjsonObj = None
        k = self.sortFldDef.jsonHead
        if not self.sortFldDef.isKey:
            k = self.sortFldDef.jsonHead
            sjsonObj = dict(sorted(jsonObj.items(),
                                   key=lambda item: item[1][k]))
        else:
            sjsonObj = dict(sorted(jsonObj.items(), key=lambda item: item[0]))

        self.removeRows()
        rowNo = 0
        for k, v in sjsonObj.items():
            row = self.createRow(k)
            for fld in row.values():
                if fld.isJson and fld.id in v.keys():
                    if fld.isVis:
                        fld.bind("<ButtonRelease-1>",
                                 partial(self.rowcb, k, fld.id))
                    fld.show(v[fld.id])
                else:
                    if fld.fldDef.isKey:
                        if fld.isVis:
                            fld.bind("<ButtonRelease-1>",
                                     partial(self.rowcb, k, fld.id))
                        data = k
                        if not fld.isJson:
                            raise Exception("Not implemented")
                        fld.show(data)
                    else:
                        fld.clear()
            rowNo = rowNo + 1
            self.rowsFlds[k] = row

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
                for fldId, fld in row.items():
                    if fld.isVis:
                        try:
                            item[fldId] = fld.get()
                        except (ValueError, KeyError):
                            pass
                jsonObj[newk] = item

        return jsonObj, self.delKeys, chgkeys

    def validate(self) -> bool:
        isOk = True
        for k, row in self.rowsFlds.items():
            for fld in row.values():
                fldOk = fld.validate()
                if not fldOk:
                    print(fld.fldDef.header)
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
