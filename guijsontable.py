import tkinter as tk
from functools import partial
import copy

import guiflds as gf
from guiflddefs import FldDef, Fld


# Row = type(dict[str, gf.GuiFld]) did not work with the editor


class Table:
    def __init__(self,
                 parentWin: tk.Toplevel,
                 parent: tk.Frame,
                 sortGuiFldDef: FldDef,
                 tabFldDefs: list[FldDef],
                 tabFldsJson: dict[str, dict] | None = None,
                 showCalcCb=None,
                 isPopUp=True,
                 postChgCb=None,
                 saveFn=None,
                 reloadFn=None):
        self.parentWin = parentWin
        self.isPopUp = isPopUp
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.showCalcFldCb = showCalcCb
        self.postChgCb = postChgCb
        self.saveFn = saveFn
        self.reloadFn = reloadFn
        self.popUpMenuCreate(self.parentWin)
        self.tabFldsJson = tabFldsJson
        if self.tabFldsJson is None:
            self.tabFldsJson = dict()
        self.tabFldDefs: dict[str, FldDef] = dict()
        for v in tabFldDefs:
            self.tabFldDefs[v.fld.jId] = v

        self.links: dict[str, list[FldDef]] = dict()
        self.calcFlds: list[FldDef] = list()
        for k, fldDef in self.tabFldDefs.items():
            if fldDef.linkDef is not None:
                linkJId = fldDef.linkDef.linkFld.jId
                cl = self.links.get(linkJId, list())
                cl.append(fldDef)
                self.links[linkJId] = cl
            if not fldDef.isJson:
                self.calcFlds.append(fldDef)

        self.sortGuiDefFld = sortGuiFldDef
        self.rowsNo = 0
        self.newRowsNo = 0
        self.columnsNo = len(self.tabFldDefs)

        self.allFldsBinds: list[tuple] = list()
        self.delKeys: list[str] = list()
        self.headFlds: list[gf.FldLabelHead] = list()
        self.rowsFlds: dict[str | int, dict[str, gf.GuiFld]] = dict()
        self.unUsedRows: list[dict[str, gf.GuiFld]] = list()
        self.keyId = None
        columNo = 0
        self.clickedKey = None  # Right click for now popMenu
        self.clickedFld = None
        self.copyKey = None

        if self.isPopUp:
            self.allFldsBinds.append(("<Button-3>", self.popMenuUp))
        if postChgCb is not None:
            self.allFldsBinds.append(("rho", self.postChgCb))

        for tabFldDef in self.tabFldDefs.values():
            headFld = gf.FldLabelHead(self.mainFrame,
                                      tabFldDef.fld)
            if tabFldDef.isVis:
                headFld.mainFrame.grid(row=0, column=columNo)
                columNo = columNo+1
                if self.isPopUp:
                    headFld.bind("<Button-3><ButtonRelease-3>",
                                 partial(self.popMenuUp, -1, headFld.fld))

            else:
                headFld.setVis(False)
            if tabFldDef.isKey:
                self.keyId = tabFldDef.fld.jId
            self.headFlds.append(headFld)

    def popUpMenuCreate(self, win: tk.Toplevel):
        if self.isPopUp:
            self.popMenu = tk.Menu(win, tearoff=0)
            self.popMenu.add_command(label="Delete Row",
                                     command=self.deleteRowClicked)
            self.popMenu.add_command(label="New Row",
                                     command=self.addNewRow)
            self.popMenu.add_command(label="Copy Row",
                                     command=self.setCopyKey)
            self.popMenu.add_command(label="Paste Row",
                                     command=self.pasteKey)
            if self.saveFn is not None:
                self.popMenu.add_command(label="Save",
                                         command=self.saveFn)
            if self.reloadFn is not None:
                self.popMenu.add_command(label="Reload",
                                         command=self.reloadFn)
            self.popMenu.bind("<FocusOut>", self.popUpMenuClose)

    def popUpMenuDisableItem(self, label: str):
        try:
            self.popMenu.entryconfigure(label, state=tk.DISABLED)
        except tk.TclError as ex:
            print("popUp menu does not exist: {}".format(ex))

    def popUpMenuClose(self, ev):
        self.popMenu.unpost()

    def popMenuUp(self, key, fld, event):
        self.clickedFld = fld
        self.clickedKey = key
        try:
            self.popMenu.tk_popup(event.x_root,
                                  event.y_root)
        finally:
            self.popMenu.grab_release()

    def addNewRow(self):
        _ = self.createRow(self.newRowsNo)
        self.newRowsNo = self.newRowsNo+1

    def addNewRowWithKey(self) -> int:
        key = self.newRowsNo
        _ = self.createRow(self.newRowsNo)
        self.newRowsNo = self.newRowsNo+1
        return key

    def deleteRowClicked(self):
        key = self.clickedKey
        self.deleteRow(key)

    def setCopyKey(self):
        self.copyKey = self.clickedKey

    def pasteKey(self):
        key = self.clickedKey
        if self.copyKey is not None:
            for fid, guiFld in self.rowsFlds[key].items():
                #  if fid is not self.keyId:
                guiFld.show(self.rowsFlds[self.copyKey][fid].get())

    def deleteRow(self, key):
        if self.copyKey == key:
            self.copyKey = None
        row = self.rowsFlds[key]
        self.moveRowToUnused(row)
        if type(key) is str:
            self.delKeys.append(key)
        del self.rowsFlds[key]
        self.newRowsNo = self.newRowsNo-1

    def setTabFldsJson(self, tabFldsJson: dict[str, dict]):
        self.tabFldsJson = tabFldsJson
        for row in self.unUsedRows:
            for jId, itemsJson in tabFldsJson.items():
                row[jId].setJsonObj(itemsJson)
        for row in self.rowsFlds.values():
            for jId, itemsJson in tabFldsJson.items():
                row[jId].setJsonObj(itemsJson)

    # TODO need a posChg bind use a special seq and add and
    # remove with postChgAdd and remove.
    # only input have postchang and only bool and option need it
    # Entry used FocusOut. Its is a mess. Also fldvar can
    # be monitored but that would include feth and remove
    # And for Entry is the whole autocompletion when is usr
    # done entering data.

    def bindAllVisFields(self, seq: str, cb):
        """
        Binds a callback function to a event to all visable fields
        The table must be empty. And the call back function take
        3 arguments key,fld and event.
        seq examples:
        <ButtonRelease-1>
        <Button-3>
        <FocusIn>
        <FocusOut>
        see https://manpages.debian.org/trixie/tk8.6-doc/bind.3tk.en.html
        """
        if self.rowsNo == 0:
            self.allFldsBinds.append([seq, cb])
        else:
            raise Exception("Rows not zero")

    def createRow_Vis(self, key, guiFld, columnNo) -> int:
        if guiFld.isVis:
            guiFld.mainFrame.grid(row=self.rowsNo+1,
                                  column=columnNo,
                                  sticky=guiFld.fld.align)
            for seq, cb in self.allFldsBinds:
                if seq == "rho":
                    guiFld.postChgAdd(partial(self.postChgCb, key, guiFld.fld))
                else:
                    guiFld.bind(seq, partial(cb, key, guiFld.fld))
            columnNo = columnNo+1
        else:
            guiFld.setVis(False)
        return columnNo

    def createRow(self, key) -> dict[str | int, gf.GuiFld]:
        row: dict[str, gf.GuiFld] = dict()
        columnNo = 0
        try:
            row = self.unUsedRows.pop(0)
            for guiFld in row.values():
                columnNo = self.createRow_Vis(key, guiFld, columnNo)
        except IndexError:
            for tabFldDef in self.tabFldDefs.values():
                guiFld = tabFldDef.createFld(self.mainFrame, isTab=True)
                columnNo = self.createRow_Vis(key, guiFld, columnNo)
                row[guiFld.id] = guiFld
            for jId, itemsJson in self.tabFldsJson.items():
                row[jId].setJsonObj(self.tabFldsJson[jId])

            for k, v in self.links.items():
                masterFld = row[k]
                for slaveFldDef in v:
                    gfld = row[slaveFldDef.fld.jId]
                    masterFld.jsonFilter.setSlave(gfld)
        self.rowsNo = self.rowsNo + 1
        self.rowsFlds[key] = row

        return row

    def removeRows(self):
        """Clear all rows"""
        delkeys = list()
        for k, row in self.rowsFlds.items():
            delkeys.append(k)
            self.moveRowToUnused(row)
        for d in delkeys:
            del self.rowsFlds[d]
        self.rowsNo = 0

    def moveRowToUnused(self, row: dict[str, gf.GuiFld]):
        self.unUsedRows.append(row)
        for guiFld in row.values():
            guiFld.clear()
            if guiFld.isVis:
                for seq, _ in self.allFldsBinds:
                    if seq == "rho":
                        guiFld.postChgRemov()
                    else:
                        guiFld.unbind(seq)
                guiFld.mainFrame.grid_forget()

    def show_AddCalc(self, jsonsObj):
        if len(self.calcFlds) > 0 and self.showCalcFldCb is not None:
            for k, itemJson in jsonsObj.items():
                for fldDef in self.calcFlds:
                    id = fldDef.fld.jId
                    itemJson[id] = self.showCalcFldCb(k, fldDef.fld, itemJson)

    def show(self, inJsonObj: dict):
        self.copyKey = None
        jsonObj = copy.deepcopy(inJsonObj)
        self.show_AddCalc(jsonObj)

        #  sort
        self.newRowsNo = 0
        self.delKeys.clear()
        sjsonObj = None
        if not self.sortGuiDefFld.isKey:
            k = self.sortGuiDefFld.fld.jId
            sjsonObj = dict(sorted(jsonObj.items(),
                                   key=lambda item: item[1][k]))
        else:
            sjsonObj = dict(sorted(jsonObj.items(), key=lambda item: item[0]))

        self.removeRows()
        for k, v in sjsonObj.items():
            row = self.createRow(k)
            for guiFld in row.values():
                if guiFld.id in v.keys():
                    guiFld.show(v[guiFld.id])
                else:
                    if guiFld.isKey:
                        guiFld.show(k)
                    else:
                        # guiFld.clear() bad with linked field
                        # And dont ehink it is needed flds are
                        # cleared
                        pass

    def setFldVal(self, fld: Fld, key: str, value):
        self.rowsFlds[key][fld.jId].show(value)

    def getFldVal(self, fld: Fld, key):
        return self.rowsFlds[key][fld.jId].get()

    def getFld(self, fld: Fld, key) -> gf.GuiFld:
        return self.rowsFlds[key][fld.jId]

    def get(self) -> tuple[dict, list[str], list[tuple[str, str]]]:
        """
        :returns:
        - jsonObj      - The current json object
        - delKeys      - A list of deleted keys
        - chgKeys      - A list of key name change (oldKey,newKey)
        - newKeys      - A list of new keys
        """
        jsonObj = None
        chgKeys: list[tuple[str, str]] = list()
        newKeys: list[str] = list()
        jsonObj = dict()
        for k, row in self.rowsFlds.items():
            item = dict()
            newk = row[self.keyId].get()
            if k != newk:
                if type(k) is int:
                    newKeys.append(newk)
                else:
                    chgKeys.append((k, newk))
            for fldId, guiFld in row.items():
                if guiFld.isJson\
                   and guiFld.linkDef is None\
                   and not guiFld.isKey:

                    data = guiFld.get()
                    if data is not None:
                        item[fldId] = data
            jsonObj[newk] = item

        return jsonObj, self.delKeys, chgKeys, newKeys

    def getAllKeys(self) -> list:
        res = list(self.rowsFlds.keys())
        return res

    def validate(self) -> bool:
        isOk = True
        for k, row in self.rowsFlds.items():
            for guiFld in row.values():
                fldOk = guiFld.validate()
                if not fldOk:
                    print(guiFld.fld.header)
                isOk = isOk and fldOk
        if isOk:
            keys = dict()
            for k, row in self.rowsFlds.items():
                row[self.keyId].setError(False)  # clear
                newKeyId = row[self.keyId].get()
                ids: list[str] = keys.get(newKeyId, list())
                ids.append(k)
                keys[newKeyId] = ids
            for k, keyList in keys.items():
                if len(keyList) > 1:
                    isOk = False
                    for key in keyList:
                        self.rowsFlds[key][self.keyId].setError(True)
        return isOk
