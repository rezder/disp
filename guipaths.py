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
        self.flds = dict()
        self.phJson = "path"

        pathFld = gj.Fld(self.mainFrame,
                         "Path",
                         45,
                         True,
                         str,
                         str)
        pathFld.mainFrame.grid(row=0,
                               column=0,
                               columnspan=2,
                               sticky="w")
        self.flds[self.phJson] = pathFld

        minPerFld = gj.Fld(self.mainFrame,
                           "Min Period",
                           10,
                           True,
                           str,
                           int,
                           default=1000)
        minPerFld.mainFrame.grid(row=1,
                                 column=0,
                                 sticky="ew",
                                 padx=(0, 5))
        self.flds["minPeriod"] = minPerFld

        decFld = gj.Fld(self.mainFrame,
                        "Decimals",
                        10,
                        True,
                        str,
                        int,
                        default=0)
        decFld.mainFrame.grid(row=2, column=0, sticky="ew", padx=(0, 5))
        self.flds["decimals"] = decFld

        labelFld = gj.Fld(self.mainFrame,
                          "Label",
                          10,
                          True,
                          str,
                          str)
        labelFld.mainFrame.grid(row=2, column=1, sticky="ew")
        #  label adde later to keep order
        unitFld = gj.FldOpt(self.mainFrame,
                            "Sk Unit",
                            4,
                            units.m,
                            units.shortTxt,
                            units.noShort,
                            units.all())
        unitFld.mainFrame.grid(row=3, column=0, sticky="ew", padx=(0, 5))
        self.flds["units"] = unitFld

        dpUnitFld = gj.FldOpt(self.mainFrame,
                              "Tab Unit",
                              4,
                              units.m,
                              units.shortTxt,
                              units.noShort,
                              units.all())
        dpUnitFld.mainFrame.grid(row=3, column=1, sticky="ew")
        self.flds["dispUnits"] = dpUnitFld
        self.flds["label"] = labelFld

        buffSizeFld = gj.Fld(self.mainFrame,
                             "Buff size",
                             10,
                             True,
                             str,
                             int,
                             default=0)
        buffSizeFld.mainFrame.grid(row=4,
                                   column=0,
                                   sticky="ew",
                                   padx=(0, 5))
        self.flds["bufSize"] = buffSizeFld

        buffFreqFld = gj.Fld(self.mainFrame,
                             "Buff Freq",
                             10,
                             True,
                             str,
                             int,
                             default=0)
        buffFreqFld.mainFrame.grid(row=4, column=1, sticky="ew")
        self.flds["bufFreq"] = buffFreqFld

        bigValFld = gj.Fld(self.mainFrame,
                           "Big Value",
                           10,
                           False,
                           str,
                           int)
        bigValFld.mainFrame.grid(row=5,
                                 column=0,
                                 sticky="ew",
                                 padx=(0, 5))
        self.flds["largeValue"] = bigValFld

        bigRefFld = gj.Fld(self.mainFrame,
                           "Ref Path",
                           10,
                           False,
                           str,
                           gj.strJson)
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

    def jsonNameXFldHead(self) -> dict[str, str]:
        """
        :return: a dict with json Header link to form Header
        It includes path for the key header
        """
        dd = dict()
        for k, fld in self.flds.items():
            dd[k] = fld.getHeader()
        return dd

    def convIn(self) -> dict:
        """
        :return: a dict with json Header link conversion
        toStr
        """
        dd = dict()
        for k, fld in self.flds.items():
            dd[k] = fld.getToStr()
        return dd

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
        self.tabelGui = gj.Table(self.tableFrame,
                                 pathJson,
                                 self.phJson,
                                 self.phJson,
                                 self.pathGui.convIn(),
                                 self.rowClick,
                                 self.pathGui.jsonNameXFldHead())
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
