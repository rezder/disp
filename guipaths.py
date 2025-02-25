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
        fldDef = gj.FldDef("path",
                           "Path",
                           str,
                           str,
                           "w",
                           isKey=True)
        pathFld = gj.FldEntry(self.mainFrame, fldDef, 45)
        pathFld.mainFrame.grid(row=0,
                               column=0,
                               columnspan=2,
                               sticky="w")
        self.flds[pathFld.id] = pathFld
        fldDef = gj.FldDef("minPeriod",
                           "Min Period",
                           str,
                           int,
                           "e"
                           )
        minPerFld = gj.FldEntry(self.mainFrame, fldDef, 10, default=1000)
        minPerFld.mainFrame.grid(row=1,
                                 column=0,
                                 sticky="ew",
                                 padx=(0, 5))
        self.flds[minPerFld.id] = minPerFld

        fldDef = gj.FldDef("decimals",
                           "Decimals",
                           str,
                           int,
                           "e"
                           )
        decFld = gj.FldEntry(self.mainFrame, fldDef, 10, default=0)
        decFld.mainFrame.grid(row=2, column=0, sticky="ew", padx=(0, 5))
        self.flds[decFld.id] = decFld

        fldDef = gj.FldDef("label",
                           "Label",
                           str,
                           str,
                           "w")
        labelFld = gj.FldEntry(self.mainFrame, fldDef, 10)
        labelFld.mainFrame.grid(row=2, column=1, sticky="ew")
        #  label adde later to ksep order
        fldDef = gj.FldDef("units",
                           "Sk Unit",
                           units.shortTxt,
                           units.noShort,
                           "w"
                           )
        unitFld = gj.FldOpt(self.mainFrame, fldDef, 4, units.all(), units.m)

        unitFld.mainFrame.grid(row=3, column=0, sticky="ew", padx=(0, 5))
        self.flds[unitFld.id] = unitFld

        fldDef = gj.FldDef("dispUnits",
                           "Tab Unit",
                           units.shortTxt,
                           units.noShort,
                           "w"
                           )

        dpUnitFld = gj.FldOpt(self.mainFrame, fldDef, 4, units.all(), units.m)
        dpUnitFld.mainFrame.grid(row=3, column=1, sticky="ew")
        self.flds[dpUnitFld.id] = dpUnitFld

        self.flds[labelFld.id] = labelFld

        fldDef = gj.FldDef("bufSize",
                           "Buff size",
                           str,
                           int,
                           "e"
                           )
        buffSizeFld = gj.FldEntry(self.mainFrame, fldDef, 10, default=0)
        buffSizeFld.mainFrame.grid(row=4,
                                   column=0,
                                   sticky="ew",
                                   padx=(0, 5))
        self.flds[buffSizeFld.id] = buffSizeFld

        fldDef = gj.FldDef("bufFreq",
                           "Buff Freq",
                           str,
                           int,
                           "e"
                           )
        buffFreqFld = gj.FldEntry(self.mainFrame, fldDef, 10, default=0)
        buffFreqFld.mainFrame.grid(row=4, column=1, sticky="ew")
        self.flds[buffFreqFld.id] = buffFreqFld

        fldDef = gj.FldDef("min",
                           "Min Val",
                           str,
                           float,
                           "e")
        minFld = gj.FldEntry(self.mainFrame, fldDef, 10, isMan=False)
        minFld.mainFrame.grid(row=5, column=0, sticky="ew", padx=(0, 5))
        self.flds[minFld.id] = minFld

        fldDef = gj.FldDef("max",
                           "Max Val",
                           str,
                           float,
                           "e")
        maxFld = gj.FldEntry(self.mainFrame, fldDef, 10, isMan=False)
        maxFld.mainFrame.grid(row=5, column=1, sticky="ew")
        self.flds[maxFld.id] = maxFld

        fldDef = gj.FldDef("bigValue",
                           "Big Value",
                           str,
                           int,
                           "e")
        bigValFld = gj.FldEntry(self.mainFrame, fldDef, 10, isMan=False)
        bigValFld.mainFrame.grid(row=6,
                                 column=0,
                                 sticky="ew",
                                 padx=(0, 5))
        self.flds[bigValFld.id] = bigValFld

        fldDef = gj.FldDef("bigDispUnit",
                           "Big Units",
                           units.shortTxt,
                           units.noShort,
                           "w"
                           )

        bigUnitFld = gj.FldOpt(self.mainFrame, fldDef, 4, units.all(), units.m)
        bigUnitFld.mainFrame.grid(row=6, column=1, sticky="ew")
        self.flds[bigUnitFld.id] = bigUnitFld

        fldDef = gj.FldDef("bigDecimals",
                           "Big Decimals",
                           str,
                           int,
                           "e"
                           )
        bigDecFld = gj.FldEntry(self.mainFrame, fldDef, 10, isMan=False)
        bigDecFld.mainFrame.grid(row=7, column=0, sticky="ew", padx=(0, 5))
        self.flds[bigDecFld.id] = bigDecFld

    def show(self, path: str, pathJson: dict):
        self.clear()
        for fld in self.flds.values():
            if fld.fldDef.isKey:
                fld.show(path)
            else:
                if fld.id in pathJson.keys():
                    fld.show(pathJson[fld.id])

    def get(self) -> tuple[str, dict]:
        path = None
        pathJson = dict()
        bigFldIsEmpty = True  # Nasty hack as opt fld is mandatry
        for fld in self.flds.values():
            if fld.fldDef.isKey:
                path = fld.get()
            else:
                try:
                    pathJson[fld.id] = fld.get()
                except ValueError:
                    if fld.id == "bigValue":
                        bigFldIsEmpty = True
                    # removes optional flds with no content
        if bigFldIsEmpty:
            del pathJson["bigDispUnit"]
        return (path, pathJson)

    def clear(self):
        for fld in self.flds.values():
            fld.clear()

    def validateFlds(self) -> bool:
        isOk = True
        for fld in self.flds.values():
            fldOk = fld.validate()
            if not fldOk:
                print(fld.fldDef.header)
            isOk = isOk and fldOk
        return isOk

    def setErrorFld(self, jsonHead: str):
        self.flds[jsonHead].setError(True)

    def getFldDefs(self) -> list[gj.FldDef]:
        defs = list()
        for fld in self.flds.values():
            defs.append(fld.fldDef)
        return defs

    def getFlds(self) -> dict[str, gj.Fld]:
        return self.flds


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
        self.keyFldDef = None
        for fldDef in self.pathGui.getFldDefs():
            if fldDef.isKey:
                self.keyFldDef = fldDef
                break

        self.tabelGui = gj.Table(self.tableFrame,
                                 len(pathJson),
                                 self.keyFldDef,
                                 self.rowClick,
                                 self.pathGui.getFldDefs())
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
                self.logger("Path: {} deleted".format(path))
            else:
                self.pathGui.setErrorFld(self.phJson)
                txt = "Error deleting path: {}:\n{}"
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
            self.delButt.config(state=tk.DISABLED)
        else:
            self.saveButt.config(state=tk.NORMAL)
            self.delButt.config(state=tk.NORMAL)
