import tkinter as tk

from gui import BORDER_COLOR_ERR as BCE


def strJson(txt: str) -> str:
    if txt == "":
        raise ValueError()
    return txt


def jsonInerJoin(json1: dict, json2: dict) -> dict:
    res = dict()
    for k1, item1 in json1.items():
        resItem = dict(item1.items())
        if k1 in json2.keys():
            item2 = json2[k1]
            for h, v in item2.items():
                if h not in resItem.keys():
                    resItem[h] = v
        res[k1] = resItem

    return res


def compJson(json1: dict, json2: dict) -> bool:
    isEqual = True
    for k, v in json1.items():
        if json2[k] != v:
            isEqual = False
            break
    if isEqual:
        for k, v in json2.items():
            if json1[k] != v:
                isEqual = False
                break
    return isEqual


class Fld:
    def __init__(self,
                 jId: str,
                 header: str,
                 shortHeader: str,
                 toStr,
                 fromStr,
                 align: str,
                 isKey: bool = False,  # This should/could be def
                 isPrime: bool = False  # This should/could  be def
                 ):
        self.align = align
        self.header = header
        self.shortHeader = shortHeader
        self.toStr = toStr
        self.fromStr = fromStr
        self.jId = jId
        self.isKey = isKey
        self.isPrime = isPrime  # Single value of a key not a dict
        #  The fld does not have a header like iskey.

    def __eq__(self, o):
        return o is self


class FldLink:
    def __init__(self, dpFld: Fld, linkFld: Fld, isFilter: bool = False):
        self.dpFld = dpFld
        self.linkFld = linkFld
        self.isFilter = isFilter


class GuiFld:
    def __init__(self,
                 parent: tk.Frame,
                 fld: Fld,
                 width: int,
                 noCap: bool,
                 isMan: bool,
                 default,
                 isJson: bool,
                 linkDef: FldLink
                 ):
        self.parent = parent
        self.fld = fld
        self.width = width
        self.noCap = noCap
        self.isMan = isMan
        self.isJson = isJson
        self.linkDef = linkDef
        self.filter: list | None = None
        self.jsonFilter = None

        self.id = fld.jId
        self.default = default
        if self.default is None:
            self.defaultStr = ""
        else:
            self.defaultStr = self.toStr(default)
        self.mainFrame = tk.Frame(self.parent)
        self.mainFrame.config(highlightbackground=BCE)
        self.mainFrame.config(highlightthickness=0)
        txt = "{}:  ".format(self.fld.header)
        self.fldVar = tk.StringVar(value=self.defaultStr)
        self.fldHead = None
        self.column = 0
        self.isVis = True
        self.mainFrame.columnconfigure(0, weight=1)
        if not self.noCap:
            self.mainFrame.columnconfigure(1, weight=1)
            self.mainFrame.columnconfigure(0, weight=0)
            txt = "{}:  ".format(self.fld.header)
            self.fldHead = tk.Label(self.mainFrame, text=txt)
            self.fldHead.grid(row=0, column=0)
            self.column = 1

    def addWidget(self, widget):
        if self.noCap:
            widget.grid(sticky="ew", row=0, column=self.column)
        else:
            widget.grid(sticky="e", row=0, column=self.column)

    def show(self, inData):
        data = self.defaultStr
        try:
            data = self.toStr(inData)
        except (ValueError, KeyError):
            pass
        self.fldVar.set(data)

    def bindHead(self, seq: str, cb):  # TODO maybe we need the 3.argument add
        if not self.noCap:
            self.fldHead.bind(seq, cb)

    def unbindHead(self, seq: str):
        if not self.noCap:
            self.fldHead.unbind(seq)

    def setVis(self, isVis: bool):
        self.isVis = isVis

    def isEmpty(self):
        return "" == self.fldVar.get()

    def isInput(self):
        return False

    def get(self):
        """
        translate the string value if possible and
        retuns it. Even if validated this function
        may fails in case of optional int.
        str will never fail use strJson
        :raises: ValueError if translation fails
        """
        data = None
        try:
            data = self.fromStr(self.fldVar.get())
        except (ValueError, KeyError):
            pass
        return data

    def clear(self):
        if self.filter is not None:
            if self.default in self.filter:
                self.show(self.default)
            else:
                self.show(self.filter[0])
        else:
            self.fldVar.set(self.defaultStr)
        self.mainFrame.config(highlightthickness=0)

    def validate(self) -> bool:
        isOk = True
        self.setError(not isOk)
        v = self.get()
        if v is None:
            if self.isEmpty():
                if self.isMan:
                    isOk = False
            else:
                isOk = False
        elif self.filter is not None:
            if v not in self.filter:
                isOk = False
        if not isOk:
            self.setError(True)
        return isOk

    def setError(self, isError: bool):
        if isError:
            self.mainFrame.config(highlightthickness=3)
        else:
            self.mainFrame.config(highlightthickness=0)

    def setJsonObj(self, linkJson: dict):
        if self.jsonFilter is not None:
            self.jsonFilter.replaceItems(linkJson)
        else:
            self.jsonFilter = JsonFilter(linkJson,
                                         self.linkDef)
            self.jsonFilter.setGuiFld(self)

    def setFilter(self, filter: list):
        self.filter = filter

    def toStr(self, value) -> str:
        if self.jsonFilter is None:
            return self.fld.toStr(value)
        else:
            return self.jsonFilter.toStr(value)

    def fromStr(self, txt):
        if self.jsonFilter is None:
            return self.fld.fromStr(txt)
        else:
            return self.jsonFilter.fromStr(txt)


class FldLabel(GuiFld):
    def __init__(self, parent: tk.Frame, fld: Fld, width: int,
                 noCap=False, isMan=False, default=None,
                 isJson=True):
        super().__init__(parent, fld, width, noCap,
                         isMan, default, isJson, None)
        align = self.getAlign()
        self.fldLabelOut = tk.Label(self.mainFrame,
                                    textvariable=self.fldVar,
                                    anchor=align,
                                    width=self.width
                                    )
        self.addWidget(self.fldLabelOut)

    def getAlign(self):
        align = tk.CENTER
        if self.fld.align == "e":
            align = tk.E
        elif self.fld.align == "w":
            align = tk.W
        return align

    def bind(self, seq: str, cb):
        self.fldLabelOut.bind(seq, cb)

    def unbind(self, seq: str):
        self.fldLabelOut.unbind(seq)


class FldLabelHead(FldLabel):
    def __init__(self, parent: tk.Frame, fld: Fld):
        super().__init__(parent, fld, None,
                         noCap=True, isMan=False, default=None, isJson=False)
        self.show(self.fld.shortHeader)

    def addWidget(self, widget):
        widget.grid(row=0, column=self.column)

    def toStr(self, value) -> str:
        return value

    def fromStr(self, txt: str):
        raise Exception("Should not be use")
        return self.fld.fromStr(txt)

    def getAlign(self):
        return tk.CENTER


class FldEntry(GuiFld):
    def __init__(self, parent: tk.Frame, fld: Fld, width: int,
                 noCap=False, isMan=True, default=None, isJson=True,
                 isDisable=False):
        super().__init__(parent, fld, width, noCap,
                         isMan, default, isJson, None)
        align = "left"
        if self.fld.align == "e":
            align = "right"
        state = tk.NORMAL
        if isDisable:
            state = tk.DISABLED
        self.fldEntry = tk.Entry(self.mainFrame,
                                 textvariable=self.fldVar,
                                 justify=align,
                                 width=self.width,
                                 state=state
                                 )
        self.addWidget(self.fldEntry)

    def isInput(self):
        return True

    def postChgAdd(self, cb):
        self.fldEntry.bind("<FocusOut>", cb)

    def postChgRemov(self):
        self.fldEntry.ubind("<FocusOut>")

    def bind(self, seq: str, cb):
        self.fldEntry.bind(seq, cb)

    def unbind(self, seq: str):
        self.fldEntry.unbind(seq)


class FldBool(GuiFld):
    def __init__(self,
                 parent: tk.Frame,
                 fld: Fld,
                 default: bool = False,
                 noCap: bool = False,
                 isJson: bool = True,
                 linkDef: FldLink | None = None,
                 isDisable: bool = False):

        super().__init__(parent, fld, 1, noCap, isMan=True,
                         default=default, isJson=isJson, linkDef=linkDef)
        state = tk.NORMAL
        if isDisable:
            state = tk.DISABLED

        self.fldCheck = tk.Checkbutton(self.mainFrame,
                                       variable=self.fldVar,
                                       onvalue="1",
                                       offvalue="",
                                       # command=fn,
                                       # selectcolor="#1a1a1a",
                                       state=state)
        # The selectcolor is background of the checkmark.
        # The checkmark looks to be fg color.
        # Default selectcolor is white and classes with
        # selectcolor on Arch on Raspberry fg is dark
        # Checkmark have no fg. The hack uses
        # bg on frame to guess fg
        txtcolor: str = self.parent.cget("bg")
        if int(txtcolor[1:3], 16) < 100:
            self.fldCheck.config(selectcolor="#1a1a1a")

        self.addWidget(self.fldCheck)

    def postChgAdd(self, cb):
        self.fldCheck.config(command=cb)

    def isInput(self):
        return True

    def bind(self, seq: str, cb):
        self.fldCheck.bind(seq, cb)

    def unbind(self, seq: str):
        self.fldCheck.unbind(seq)

    def toStr(self, value) -> str:
        txt = ""
        if value:
            txt = "1"
        return txt

    def fromStr(self, txt):
        return bool(txt)


class FldOpt(GuiFld):
    def __init__(self,
                 parent: tk.Frame,
                 fld: Fld,
                 width: int,
                 options: list,
                 default=None,
                 noCap=False,
                 isJson=True,
                 linkDef=None):
        if options is None:
            options = [""]
            if default is not None:
                options = [default]
        if default is None:
            default = options[0]

        super().__init__(parent, fld, width, noCap, isMan=True,
                         default=default, isJson=isJson, linkDef=linkDef)

        self.options: list[str] = list()
        for i in options:
            self.options.append(self.toStr(i))

        self.fldOpt = tk.OptionMenu(self.mainFrame,
                                    self.fldVar,
                                    *self.options)
        self.fldOpt.config(width=self.width)
        self.addWidget(self.fldOpt)

    def isInput(self):
        return True

    def postChgAdd(self, cb):
        self.fldOpt.config(command=cb)

    def bind(self, seq: str, cb):
        self.fldOpt.bind(seq, cb)

    def unbind(self, seq: str):
        self.fldOpt.unbind(seq)

    def addOpt(self, opt):
        if self.jsonFilter is not None:
            raise Exception("Not possibel with json ")
        strOpt = self.toStr(opt)
        if strOpt not in self.options:
            self.options.append(strOpt)
            menu = self.fldOpt['menu']
            menu.add_command(label=strOpt, command=tk._setit(self.fldVar,
                                                             strOpt))

    def removeOpt(self, opt):
        if self.jsonFilter is not None:
            raise Exception("Not possibel with json")
        strOpt = self.toStr(opt)
        ix = self.options.index(strOpt)  # raise ValueError
        if self.defaultStr == strOpt or self.fldVar.get() == strOpt:
            raise ValueError
        self.options.remove(strOpt)
        menu = self.fldOpt['menu']
        menu.delete(ix)

    def replaceOpts(self, opts: list):
        strOpts = list()
        menu = self.fldOpt['menu']
        for opt in opts:
            so = self.toStr(opt)
            strOpts.append(so)
        value = self.fldVar.get()
        if value not in strOpts:
            self.show(opts[0])
        menu.delete(0, 'end')
        for strOpt in strOpts:
            menu.add_command(label=strOpt, command=tk._setit(self.fldVar,
                                                             strOpt))
        self.options = strOpts

    def setFilter(self, options):
        super().setFilter(options)
        self.replaceOpts(options)


class JsonFilter:
    def __init__(self, items: dict, linkDef: FldLink):
        self.slaveFilters: list[JsonFilter] = list()
        self.items = items
        self.linkDef = linkDef
        self.negfilter = set()
        self.isMaster = False
        if linkDef is None:
            self.isMaster = True
        else:
            self.dpFld = linkDef.dpFld
        self.isCbIgnore = False
        self.sortList = self.creaSortedOptions()

    def setGuiFld(self, guiFld: GuiFld):
        self.guiFld = guiFld
        self.guiFld.setFilter(self.sortList)
        if self.isMaster:
            self.setFldChgCb(self.fldChgCb)

    def setSlave(self, slaveGuiFld: GuiFld):
        slaveGuiFld.setJsonObj(self.items)
        slaveFilter = slaveGuiFld.jsonFilter
        self.slaveFilters.append(slaveFilter)
        slaveFilter.setFldChgCb(self.slaveCb)
        v = self.guiFld.get()
        if v is not None:
            self.ignoreCb = True
            slaveFilter.setKeyDpValue(v)
            self.ignoreCb = False
        else:
            self.updFilter()

    def setFldChgCb(self, fn):
        _ = self.guiFld.fldVar.trace_add('write', fn)

    def fldChgCb(self, var, index, mode):
        """
        Call back for master when strVar changes
        """
        v = self.guiFld.get()
        if v is not None and v in self.guiFld.filter:
            for slave in self.slaveFilters:
                self.ignoreCb = True
                slave.setKeyDpValue(v)
            self.ignoreCb = False

    def updFilter(self):
        removes = set()
        for slave in self.slaveFilters:
            negSet = slave.negFilter()
            removes = removes.union(negSet)
        no = len(self.items)
        if no - len(removes) == 1:
            removes.clear()
            all = set(self.items.keys())
            v = all.difference(removes).pop()
            if v != self.guiFld.get():
                self.guiFld.show(v)
        elif len(removes) == no:
            self.guiFld.show(None)
            removes.clear()
        if removes != self.negfilter:
            self.negfilter = removes
            options = self.creaSortedOptions()
            self.guiFld.setFilter(options)
            curVal = self.guiFld.get
            if curVal is not None:
                if curVal not in options:
                    self.guiFld.show(None)

    def slaveCb(self, var, index, mode):
        if not self.isCbIgnore:
            self.updFilter()

    def setKeyDpValue(self, key):
        if key is not None:
            v = self.items[key][self.dpFld.jId]
            self.guiFld.show(v)

    def negFilter(self) -> set:
        res = set()
        if self.linkDef.isFilter:
            value = self.guiFld.get()
            isEmpty = self.guiFld.isEmpty()
            for key in self.items.keys():
                isOk = True
                if not isEmpty:
                    if value is None:
                        isOk = False
                    else:
                        isOk = self.items[key][self.dpFld.jId] == value
                if not isOk:
                    res.add(key)
        return res

    def creaSortedOptions(self) -> list:
        sortList = None
        if self.isMaster:
            temp = list(sorted(self.items.keys()))
            for v in self.negfilter:
                temp.remove(v)
            sortList = [None]
            sortList.extend(temp)
        else:
            s = set()
            for r in self.items.values():
                s.add(r[self.dpFld.jId])
            ll = list(sorted(s))
            sortList = [None]
            sortList.extend(ll)
        return sortList

    def replaceItems(self, items: dict) -> list:
        self.items = items
        self.negfilter.clear()
        self.sortList = self.creaSortedOptions()
        self.guiFld.setFilter(self.sortList)
        for slave in self.slaveFilters:
            slave.replaceItems(items)

    def isValue(self, value) -> bool:
        isIn = value in self.sortList
        return isIn

    def toStr(self, value) -> str:
        res = ""
        if value is not None:
            if self.isMaster:
                res = self.guiFld.fld.toStr(value)
            else:
                res = self.dpFld.toStr(value)
        return res

    def fromStr(self, txt):
        res = None
        if txt != "":
            if self.isMaster:
                res = self.guiFld.fld.fromStr(txt)
            else:
                res = self.dpFld.fromStr(txt)
        return res
