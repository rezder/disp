from flds import Fld, flds, Link
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
                 linkDef: Link | None = None,
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

    pathJs = FldDef(flds.path, 44, 44, gf.FldOpt,
                    linkDef=None,
                    options=None,
                    defaultVal="navigation.courseRhumbline.nextPoint.distance"
                    )

    labelJs = FldDef(flds.label, 4, 4, gf.FldOpt,
                     linkDef=Link(flds.label, flds.path, True),
                     options=None,
                     defaultVal="COG")
    dpUnitJs = FldDef(flds.dpUnit, 4, 4, gf.FldOpt,
                      linkDef=Link(flds.dpUnit, flds.path),
                      options=None,
                      defaultVal=units.m)
    dis = FldDef(flds.dis, 1, 1, gf.FldBool,
                 defaultVal=False)
