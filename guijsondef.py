class JsonFld:
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


class GuiFld:
    def __init__(self,
                 jsonFld: JsonFld,
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
        self.jsonFld = jsonFld
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

    def cp(self):
        res = GuiFld(self.jsonFld,
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
