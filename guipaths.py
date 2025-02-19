import tkinter as tk
import guijson as gj
import units


class Path:
    def __init__(self,
                 parent: tk.Frame,
                 ):

        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.mainFrame.columnconfigure(1, weight=1)
        self.mainFrame.columnconfigure(0, weight=1)
        self.flds: dict[str, gj.Fld] = dict()
        self.phJson = "path"
        fldDef = gj.FldDef("Path",
                           45,
                           True,
                           str,
                           str,
                           "w")
        pathFld = gj.FldEntry(self.mainFrame, fldDef)
        pathFld.mainFrame.grid(row=0,
                               column=0,
                               columnspan=2,
                               sticky="w")
        self.flds[self.phJson] = pathFld
        fldDef = gj.FldDef("Min Period",
                           10,
                           True,
                           str,
                           int,
                           "e",
                           default=1000)
        minPerFld = gj.FldEntry(self.mainFrame, fldDef)
        minPerFld.mainFrame.grid(row=1,
                                 column=0,
                                 sticky="ew",
                                 padx=(0, 5))
        self.flds["minPeriod"] = minPerFld

        fldDef = gj.FldDef("Decimals",
                           10,
                           True,
                           str,
                           int,
                           "e",
                           default=0)
        decFld = gj.FldEntry(self.mainFrame, fldDef)
        decFld.mainFrame.grid(row=2, column=0, sticky="ew", padx=(0, 5))
        self.flds["decimals"] = decFld

        fldDef = gj.FldDef("Label",
                           10,
                           True,
                           str,
                           str,
                           "w")
        labelFld = gj.FldEntry(self.mainFrame, fldDef)
        labelFld.mainFrame.grid(row=2, column=1, sticky="ew")
        #  label adde later to keep order
        fldDef = gj.FldDef("Sk Unit",
                           4,
                           True,
                           units.shortTxt,
                           units.noShort,
                           "w",
                           units.m)
        unitFld = gj.FldOpt(self.mainFrame, fldDef, units.all())

        unitFld.mainFrame.grid(row=3, column=0, sticky="ew", padx=(0, 5))
        self.flds["units"] = unitFld

        fldDef = gj.FldDef("Tab Unit",
                           4,
                           True,
                           units.shortTxt,
                           units.noShort,
                           "w",
                           units.m)

        dpUnitFld = gj.FldOpt(self.mainFrame, fldDef, units.all())
        dpUnitFld.mainFrame.grid(row=3, column=1, sticky="ew")
        self.flds["dispUnits"] = dpUnitFld

        self.flds["label"] = labelFld
        fldDef = gj.FldDef("Buff size",
                           10,
                           True,
                           str,
                           int,
                           "e",
                           default=0)
        buffSizeFld = gj.FldEntry(self.mainFrame, fldDef)
        buffSizeFld.mainFrame.grid(row=4,
                                   column=0,
                                   sticky="ew",
                                   padx=(0, 5))
        self.flds["bufSize"] = buffSizeFld

        fldDef = gj.FldDef("Buff Freq",
                           10,
                           True,
                           str,
                           int,
                           "e",
                           default=0)
        buffFreqFld = gj.FldEntry(self.mainFrame, fldDef)
        buffFreqFld.mainFrame.grid(row=4, column=1, sticky="ew")
        self.flds["bufFreq"] = buffFreqFld

        fldDef = gj.FldDef("Big Value",
                           10,
                           False,
                           str,
                           int,
                           "e")
        bigValFld = gj.FldEntry(self.mainFrame, fldDef)
        bigValFld.mainFrame.grid(row=5,
                                 column=0,
                                 sticky="ew",
                                 padx=(0, 5))
        self.flds["largeValue"] = bigValFld

        fldDef = gj.FldDef("Ref Path",
                           10,
                           False,
                           str,
                           gj.strJson,
                           "w"
                           )
        bigRefFld = gj.FldEntry(self.mainFrame, fldDef)
        bigRefFld.mainFrame.grid(row=5, column=1, sticky="ew")
        self.flds["largePath"] = bigRefFld

    def show(self, path: str, pathJson: dict):
        self.flds[self.phJson].show(path)
        for k, fld in self.flds.items():
            if k in pathJson.keys():
                fld.show(pathJson[k])

    def get(self) -> tuple[str, dict]:
        path = None
        pathJson = dict()
        for k, fld in self.flds.items():
            if k == self.phJson:
                path = self.flds[k].get()
            else:
                try:
                    pathJson[k] = fld.get()
                except ValueError:
                    pass
        return (path, pathJson)

    def clear(self):
        for fld in self.flds.values():
            fld.clear()

    def validateFlds(self) -> bool:
        isOk = True
        for fld in self.flds.values():
            fldOk = fld.validate()
            isOk = isOk and fldOk
        return isOk

    def setErrorFld(self, jsonHead: str):
        self.flds[jsonHead].setError(True)

    def getFlds(self) -> dict[str, gj.Fld]:
        return self.flds

    def getPhJson(self):
        return self.phJson


class Paths:
    def __init__(self,
                 parent: tk.Frame,
                 pathJson: dict,
                 logger,
                 deleteCb,
                 saveCb
                 ):
        self.phJson = "path"
        self.subPathUpdList = list()
        self.parent = parent
        self.logger = logger
        self.deleteCb = deleteCb
        self.saveCb = saveCb
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
        fldDefs: dict[str, gj.FldDef] = dict()
        for path, fld in self.pathGui.flds.items():
            fldDefs[path] = fld.fldDef

        self.tabelGui = gj.Table(self.tableFrame,
                                 pathJson,
                                 self.phJson,
                                 self.phJson,
                                 self.rowClick,
                                 fldDefs)
        self.tabelGui.mainFrame.pack()

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

    def show(self, pathJson):
        self.pathJsonOld = pathJson
        self.tabelGui.show(pathJson)

    def rowClick(self, path: str, head: str):
        self.pathGui.clear()
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
            isOk, errFlds, errTxt, pathJson = self.saveCb(path, itemJson)
            if isOk:
                self.clear()
                self.show(pathJson)
                self.execPathUdp(pathJson)
            else:
                for head in errFlds:
                    print(head)
                    self.pathGui.setErrorFld(head)

                txt = "Error saving path: {}\nError: {}"
                self.logger(txt.format(path, errTxt))

    def delete(self):
        path, itemJson = self.pathGui.get()
        if path in self.pathJsonOld.keys():
            isOk, errTxt, pathJson = self.deleteCb(path)
            if isOk:
                self.clear()
                self.show(pathJson)
                self.execPathUdp(pathJson)
            else:
                self.pathGui.setErrorFld(self.phJson)
                txt = "Error deleting path: {}\n Error: {}"
                self.logger(txt.format(path, errTxt))
        else:
            self.logger("Nothing deleted path does not exist")

    def clear(self):
        self.pathGui.clear()

    def subScribePathUpd(self, fn):
        self.subPathUpdList.append(fn)

    def execPathUdp(self, pathJson: dict):
        for f in self.subPathUpdList:
            f(pathJson)

    def serverOn(self, isOn: bool):
        if isOn:
            self.saveButt.config(state=tk.DISABLED)
            self.delButt.config(state=tk.normal)
        else:
            self.saveButt.config(state=tk.normal)
            self.delButt.config(state=tk.normal)
