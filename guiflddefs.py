from flds import Fld
from flds import flds
import guiflds as gf
import tkinter as tk
import units


class FldDef:
    def __init__(self,
                 fld: Fld,
                 width: int,
                 shortWidth: int,
                 fldClass,
                 isVis: bool = True,
                 options:  list | None = None,
                 optJson: dict | None = None,
                 optJsonHead: str | None = None,
                 defaultVal=None,
                 isMan: bool = True,
                 isKey: bool = False,
                 isJson: bool = True
                 ):
        self.fld = fld
        self.width = width
        self.shortWidth = shortWidth
        self.fldClass = fldClass
        self.isVis = isVis
        self.options = options
        self.optJson = optJson
        self.optJsonHead = optJsonHead
        self.defaultVal = defaultVal
        self.isMan = isMan
        self.isKey = isKey
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
                     optJson=self.optJson,
                     optJsonHead=self.optJsonHead,
                     defaultVal=self.defaultVal,
                     isMan=self.isMan,
                     isKey=self.isKey,
                     isJson=self.isJson)
        return res

    def createFld(self, parent: tk.Frame, isTab=False) -> gf.GuiFld:
        noCap = False
        width = self.width
        if isTab:
            noCap = True
            width = None
            lins = [gf.FldEntry, gf.FldOpt, gf.FldOptJson]
            if self.fldClass in lins:
                width = self.shortWidth

        guiFld = None
        if self.fldClass == gf.FldLabel:
            guiFld = gf.FldLabel(parent,
                                 self.fld,
                                 width,
                                 noCap=noCap,
                                 isMan=self.isMan,
                                 default=self.defaultVal)
        elif self.fldClass == gf.FldEntry:
            guiFld = gf.FldEntry(parent,
                                 self.fld,
                                 width,
                                 noCap=noCap,
                                 isMan=self.isMan,
                                 default=self.defaultVal)
        elif self.fldClass == gf.FldOpt:
            guiFld = gf.FldOpt(parent,
                               self.fld,
                               width,
                               self.options,
                               self.defaultVal,
                               noCap=noCap
                               )
        elif self.fldClass == gf.FldOptJson:
            guiFld = gf.FldOptJson(parent,
                                   self.fld,
                                   width,
                                   self.optJson,
                                   self.optJsonHead,
                                   self.defaultVal,
                                   noCap=noCap
                                   )
        return guiFld


class tabs:
    pos = FldDef(flds.pos,
                 3,
                 3,
                 gf.FldEntry)


class paths:
    path = FldDef(flds.path,
                  45,
                  45,
                  gf.FldEntry)
    minPer = FldDef(flds.minPer,
                    10,
                    5,
                    gf.FldEntry)
    dec = FldDef(flds.dec,
                 10,
                 3,
                 gf.FldEntry)
    label = FldDef(flds.label,
                   10,
                   4,
                   gf.FldEntry
                   )
    skUnit = FldDef(flds.skUnit,
                    4,
                    4,
                    gf.FldOpt,
                    options=units.all(),
                    defaultVal=units.m
                    )
    dpUnit = FldDef(flds.dpUnit,
                    4,
                    4,
                    gf.FldOpt,
                    options=units.all(),
                    defaultVal=units.m
                    )
    bufSize = FldDef(flds.bufSize,
                     10,
                     3,
                     gf.FldEntry
                     )
    bufFreq = FldDef(flds.bufFreq,
                     10,
                     3,
                     gf.FldEntry
                     )
    min = FldDef(flds.min,
                 10,
                 4,
                 gf.FldEntry,
                 isMan=False
                 )
    max = FldDef(flds.max,
                 10,
                 4,
                 gf.FldEntry,
                 isMan=False)

    limit = FldDef(flds.limit,
                   10,
                   4,
                   gf.FldEntry,
                   isMan=False)
