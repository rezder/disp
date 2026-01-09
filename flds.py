
import units
import empty
from guiflds import Fld, FldLink
import guiflds as gf
from guiflddefs import FldDef


class flds:
    pathId = Fld("pathId",  # Maybe all should be id
                 "Path ID",
                 "Path ID",
                 str
                 )
    viewId = Fld("viewId", "View ID", "View ID",
                 str)

    view = Fld("view", "View", "View",
               str
               )

    dispId = Fld("dispId", "Display ID", "Dis. ID",
                 str
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
    val = Fld("val", "Value", "Value",
              float)
    limit = Fld("limit",
                "Limit",
                "Limit",
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
    interface = Fld("interface",
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

    paths = Fld("paths", "Paths", "Paths", dict, isTab=True)
    bigs = Fld("bigs", "Bigs", "Bigs", dict, isTab=True)
    alarms = Fld("alarms", "Alarms", "Alarms", dict, isTab=True)
    tabs = Fld("tabs", "Tabs", "Tabs", dict, isTab=True)
    poss = Fld("poss", "Positions", "Poss", dict, isTab=True)
    displays = Fld("displays", "Displays", "Displays", dict, isTab=True)
    macs = Fld("macs", "MAC Addresses", "MACs", dict, isTab=True)


class tabs:
    pos = FldDef(flds.pos,
                 3,
                 3,
                 gf.FldEntry)


class paths:
    path = FldDef(flds.pathId,
                  45,
                  45,
                  gf.FldEntry,
                  empty=empty.noEmpty,
                  isKey=True
                  )
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

    pathJs = FldDef(flds.pathId, 44, 44, gf.FldOpt,
                    linkDef=None,
                    options=None,
                    defaultVal="navigation.courseRhumbline.nextPoint.distance",
                    isKey=True
                    )

    labelJs = FldDef(flds.label, 4, 4, gf.FldOpt,
                     linkDef=FldLink(flds.label, flds.pathId, True),
                     options=None,
                     defaultVal="COG")
    dpUnitJs = FldDef(flds.dpUnit, 4, 4, gf.FldOpt,
                      linkDef=FldLink(flds.dpUnit, flds.pathId),
                      options=None,
                      defaultVal=units.m)
    dis = FldDef(flds.disable, 1, 1, gf.FldBool,
                 defaultVal=False)


class alarms_server:
    pathId = FldDef(flds.pathId, 44, 44, gf.FldLabel,
                    linkDef=None,
                    options=None,
                    isKey=True,
                    isVis=False
                    )

    label = FldDef(flds.label, 4, 4, gf.FldLabel,
                   linkDef=FldLink(flds.label, flds.pathId, False),
                   options=None
                   )

    min = FldDef(flds.min,
                 10,
                 4,
                 gf.FldLabel,
                 empty=empty.noNaN,
                 isMan=False
                 )
    val = FldDef(flds.val,
                 10,
                 4,
                 gf.FldLabel,
                 empty=empty.noNaN,
                 isJson=False
                 )
    max = FldDef(flds.max,
                 10,
                 4,
                 gf.FldLabel,
                 empty=empty.noNaN,
                 isMan=False)

    dis = FldDef(flds.disable, 1, 1, gf.FldBool,
                 defaultVal=False, isJson=False)


class settings:
    iface = FldDef(flds.interface,
                   10,
                   4,
                   gf.FldEntry,
                   )
    broadCP = FldDef(flds.broadCP,
                     10,
                     4,
                     gf.FldEntry,
                     )
    disSub = FldDef(flds.dissub,
                    10,
                    4,
                    gf.FldEntry,
                    )


class disp:
    dispId = FldDef(flds.dispId,
                    10,
                    10,
                    gf.FldLabel,
                    isKey=True,
                    empty=empty.noEmpty)

    view = FldDef(flds.view,
                  10,
                  10,
                  gf.FldOpt,
                  empty=empty.noEmpty,
                  defaultVal="None")

    addr = FldDef(flds.addr,
                  15,
                  15,
                  gf.FldLabel)

    dis = FldDef(flds.disable,
                 10,
                 4,
                 gf.FldBool,
                 defaultVal=False)

    viewId = FldDef(flds.viewId,
                    10,
                    10,
                    gf.FldLabel,
                    isKey=True,
                    empty=empty.noEmpty)

    poss = FldDef(fldsDict.poss,
                  10,
                  4,
                  gf.FldLabel,
                  isVis=False
                  )
    pathJs = FldDef(flds.pathId,
                    44,
                    44,
                    gf.FldOpt,
                    isKey=True,
                    defaultVal="environment.depth.belowTransducer"
                    )
    pos = FldDef(flds.pos,
                 10,
                 4,
                 gf.FldEntry,
                 )


