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
        self.flds["path"] = pathFld

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
        self.flds["path"].show(path)
        for k, fld in self.flds.items():
            if k in pathJson.keys():
                fld.show(pathJson[k])

    def get(self) -> tuple[str, dict]:
        path = None
        pathJson = dict()
        for k, fld in self.flds.items():
            if k == "path":
                path = self.flds["path"].get()
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
            isOk = isOk or fld.validate()
        return isOk

    def jsonNameXFldHead(self) -> dict[str, str]:
        """
        :return: a dict with json Header link to form Header
        It includes path for the key header
        """
        dd = dict()
        for k, fld in self.flds.items():
            dd[k] = fld.getHeader()
        return dd
