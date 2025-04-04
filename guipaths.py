import tkinter as tk
import guiflds as gf
from guijsontable import Table
from flds import paths as pathFlds
from guiflddefs import FldDef
from guimenu import addWinMenuItem


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
            if guiFld.fld.isKey:
                guiFld.show(path)
            else:
                if guiFld.id in pathJson.keys():
                    guiFld.show(pathJson[guiFld.id])

    def get(self) -> tuple[str, dict]:
        path = None
        pathJson = dict()
        for guiFld in self.flds.values():
            if guiFld.fld.isKey:
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
                 deletePathCb,
                 savePathCb
                 ):
        self.parentWin = parentWin
        self.subPathUpdList = list()
        self.parent = parent
        self.logger = logger
        self.deletePathCb = deletePathCb
        self.savePathCb = savePathCb
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
            if tabFld.fld.isKey:
                sortGuiFldDef = tabFld
            tabFlds.append(tabFld)

        self.tabelGui = Table(self.parentWin,
                              self.tableFrame,
                              sortGuiFldDef,
                              self.rowClick,
                              tabFlds,
                              isPopUp=False)
        self.tabelGui.mainFrame.pack()
        self.alarmsGui, self.bigsGui = self.creatMenu(self.parentWin)

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
        # TODO add save and reload menu commands
        # savecb must return isOk,list of (key,errFlds),
        # errorTxt and tPathsJson
        # only validation both min and max cant be empty.
        # table and fld validation should take care of the rest
        # if that is untrusted the validation should be repeated.
        alarmsFlds = [pathFlds.pathJs, pathFlds.min, pathFlds.max]
        alarmsTableGui = Table(
            win,
            alarmsFrame,
            pathFlds.path,
            None,
            alarmsFlds)
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
            None,
            bigsFlds)
        bigsTableGui.mainFrame.pack()
        win.config(menu=menuBar)

        return alarmsTableGui, bigsTableGui

    def show(self, tPathsJson):
        paths, alarms, bigs = tPathsJson
        self.pathJsonOld = paths
        self.alarmsJsonOld = alarms
        self.bigsJsonOld = bigs
        self.tabelGui.show(paths)
        jId = pathFlds.pathJs.fld.jId
        fldsJson = {jId: paths}
        self.alarmsGui.setTabFldsJson(fldsJson)
        self.alarmsGui.show(alarms)
        self.bigsGui.setTabFldsJson(fldsJson)
        self.bigsGui.show(bigs)

    def rowClick(self, path: str, head: str):
        self.pathGui.show(path, self.pathJsonOld[path])

    def save(self):
        if self.pathGui.validateFlds():
            path, itemJson = self.pathGui.get()
            if path in self.pathJsonOld.keys():
                txt = "Modifying path: {}"
                self.logger(txt.format(path))
            else:
                txt = "Creating new path: {}"
                self.logger(txt.format(path))
            #  TODO save and delete need to include alarms and bigs
            # maybe with a button on each tabel
            # delte row and new row is also missing
            isOk, errFlds, errTxt, tPathsJson = self.savePathCb(path, itemJson)
            if isOk:
                self.clear()
                self.show(tPathsJson)
                self.execPathUdp(tPathsJson)
            else:
                for head in errFlds:
                    self.pathGui.setErrorFld(head)

                txt = "Error saving path: {}\nError: {}"
                self.logger(txt.format(path, errTxt))

    def delete(self):
        path, itemJson = self.pathGui.get()
        if path in self.pathJsonOld.keys():
            isOk, errTxt, tPathsJson = self.deletePathCb(path)

            if isOk:
                self.clear()
                self.show(tPathsJson)
                self.execPathUdp(tPathsJson)
                self.logger("Path: {} deleted".format(path))
            else:
                self.pathGui.setErrorFld(pathFlds.path.fld.jId)
                txt = "Error deleting path: {}:\n{}"
                self.logger(txt.format(path, errTxt))
        else:
            self.logger("Nothing deleted path does not exist")

    def clear(self):
        self.pathGui.clear()

    def subScribePathUpd(self, fn):
        self.subPathUpdList.append(fn)

    def execPathUdp(self, tPathJson: tuple[dict, dict, dict]):
        for f in self.subPathUpdList:
            f(tPathJson)

    def serverOn(self, isOn: bool):
        if isOn:
            self.saveButt.config(state=tk.DISABLED)
            self.delButt.config(state=tk.DISABLED)
        else:
            self.saveButt.config(state=tk.NORMAL)
            self.delButt.config(state=tk.NORMAL)
