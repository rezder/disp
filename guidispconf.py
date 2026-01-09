import tkinter as tk

import guiflds as gf
from flds import fldsDict as fd
from guijsontable import Table
from flds import disp as df
from guiflds import jsonOuterJoin, jsonOuterJsonSplit
from gui import BORDER_COLOR, BORDER_WIDTH


class Disp:
    def __init__(self,
                 parentWin: tk.Toplevel,
                 parent: tk.Frame,
                 logger,
                 validateFn,
                 saveFn
                 ):
        self.parentWin = parentWin
        self.parent = parent
        self.logger = logger
        self.confValidateFn = validateFn
        self.confSaveFn = saveFn
        self.oldDisps = None
        self.oldMacs = None
        self.oldViews = None
        self.paths = None
        self.macsDefaults = {df.addr.fld.jId: "",
                             df.dis.fld.jId: False}
        self.mainFrame = tk.Frame(self.parent)
        topFrame = tk.Frame(self.mainFrame,
                            highlightthickness=BORDER_WIDTH,
                            highlightbackground=BORDER_COLOR)
        topFrame.pack(expand=True, fill="x")
        title = tk.Label(topFrame, text=fd.poss.header)
        title.pack()
        tabsFrame = tk.Frame(topFrame)
        tabsFrame.pack(expand=True, fill="x")
        viewsFlds = [df.viewId, df.poss]
        self.viewTab = Table(self.parentWin,
                             tabsFrame,
                             df.viewId,
                             viewsFlds,
                             isPopUp=False)
        self.viewTab.bindAllVisFields("<ButtonRelease-1>", self.viewClick)
        self.viewTab.mainFrame.pack(side=tk.LEFT, anchor=tk.N)
        possFrame = tk.Frame(tabsFrame,
                             highlightthickness=BORDER_WIDTH,
                             highlightbackground=BORDER_COLOR)
        possFrame.pack(side=tk.LEFT,
                       anchor=tk.N,
                       expand=True,
                       fill="x",
                       padx=(10, 10))
        curViewId = df.viewId.cp()
        curViewId.fldClass = gf.FldEntry
        self.curViewKey = None
        self.curViewIdGf = curViewId.createFld(possFrame, noCap=True)
        self.curViewIdGf.mainFrame.pack()
        possFlds = [df.pathJs, df.pos]
        self.possTab = Table(self.parentWin, possFrame, df.pos, possFlds)
        self.possTab.mainFrame.pack()
        butFrame = tk.Frame(tabsFrame)
        butFrame.pack(side=tk.LEFT, anchor=tk.N)
        newButt = tk.Button(butFrame,
                            text="New",
                            command=self.posNew)
        newButt.pack()
        delButt = tk.Button(butFrame,
                            text="Delete",
                            command=self.posDel)
        delButt.pack()

        centFrame = tk.Frame(self.mainFrame)
        centFrame.pack(pady=(10, 10))
        saveButt = tk.Button(centFrame,
                             text="Save",
                             command=self.save)
        saveButt.pack(side=tk.LEFT)

        reloadButt = tk.Button(centFrame,
                               text="Reload",
                               command=self.reload)

        reloadButt.pack(side=tk.LEFT)
        bottomFrame = tk.Frame(self.mainFrame,
                               highlightthickness=BORDER_WIDTH,
                               highlightbackground=BORDER_COLOR
                               )
        bottomFrame.pack()
        title = tk.Label(bottomFrame, text=fd.displays.header)
        title.pack()
        dispFldDefs = [df.dispId, df.view, df.addr, df.dis]

        self.dispTab = Table(self.parentWin,
                             bottomFrame,
                             df.dispId,
                             dispFldDefs)
        self.dispTab.mainFrame.pack()

    def show(self,
             disps: dict,
             macs: dict,
             views: dict,
             paths: dict):
        self.oldDisps = disps
        self.oldMacs = macs
        self.oldViews = views
        self.paths = paths
        self.viewTab.show(views)
        curViewKey = self.curViewKey
        self.curViewKey = None
        self.curViewIdGf.clear()
        self.possTab.removeRows()
        jId = df.pathJs.fld.jId
        fldsJson = {jId: self.paths}
        self.possTab.setTabFldsJson(fldsJson)
        if curViewKey not in views.keys():
            if len(views) != 0:
                curViewKey = next(iter(views.keys()))
            else:
                curViewKey = None
        self.switchView(curViewKey)
        jId = df.view.fld.jId
        fldsJson = {jId: views}
        self.dispTab.setTabFldsJson(fldsJson)
        if len(disps) != 0:
            tab = jsonOuterJoin(disps, macs, self.macsDefaults)
            self.dispTab.show(tab)
        else:
            self.dispTab.removeRows()

    def switchView(self, newKey):
        if newKey != self.curViewKey:
            if self.curViewKey is not None:
                self.viewTab.setFldVal(df.viewId.fld,
                                       self.curViewKey,
                                       self.curViewIdGf.get())
                poss, _, _, _ = self.possTab.get()
                self.viewTab.setFldVal(df.poss.fld,
                                       self.curViewKey,
                                       poss)
            self.curViewKey = newKey
            if newKey is None:
                self.curViewIdGf.clear()
                self.possTab.removeRows()
            else:
                newViewId = self.viewTab.getFldVal(df.viewId.fld, newKey)
                newPoss = self.viewTab.getFldVal(df.poss.fld, newKey)
                self.curViewIdGf.show(newViewId)
                self.possTab.show(newPoss)

    def viewClick(self, key, fld, event):
        self.switchView(key)

    def pathsChg(self, pathsJson: dict):
        jId = df.pathJs.fld.jId
        fldsJson = {jId: self.paths}
        self.possTab.setTabFldsJson(fldsJson)

    def save(self):
        isOk = True
        isOk = isOk and self.dispTab.validate()
        isOk = isOk and self.viewTab.validate()
        if isOk:
            curKey = self.curViewKey
            for key in self.viewTab.getAllKeys():
                self.switchView(key)
                isOk = isOk and self.possTab.validate()
                if not isOk:
                    break
            if isOk:
                self.switchView(curKey)
        if isOk:
            tab = self.dispTab.get()[0]
            disps, macs = jsonOuterJsonSplit(tab, self.macsDefaults)
            views = self.viewTab.get()[0]
            errTxt, errPtrs = self.confValidateFn(disps, macs, views)
            if len(errPtrs) != 0:
                self.logger(errTxt)
            else:
                disps, macs, views = self.confSaveFn(disps, macs, views)
                self.show(disps, macs, views, self.paths)

    def reload(self):
        self.show(self.oldDisps, self.oldMacs, self.oldViews, self.paths)

    def posDel(self):
        if self.curViewKey is not None:
            key = self.curViewKey

            self.curViewKey = None
            self.curViewIdGf.clear()
            self.possTab.removeRows()

            self.viewTab.deleteRow(key)
            keys = self.viewTab.getAllKeys()
            if len(keys) != 0:
                self.switchView(keys[0])

    def posNew(self):
        key = self.viewTab.addNewRowWithKey()
        self.switchView(key)
