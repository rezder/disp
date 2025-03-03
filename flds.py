import units


class Fld:
    def __init__(self,
                 jsonHead: str,
                 header: str,
                 shortHeader: str,
                 toStr,
                 fromStr,
                 align: str,
                 isKey: bool = False,
                 isPrime: bool = False
                 ):
        self.align = align
        self.header = header
        self.shortHeader = shortHeader
        self.toStr = toStr
        self.fromStr = fromStr
        self.jsonHead = jsonHead
        self.isKey = isKey
        self.isPrime = isPrime

    def __eq__(self, o):
        return o is self


class Link:
    def __init__(self, dpFld: Fld, linkFld: Fld, isFilter: bool = False):
        self.dpFld = dpFld
        self.linkFld = linkFld
        self.isFilter = isFilter


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
