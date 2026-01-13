import tkinter as tk
from tkinter import messagebox

import guiflds as gf
from flds import fldsDict as fd
from guijsontable import Table
from flds import disp as df
from guiflds import jsonOuterJoin, jsonOuterJsonSplit
from gui import BORDER_COLOR, BORDER_WIDTH
import guimenu
import guiserial


class Disp:
    def __init__(self,
                 parentWin: tk.Toplevel,
                 parent: tk.Frame,
                 logger,
                 saveFn,
                 subPort: int,
                 dispIdValidateFn
                 ):
        self.parentWin = parentWin
        self.parent = parent
        self.logger = logger
        self.dispIdValidateFn = dispIdValidateFn
        self.confSaveFn = saveFn
        self.oldDisps = None
        self.oldMacs = None
        self.oldViews = None
        self.paths = None
        self.subPort = subPort
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
        self.dispTab.popUpMenuDisableItem("New Row")
        self.dispTab.popUpMenuDisableItem("Copy Row")
        self.dispTab.popUpMenuDisableItem("Paste Row")

        self.dispTab.mainFrame.pack()

        self.udpFram, self.udpWin, self.bleFrame, self.bleWin = createMenu(self.parentWin)
        self.bleGui = guiserial.Ble(self.bleWin,
                                    self.bleFrame,
                                    self.bleDispUpd,
                                    self.logger,
                                    self.dispIdValidateFn)
        self.udpGui = guiserial.Udp(self.udpWin,
                                    self.udpFram,
                                    self.udpDispUpd,
                                    self.logger,
                                    self.dispIdValidateFn)
        self.udpGui.mainFrame.pack()
        self.udpGui.show(self.subPort)
        self.bleGui.mainFrame.pack()
        self.bleGui.show()

    def settingsUpd(self, settJso: dict):
        self.udpGui.settingsUpd(settJso)

    def udpDispUpd(self, newId: str):
        isNew = True
        for key in self.dispTab.getAllKeys():
            id = self.dispTab.getFldVal(df.dispId.fld, key)
            if id == newId:
                isNew = False
                break
        if isNew:
            key = self.dispTab.addNewRowWithKey()
            self.dispTab.setFldVal(df.dispId.fld, key, newId)

    def bleDispUpd(self, newId: str, newAddr: str):
        idKey = None
        addrKey = None
        for key in self.dispTab.getAllKeys():
            id = self.dispTab.getFldVal(df.dispId.fld, key)
            addr = self.dispTab.getFldVal(df.addr.fld, key)
            if id == newId:
                idKey = key
            if addr == newAddr:
                addrKey = key
        if idKey is None and addrKey is None:
            key = self.dispTab.addNewRowWithKey()
            self.dispTab.setFldVal(df.dispId.fld, key, newId)
            self.dispTab.setFldVal(df.addr.fld, key, newAddr)
        else:
            if idKey is not None and addrKey is None:
                self.dispTab.setFldVal(df.addr.fld, idKey, newAddr)
            elif addrKey is not None and idKey is None:
                self.dispTab.setFldVal(df.dispId.fld, addrKey, newId)
            elif addrKey != idKey:
                errTxt = "Display id allready exist with different mac address"
                self.handleErrMsg(self.bleWin, errTxt)

    def handleErrMsg(self, win, errTxt: str):
        messagebox.showerror("Error", errTxt, parent=win)

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

    def switchView(self, newKey, isForce=False):
        if newKey != self.curViewKey or isForce:
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

    def pathsChg(self,
                 paths: dict,
                 alarms: dict,
                 bigs: dict):
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
                self.switchView(key, True)
                isOk = isOk and self.possTab.validate()
                if not isOk:
                    break
            if isOk:
                self.switchView(curKey)
        if isOk:
            tab = self.dispTab.get()[0]
            disps, macs = jsonOuterJsonSplit(tab, self.macsDefaults)
            views = self.viewTab.get()[0]
            errTxt, errPtrs = self.confSaveFn(disps, macs, views)
            if len(errPtrs) != 0:
                self.handleErrMsg(self.parentWin, errTxt)
            else:
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


def createMenu(win: tk.Toplevel) -> tuple[tk.Frame,
                                          tk.Toplevel,
                                          tk.Frame,
                                          tk.Toplevel]:
    menuBar = tk.Menu(win, tearoff=0)
    menuRegistor = tk.Menu(menuBar, tearoff=0)
    udpFrame, udpWin = guimenu.addWinMenuItem(win,
                                              menuRegistor,
                                              "Udp Display Registor",
                                              titleMenu="Udp")
    bleFrame, bleWin = guimenu.addWinMenuItem(win,
                                              menuRegistor,
                                              "Ble Display Registor",
                                              "Ble")
    menuBar.add_cascade(label="Registor Display",
                        menu=menuRegistor,
                        background="grey26")
    win.config(menu=menuBar)
    return udpFrame, udpWin, bleFrame, bleWin
