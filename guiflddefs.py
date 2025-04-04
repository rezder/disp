import guiflds as gf
from guiflds import Fld, FldLink
import tkinter as tk


class FldDef:
    def __init__(self,
                 fld: Fld,
                 width: int,
                 shortWidth: int,
                 fldClass,
                 isVis: bool = True,
                 options:  list | None = None,
                 linkDef: FldLink | None = None,
                 defaultVal=None,
                 isMan: bool = True,
                 isJson: bool = True
                 ):
        self.fld = fld
        self.width = width
        self.shortWidth = shortWidth
        self.fldClass = fldClass
        self.isVis = isVis
        self.options = options
        self.linkDef = linkDef
        self.defaultVal = defaultVal
        self.isMan = isMan
        self.isJson = isJson
        self.delkeys: list[str] = list()

    def __eq__(self, o):
        return o is self

    def cp(self):
        res = FldDef(self.fld,
                     self.width,
                     self.shortWidth,
                     self.fldClass,
                     isVis=self.isVis,
                     options=self.options,
                     linkDef=self.linkDef,
                     defaultVal=self.defaultVal,
                     isMan=self.isMan,
                     isJson=self.isJson)
        return res

    def createFld(self, parent: tk.Frame, isTab=False) -> gf.GuiFld:
        noCap = False
        width = self.width
        if isTab:
            noCap = True
            width = None
            lins = [gf.FldEntry, gf.FldOpt]
            if self.fldClass in lins:
                width = self.shortWidth

        guiFld = None
        if self.fldClass == gf.FldLabel:
            guiFld = gf.FldLabel(parent,
                                 self.fld,
                                 width,
                                 noCap=noCap,
                                 isMan=self.isMan,
                                 isJson=self.isJson,
                                 default=self.defaultVal)
        elif self.fldClass == gf.FldEntry:
            guiFld = gf.FldEntry(parent,
                                 self.fld,
                                 width,
                                 noCap=noCap,
                                 isMan=self.isMan,
                                 isJson=self.isJson,
                                 default=self.defaultVal)
        elif self.fldClass == gf.FldOpt:
            guiFld = gf.FldOpt(parent,
                               self.fld,
                               width,
                               self.options,
                               self.defaultVal,
                               noCap=noCap,
                               isJson=self.isJson,
                               linkDef=self.linkDef
                               )
        elif self.fldClass == gf.FldBool:
            guiFld = gf.FldBool(parent,
                                self.fld,
                                default=self.defaultVal,
                                noCap=noCap,
                                isJson=self.isJson,
                                linkDef=self.linkDef)
        return guiFld
