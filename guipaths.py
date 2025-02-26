import tkinter as tk
import guiflds as gf
import guijsondef as gdef
from guijsontable import Table
from flds import paths as pathFlds


class Path:
    def __init__(self,
                 parent: tk.Frame,
                 ):

        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.mainFrame.columnconfigure(1, weight=1)
        self.mainFrame.columnconfigure(0, weight=1)
        self.flds: dict[str, gf.Fld] = dict()
        self.fldDefs: list[gdef.GuiFld] = list()

        pathFld = gf.createFld(self.mainFrame, pathFlds.path)
        pathFld.mainFrame.grid(row=0, column=0, columnspan=2, sticky="w")
        self.flds[pathFld.id] = pathFld
        self.fldDefs.append(pathFlds.path)

        minPerFld = gf.createFld(self.mainFrame, pathFlds.minPer)
        minPerFld.mainFrame.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        self.flds[minPerFld.id] = minPerFld
        self.fldDefs.append(pathFlds.minPer)

        decFld = gf.createFld(self.mainFrame, pathFlds.dec)
        decFld.mainFrame.grid(row=2, column=0, sticky="ew", padx=(0, 5))
        self.flds[decFld.id] = decFld
        self.fldDefs.append(pathFlds.dec)

        labelFld = gf.createFld(self.mainFrame, pathFlds.label)
        labelFld.mainFrame.grid(row=2, column=1, sticky="ew")
        self.flds[labelFld.id] = labelFld
        #  label adde later to ksep order

        unitFld = gf.createFld(self.mainFrame, pathFlds.skUnit)
        unitFld.mainFrame.grid(row=3, column=0, sticky="ew", padx=(0, 5))
        self.flds[unitFld.id] = unitFld
        self.fldDefs.append(pathFlds.skUnit)

        dpUnitFld = gf.createFld(self.mainFrame, pathFlds.dpUnit)
        dpUnitFld.mainFrame.grid(row=3, column=1, sticky="ew")
        self.flds[dpUnitFld.id] = dpUnitFld
        self.fldDefs.append(pathFlds.dpUnit)

        # Adding label
        self.fldDefs.append(pathFlds.label)

        buffSizeFld = gf.createFld(self.mainFrame, pathFlds.bufSize)
        buffSizeFld.mainFrame.grid(row=4, column=0, sticky="ew", padx=(0, 5))
        self.flds[buffSizeFld.id] = buffSizeFld
        self.fldDefs.append(pathFlds.bufSize)

        buffFreqFld = gf.createFld(self.mainFrame, pathFlds.bufFreq)
        buffFreqFld.mainFrame.grid(row=4, column=1, sticky="ew")
        self.flds[buffFreqFld.id] = buffFreqFld
        self.fldDefs.append(pathFlds.bufFreq)

        minFld = gf.createFld(self.mainFrame, pathFlds.min)
        minFld.mainFrame.grid(row=5, column=0, sticky="ew", padx=(0, 5))
        self.flds[minFld.id] = minFld
        self.fldDefs.append(pathFlds.min)

        maxFld = gf.createFld(self.mainFrame, pathFlds.max)
        maxFld.mainFrame.grid(row=5, column=1, sticky="ew")
        self.flds[maxFld.id] = maxFld
        self.fldDefs.append(pathFlds.max)

        bigValFld = gf.createFld(self.mainFrame, pathFlds.bigVal)
        bigValFld.mainFrame.grid(row=6, column=0, sticky="ew", padx=(0, 5))
        self.flds[bigValFld.id] = bigValFld
        self.fldDefs.append(pathFlds.bigVal)

        bigUnitFld = gf.createFld(self.mainFrame, pathFlds.bigUnit)
        bigUnitFld.mainFrame.grid(row=6, column=1, sticky="ew")
        self.flds[bigUnitFld.id] = bigUnitFld
        self.fldDefs.append(pathFlds.bigUnit)

        bigDecFld = gf.createFld(self.mainFrame, pathFlds.bigDec)
        bigDecFld.mainFrame.grid(row=7, column=0, sticky="ew", padx=(0, 5))
        self.flds[bigDecFld.id] = bigDecFld
        self.fldDefs.append(pathFlds.bigDec)

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

    def getGuiFldDefs(self) -> list[gdef.GuiFld]:
        return self.fldDefs

    def getFlds(self) -> dict[str, gf.Fld]:
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

        sortGuiFldDef = None

        tabFlds: list[gdef.GuiFld] = list()
        for guiFldDef in self.pathGui.getGuiFldDefs():
            tabFld = guiFldDef.cp()
            tabFld.fldClass = gf.FldLabel
            if tabFld.jsonFld.isKey:
                sortGuiFldDef = tabFld
            tabFlds.append(tabFld)

        self.tabelGui = Table(self.tableFrame,
                              sortGuiFldDef,
                              self.rowClick,
                              tabFlds)
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
