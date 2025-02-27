import guijsondef as gdef
import guiflds
import units


class defs:
    path = gdef.JsonFld("path",
                        "Path",
                        "Path",
                        str,
                        str,
                        "w",
                        isKey=True)
    minPer = gdef.JsonFld("minPeriod",
                          "Min Period",
                          "Min Per",
                          str,
                          int,
                          "e"
                          )
    dec = gdef.JsonFld("decimals",
                       "Decimals",
                       "Dec.",
                       str,
                       int,
                       "e")
    label = gdef.JsonFld("label",
                         "Label",
                         "Label",
                         str,
                         str,
                         "w")
    skUnit = gdef.JsonFld("units",
                          "Signal k Unit",
                          "Sk Unit",
                          units.shortTxt,
                          units.noShort,
                          "w")
    dpUnit = gdef.JsonFld("dispUnits",
                          "Display Unit",
                          "Dp Unit",
                          units.shortTxt,
                          units.noShort,
                          "w")
    bufSize = gdef.JsonFld("bufSize",
                           "Buffer Size",
                           "Buf Size",
                           str,
                           int,
                           "e")
    bufFreq = gdef.JsonFld("bufFreq",
                           "Buffer Frequence",
                           "Buf Freq",
                           str,
                           int,
                           "e")
    min = gdef.JsonFld("min",
                       "Min Value",
                       "Min",
                       str,
                       float,
                       "e")
    max = gdef.JsonFld("max",
                       "Max Value",
                       "Max",
                       str,
                       float,
                       "e")
    limit = gdef.JsonFld("limit",
                         "Limit",
                         "limit",
                         str,
                         int,
                         "e")


class paths:
    path = gdef.GuiFld(defs.path,
                       45,
                       45,
                       guiflds.FldEntry)
    minPer = gdef.GuiFld(defs.minPer,
                         10,
                         5,
                         guiflds.FldEntry)
    dec = gdef.GuiFld(defs.dec,
                      10,
                      3,
                      guiflds.FldEntry)
    label = gdef.GuiFld(defs.label,
                        10,
                        4,
                        guiflds.FldEntry
                        )
    skUnit = gdef.GuiFld(defs.skUnit,
                         4,
                         4,
                         guiflds.FldOpt,
                         options=units.all(),
                         defaultVal=units.m
                         )
    dpUnit = gdef.GuiFld(defs.dpUnit,
                         4,
                         4,
                         guiflds.FldOpt,
                         options=units.all(),
                         defaultVal=units.m
                         )
    bufSize = gdef.GuiFld(defs.bufSize,
                          10,
                          3,
                          guiflds.FldEntry
                          )
    bufFreq = gdef.GuiFld(defs.bufFreq,
                          10,
                          3,
                          guiflds.FldEntry
                          )
    min = gdef.GuiFld(defs.min,
                      10,
                      4,
                      guiflds.FldEntry,
                      isMan=False
                      )
    max = gdef.GuiFld(defs.max,
                      10,
                      4,
                      guiflds.FldEntry,
                      isMan=False)

    limit = gdef.GuiFld(defs.limit,
                        10,
                        4,
                        guiflds.FldEntry,
                        isMan=False)
