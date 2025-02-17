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
        self.pathFld = gj.Fld(self.mainFrame,
                              "Path",
                              45,
                              str,
                              str)
        self.pathFld.mainFrame.grid(row=0,
                                    column=0,
                                    columnspan=2,
                                    sticky="w")
        self.minPerFld = gj.Fld(self.mainFrame,
                                "Min Period",
                                10,
                                str,
                                str)
        self.minPerFld.mainFrame.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        self.decFld = gj.Fld(self.mainFrame,
                             "Decimals",
                             10,
                             str,
                             str)
        self.decFld.mainFrame.grid(row=2, column=0, sticky="ew", padx=(0, 5))
        self.labelFld = gj.Fld(self.mainFrame,
                               "Sk Units",
                               10,
                               str,
                               str)
        self.labelFld.mainFrame.grid(row=2, column=1, sticky="ew")

        self.unitFld = gj.FldOpt(self.mainFrame,
                                 "Sk unit",
                                 4,
                                 units.m,
                                 units.shortTxt,
                                 units.noShort,
                                 units.all())
        self.unitFld.mainFrame.grid(row=3, column=0, sticky="ew", padx=(0, 5))
        self.dpUnitFld = gj.FldOpt(self.mainFrame,
                                   "Display Unit",
                                   4,
                                   units.m,
                                   units.shortTxt,
                                   units.noShort,
                                   units.all())
        self.dpUnitFld.mainFrame.grid(row=3, column=1, sticky="ew")
        self.buffSizeFld = gj.Fld(self.mainFrame,
                                  "Buffer size",
                                  10,
                                  str,
                                  int)
        self.buffSizeFld.mainFrame.grid(row=4, column=0, sticky="ew", padx=(0, 5))
        self.buffFreqFld = gj.Fld(self.mainFrame,
                                  "Buffer Frequenz",
                                  10,
                                  str,
                                  int)
        self.buffFreqFld.mainFrame.grid(row=4, column=1, sticky="ew")
        self.bigValFld = gj.Fld(self.mainFrame,
                                "Big Value",
                                10,
                                str,
                                int)
        self.bigValFld.mainFrame.grid(row=5, column=0, sticky="ew", padx=(0, 5))
        self.bigRefFld = gj.Fld(self.mainFrame,
                                "Ref Path",
                                10,
                                str,
                                str)
        self.bigRefFld.mainFrame.grid(row=5, column=1, sticky="ew")

    def show(self, path: str, pathJson: dict):
        self.pathFld.show(path)
        fld = "minPeriod"
        if fld in pathJson.keys():
            self.minPerFld.show(pathJson[fld])
        fld = "decimals"
        if fld in pathJson.keys():
            self.decFld.show(pathJson[fld])
        fld = "label"
        if fld in pathJson.keys():
            self.labelFld.show(pathJson[fld])
        fld = "bufSize"
        if fld in pathJson.keys():
            self.buffSizeFld.show(pathJson[fld])
        fld = "buffFreq"
        if fld in pathJson.keys():
            self.buffFreqFld.show(pathJson[fld])
        fld = "units"
        if fld in pathJson.keys():
            self.unitFld.show(pathJson["units"])
        fld = "dispUnits"
        if fld in pathJson.keys():
            self.dpUnitFld.show(pathJson[fld])
        fld = "largeValue"
        if fld in pathJson.keys():
            self.bigValFld.show(pathJson[fld])
        fld = "largePath"
        if fld in pathJson.keys():
            self.bigRefFld.show(pathJson[fld])
