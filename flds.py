
import units
import empty
from guiflds import Fld, FldLink
import guiflds as gf
from guiflddefs import FldDef
import json


class flds:
    path = Fld("path",  # Maybe all should be id
               "Path",
               "Path",
               str,
               isKey=True)
    viewId = Fld("viewId", "View ID", "View ID",
                 str, isKey=True)

    view = Fld("view", "View", "View",
               str
               )

    dispId = Fld("dispId", "Display ID", "Dis. ID",
                 str,
                 isKey=True
                 )

    minPer = Fld("minPeriod",
                 "Min Period",
                 "Min Per",
                 int
                 )
    dec = Fld("decimals",
              "Decimals",
              "Dec.",
              int
              )
    label = Fld("label",
                "Label",
                "Label",
                str
                )
    skUnit = Fld("units",
                 "Signal k Unit",
                 "Sk Unit",
                 int,
                 toStr=units.shortTxt,
                 fromStr=units.noShort,
                 isDom=True)
    dpUnit = Fld("dispUnits",
                 "Display Unit",
                 "Dp Unit",
                 int,
                 toStr=units.shortTxt,
                 fromStr=units.noShort,
                 isDom=True)
    bufSize = Fld("bufSize",
                  "Buffer Size",
                  "Buf Size",
                  int
                  )
    bufFreq = Fld("bufFreq",
                  "Buffer Frequence",
                  "Buf Freq",
                  int
                  )
    min = Fld("min",
              "Min Value",
              "Min",
              float
              )
    max = Fld("max",
              "Max Value",
              "Max",
              float
              )
    limit = Fld("limit",
                "Limit",
                "limit",
                int
                )
    pos = Fld("pos",
              "Position",
              "Pos",
              int
              )
    disable = Fld("isDisable",
                  "Disable",
                  "Disable",
                  bool
                  )
    addr = Fld("addr",
               "Address",
               "Addr",
               str
               )
    broadCP = Fld("broadcastPort",
                  "Broadcast Port",
                  "BC Port",
                  int
                  )
    intface = Fld("interface",
                  "Wifi Interface",
                  "Wifi",
                  str)
    dissub = Fld("disableSubServer",
                 "Disable Subscriber Server",
                 "Dis Sub",
                 bool
                 )


class fldsDict:

    conf = Fld("conf", "Server Configuration", "Conf", dict)

    paths = Fld("paths", "Paths", "Paths", dict)
    bigs = Fld("bigs", "Bigs", "Bigs", dict)
    alarms = Fld("alarms", "Alarms", "Alarms", dict)
    tabs = Fld("tabs", "Tabs", "Tabs", dict)
    poss = Fld("poss", "Positions", "Poss", dict)
    displays = Fld("displays", "Displays", "Displays", dict)
    macs = Fld("macs", "MAC Addresses", "MACs", dict)


class tabs:
    pos = FldDef(flds.pos,
                 3,
                 3,
                 gf.FldEntry)


class paths:
    path = FldDef(flds.path,
                  45,
                  45,
                  gf.FldEntry,
                  empty=empty.noEmpty)
    minPer = FldDef(flds.minPer,
                    10,
                    5,
                    gf.FldEntry,
                    defaultVal=1000,
                    empty=empty.noZero)
    dec = FldDef(flds.dec,
                 10,
                 3,
                 gf.FldEntry)
    label = FldDef(flds.label,
                   10,
                   4,
                   gf.FldEntry,
                   empty=empty.noEmpty
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
                 empty=empty.noNaN,
                 isMan=False
                 )
    max = FldDef(flds.max,
                 10,
                 4,
                 gf.FldEntry,
                 empty=empty.noNaN,
                 isMan=False)
    limit = FldDef(flds.limit,
                   10,
                   4,
                   gf.FldEntry,
                   empty=empty.noZero)

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
    dis = FldDef(flds.disable, 1, 1, gf.FldBool,
                 defaultVal=False)
