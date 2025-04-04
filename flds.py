import units
from guiflds import Fld, FldLink
import guiflds as gf
from guiflddefs import FldDef


class flds:
    path = Fld("path",
               "Path",
               "Path",
               str,
               str,
               "w",
               isKey=True)
    minPer = Fld("minPeriod",
                 "Min Period",
                 "Min Per",
                 str,
                 int,
                 "e"
                 )
    dec = Fld("decimals",
              "Decimals",
              "Dec.",
              str,
              int,
              "e")
    label = Fld("label",
                "Label",
                "Label",
                str,
                str,
                "w")
    skUnit = Fld("units",
                 "Signal k Unit",
                 "Sk Unit",
                 units.shortTxt,
                 units.noShort,
                 "w")
    dpUnit = Fld("dispUnits",
                 "Display Unit",
                 "Dp Unit",
                 units.shortTxt,
                 units.noShort,
                 "w")
    bufSize = Fld("bufSize",
                  "Buffer Size",
                  "Buf Size",
                  str,
                  int,
                  "e")
    bufFreq = Fld("bufFreq",
                  "Buffer Frequence",
                  "Buf Freq",
                  str,
                  int,
                  "e")
    min = Fld("min",
              "Min Value",
              "Min",
              str,
              float,
              "e")
    max = Fld("max",
              "Max Value",
              "Max",
              str,
              float,
              "e")
    limit = Fld("limit",
                "Limit",
                "limit",
                str,
                int,
                "e")
    pos = Fld("pos",
              "Position",
              "Pos",
              str,
              int,
              "e",
              isPrime=True)
    dis = Fld("dis",
              "Disable",
              "Dis",
              None,
              None,
              "e")


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
                    gf.FldEntry,
                    defaultVal=1000)
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
                     gf.FldEntry,
                     defaultVal=0
                     )
    bufFreq = FldDef(flds.bufFreq,
                     10,
                     3,
                     gf.FldEntry,
                     defaultVal=0
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
                     linkDef=FldLink(flds.label, flds.path, True),
                     options=None,
                     defaultVal="COG")
    dpUnitJs = FldDef(flds.dpUnit, 4, 4, gf.FldOpt,
                      linkDef=FldLink(flds.dpUnit, flds.path),
                      options=None,
                      defaultVal=units.m)
    dis = FldDef(flds.dis, 1, 1, gf.FldBool,
                 defaultVal=False)
