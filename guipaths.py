import tkinter as tk

import guiflds as gf
from guijsontable import Table
from flds import paths as pathFlds
from guiflddefs import FldDef
from guimenu import addWinMenuItem
from guiflds import Fld


class Path:
    def __init__(self,
                 parent: tk.Frame,
                 ):

        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.mainFrame.columnconfigure(1, weight=1)
        self.mainFrame.columnconfigure(0, weight=1)
        self.flds: dict[str, gf.GuiFld] = dict()
        self.fldDefs: list[FldDef] = list()

        pathFld = pathFlds.path.createFld(self.mainFrame)
        pathFld.mainFrame.grid(row=0, column=0, columnspan=2, sticky="w")
        self.flds[pathFld.id] = pathFld
        self.fldDefs.append(pathFlds.path)

        minPerFld = pathFlds.minPer.createFld(self.mainFrame)
        minPerFld.mainFrame.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        self.flds[minPerFld.id] = minPerFld
        self.fldDefs.append(pathFlds.minPer)

        decFld = pathFlds.dec.createFld(self.mainFrame)
        decFld.mainFrame.grid(row=2, column=0, sticky="ew", padx=(0, 5))
        self.flds[decFld.id] = decFld
        self.fldDefs.append(pathFlds.dec)

        labelFld = pathFlds.label.createFld(self.mainFrame)
        labelFld.mainFrame.grid(row=2, column=1, sticky="ew")
        self.flds[labelFld.id] = labelFld
        #  label adde later to ksep order

        unitFld = pathFlds.skUnit.createFld(self.mainFrame)
        unitFld.mainFrame.grid(row=3, column=0, sticky="ew", padx=(0, 5))
        self.flds[unitFld.id] = unitFld
        self.fldDefs.append(pathFlds.skUnit)

        dpUnitFld = pathFlds.dpUnit.createFld(self.mainFrame)
        dpUnitFld.mainFrame.grid(row=3, column=1, sticky="ew")
        self.flds[dpUnitFld.id] = dpUnitFld
        self.fldDefs.append(pathFlds.dpUnit)

        # Adding label
        self.fldDefs.append(pathFlds.label)

        buffSizeFld = pathFlds.bufSize.createFld(self.mainFrame)
        buffSizeFld.mainFrame.grid(row=4, column=0, sticky="ew", padx=(0, 5))
        self.flds[buffSizeFld.id] = buffSizeFld
        self.fldDefs.append(pathFlds.bufSize)

        buffFreqFld = pathFlds.bufFreq.createFld(self.mainFrame)
        buffFreqFld.mainFrame.grid(row=4, column=1, sticky="ew")
        self.flds[buffFreqFld.id] = buffFreqFld
        self.fldDefs.append(pathFlds.bufFreq)

    def show(self, path: str, pathJson: dict):
        self.clear()
        for guiFld in self.flds.values():
            if guiFld.isKey:
                guiFld.show(path)
            else:
                if guiFld.id in pathJson.keys():
                    guiFld.show(pathJson[guiFld.id])

    def get(self) -> tuple[str, dict]:
        path = None
        pathJson = dict()
        for guiFld in self.flds.values():
            if guiFld.isKey:
                path = guiFld.get()
            else:
                try:
                    pathJson[guiFld.id] = guiFld.get()
                except ValueError:
                    pass
                    # removes optional flds with no content
        return (path, pathJson)

    def clear(self):
        for guiFld in self.flds.values():
            guiFld.clear()

    def validateFlds(self) -> bool:
        isOk = True
        for guiFld in self.flds.values():
            fldOk = guiFld.validate()
            if not fldOk:
                print(guiFld.fld.header)
            isOk = isOk and fldOk
        return isOk

    def setErrorFld(self, jId: str):
        self.flds[jId].setError(True)

    def getGuiFldDefs(self) -> list[FldDef]:
        return self.fldDefs

    def getFlds(self) -> dict[str, gf.GuiFld]:
        return self.flds


class Paths:
    def __init__(self,
                 parentWin: tk.Toplevel,
                 parent: tk.Frame,
                 logger,
                 savePathsFn
                 ):
        self.parentWin = parentWin
        self.subPathUpdList = list()
        self.parent = parent
        self.logger = logger
        self.savePathsFn = savePathsFn
        self.mainFrame = tk.Frame(self.parent)
        self.topFrame = tk.Frame(self.mainFrame)
        self.topFrame.pack()
        self.itemFrame = tk.Frame(self.topFrame)
        self.tableFrame = tk.Frame(self.mainFrame)
        self.buttFrame = tk.Frame(self.topFrame)

        self.itemFrame.pack(side=tk.LEFT)
        self.buttFrame.pack(side=tk.LEFT, padx=(10, 0))
        self.tableFrame.pack(side=tk.BOTTOM)

        self.pathGui = Path(self.itemFrame)
        self.pathGui.mainFrame.pack()

        sortGuiFldDef = None

        tabFlds: list[FldDef] = list()
        for guiFldDef in self.pathGui.getGuiFldDefs():
            tabFld = guiFldDef.cp()
            tabFld.fldClass = gf.FldLabel
            if tabFld.isKey:
                sortGuiFldDef = tabFld
            tabFlds.append(tabFld)

        self.pathsTab = Table(self.parentWin,
                              self.tableFrame,
                              sortGuiFldDef,
                              tabFlds,
                              isPopUp=False)
        self.pathsTab.bindAllVisFields("<ButtonRelease-1>", self.rowClick)
        self.pathsTab.mainFrame.pack()
        alarmsTab, bigsTab = self.creatMenu(self.parentWin)
        self.alarmsTab = alarmsTab
        self.bigsTab: Table = bigsTab

        self.saveButt = tk.Button(self.buttFrame,
                                  text="Save",
                                  command=self.save)
        self.saveButt.pack(anchor=tk.W)

        self.clearButt = tk.Button(self.buttFrame,
                                   text="Clear",
                                   command=self.clear)
        self.clearButt.pack(anchor=tk.W)

        self.delButt = tk.Button(self.buttFrame,
                                 text="Delete",
                                 command=self.delete)
        self.delButt.pack(anchor=tk.W)

    def creatMenu(self, win: tk.Toplevel) -> tuple[Table, Table]:
        """
        Creates the menu with alarms and bigs
        :returns:
        - Alarms table gui
        - Bigs table gui
        """
        menuBar = tk.Menu(win, tearoff=0)
        alarmsFrame, _ = addWinMenuItem(win,
                                        menuBar,
                                        "Alarms")
        alarmsFlds = [pathFlds.pathJs, pathFlds.min, pathFlds.max]
        alarmsTableGui = Table(
            win,
            alarmsFrame,
            pathFlds.pathJs,
            alarmsFlds,
            saveFn=self.saveAlarms,
            reloadFn=self.reloadAlarms
        )
        alarmsTableGui.mainFrame.pack()
        bigsFrame, _ = addWinMenuItem(win,
                                      menuBar,
                                      "Bigs")
        bigsFlds = [pathFlds.pathJs, pathFlds.limit,
                    pathFlds.dpUnit, pathFlds.dec]

        bigsTableGui = Table(
            win,
            bigsFrame,
            pathFlds.pathJs,
            bigsFlds,
            saveFn=self.saveBigs,
            reloadFn=self.reloadBigs)

        bigsTableGui.mainFrame.pack()
        win.config(menu=menuBar)

        return alarmsTableGui, bigsTableGui

    def show(self, pathsJso, alarmsJso, bigsJso):
        self.pathsJsoOld = pathsJso
        self.alarmsJsonOld = alarmsJso
        self.bigsJsonOld = bigsJso
        self.pathsTab.show(pathsJso)
        jId = pathFlds.pathJs.fld.jId
        fldsJson = {jId: pathsJso}
        self.alarmsTab.setTabFldsJson(fldsJson)
        self.alarmsTab.show(alarmsJso)
        self.bigsTab.setTabFldsJson(fldsJson)
        self.bigsTab.show(bigsJso)

    def rowClick(self, path: str, fld: Fld, event):
        self.pathGui.show(path, self.pathsJsoOld[path])

    def saveAlarms(self):
        isOk = True
        isOk = isOk and self.alarmsTab.validate()
        if isOk:
            alarmsJso = self.alarmsTab.get()[0]
            bigsJso = self.bigsJsonOld
            pathsJso = self.pathsJsoOld
            errTxt, errPtrs = self.savePathsFn(pathsJso,
                                               alarmsJso,
                                               bigsJso)
            if len(errPtrs) != 0:
                self.logger(errTxt)
            else:
                self.alarmsTab.show(alarmsJso)
                self.alarmsJsonOld = alarmsJso
                self.execPathUdp(pathsJso, alarmsJso, bigsJso)

    def reloadAlarms(self):
        self.alarmsTab.show(self.alarmsJsonOld)

    def saveBigs(self):
        isOk = True
        isOk = isOk and self.bigsTab.validate()
        if isOk:
            alarmsJso = self.alarmsJsonOld
            bigsJso = self.bigsTab.get()[0]
            pathsJso = self.pathsJsoOld
            errTxt, errPtrs = self.savePathsFn(pathsJso,
                                               alarmsJso,
                                               bigsJso)
            if len(errPtrs) != 0:
                self.logger(errTxt)
            else:
                self.bigsTab.show(bigsJso)
                self.bigsJsonOld = bigsJso
                self.execPathUdp(pathsJso, alarmsJso, bigsJso)

    def reloadBigs(self):
        self.bigsTab.show(self.bigsJsonOld)

    def updatePath(self, isDel=False):
        if self.pathGui.validateFlds():
            pathId, pathJso = self.pathGui.get()
            newPaths = self.pathsTab.get()[0]
            isClear = False
            if pathId in self.pathsJsoOld.keys():
                txt = "Modifying path: {}"
                if isDel:
                    txt = "Deleting path: {}"
                    newPaths.pop(pathId)
                else:
                    newPaths[pathId] = pathJso
                self.logger(txt.format(pathId))
            else:
                txt = "Creating new path: {}"
                if isDel:
                    txt = "Path: {} does not exist"
                    isClear = True
                else:
                    newPaths[pathId] = pathJso
                self.logger(txt.format(pathId))
            if isClear:
                self.pathGui.clear()
            else:
                alarmsJso = self.alarmsJsonOld
                bigsJso = self.bigsJsonOld
                errTxt, errPtrs = self.savePathsFn(newPaths,
                                                   alarmsJso,
                                                   bigsJso)
                if len(errPtrs) != 0:
                    self.logger(errTxt)
                else:
                    self.show(newPaths, alarmsJso, bigsJso)
                    self.execPathUdp(newPaths, alarmsJso, bigsJso)

    def save(self):
        self.updatePath()

    def delete(self):
        self.updatePath(True)

    def clear(self):
        self.pathGui.clear()

    def subScribePathUpd(self, fn):
        self.subPathUpdList.append(fn)

    def execPathUdp(self, pathsJso, alarmsJso, bigsJso):
        for f in self.subPathUpdList:
            f(pathsJso, alarmsJso, bigsJso)
