import tkinter as tk
from functools import partial
from gui import BORDER_COLOR_ERR as BCE


def strJson(txt: str) -> str:
    if txt == "":
        raise ValueError()
    return txt


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


class FldDef:
    def __init__(self,
                 jsonHead: str,
                 header: str,
                 toStr,
                 fromStr,
                 align: str,
                 isKey: bool = False
                 ):
        self.align = align
        self.header = header
        self.toStr = toStr
        self.fromStr = fromStr
        self.jsonHead = jsonHead
        self.isKey = isKey


class Fld:
    def __init__(self,
                 parent: tk.Frame,
                 fldDef: FldDef,
                 width: int,
                 noCap: bool,
                 isMan: bool,
                 default,
                 isJson: bool
                 ):
        self.parent = parent
        self.fldDef = fldDef
        self.width = width
        self.noCap = noCap
        self.isMan = isMan
        self.isJson = isJson
        self.id = fldDef.jsonHead
        if default is None:
            self.defaultStr = ""
        else:
            self.defaultStr = self.toStr(default)
        self.mainFrame = tk.Frame(self.parent)
        self.mainFrame.config(highlightbackground=BCE)
        self.mainFrame.config(highlightthickness=0)
        txt = "{}:  ".format(self.fldDef.header)
        self.fldVar = tk.StringVar(value=self.defaultStr)
        self.fldHead = None
        self.column = 0
        self.isVis = True
        self.mainFrame.columnconfigure(0, weight=1)
        if not self.noCap:
            self.mainFrame.columnconfigure(1, weight=1)
            self.mainFrame.columnconfigure(0, weight=0)
            txt = "{}:  ".format(self.fldDef.header)
            self.fldHead = tk.Label(self.mainFrame, text=txt)
            self.fldHead.grid(row=0, column=0)
            self.column = 1

    def addWidget(self, widget):
        if self.noCap:
            widget.grid(sticky="ew", row=0, column=self.column)
        else:
            widget.grid(sticky="e", row=0, column=self.column)

    def show(self, data):
        self.fldVar.set(self.toStr(data))

    def bind(self, seq: str, cb):
        if not self.noCap:
            self.fldHead.bind(seq, cb)

    def unbind(self, seq: str):
        if not self.noCap:
            self.fldHead.unbind(seq)

    def setVis(self, isVis: bool):
        self.isVis = isVis

    def get(self):
        """
        translate the string value if possible and
        retuns it. Even if validated this function
        may fails in case of optional int.
        str will never fail use strJson
        :raises: ValueError if translation fails
        """
        return self.fromStr(self.fldVar.get())

    def clear(self):
        self.fldVar.set(self.defaultStr)
        self.mainFrame.config(highlightthickness=0)

    def validate(self) -> bool:
        isOk = True
        self.setError(not isOk)
        return isOk

    def setError(self, isError: bool):
        if isError:
            self.mainFrame.config(highlightthickness=3)
        else:
            self.mainFrame.config(highlightthickness=0)

    def toStr(self, value) -> str:
        return self.fldDef.toStr(value)

    def fromStr(self, txt: str):
        return self.fldDef.fromStr(txt)


class FldLabel(Fld):
    def __init__(self, parent: tk.Frame, fldDef: FldDef, width: int,
                 noCap=False, isMan=False, default=None, isJson=True):
        super().__init__(parent, fldDef, width, noCap, isMan, default, isJson)
        align = self.getAlign()
        self.fldLabelOut = tk.Label(self.mainFrame,
                                    textvariable=self.fldVar,
                                    anchor=align,
                                    width=self.width
                                    )
        self.addWidget(self.fldLabelOut)

    def getAlign(self):
        align = tk.CENTER
        if self.fldDef.align == "e":
            align = tk.E
        elif self.fldDef.align == "w":
            align = tk.W
        return align

    def bind(self, seq: str, cb):
        super().bind(seq, cb)
        self.fldLabelOut.bind(seq, cb)

    def unbind(self, seq: str):
        super().unbind(seq)
        self.fldLabelOut.unbind(seq)

    def validate(self) -> bool:
        isOk = super().validate()
        txt = self.fldVar.get()
        if txt == "":
            if self.isMan:
                if self.defaultStr == "":
                    self.setError(True)
                    isOk = False
                else:
                    self.fldVar.set(self.defaultStr)
        else:
            try:
                self.fromStr(txt)
            except ValueError:
                self.setError(True)
                isOk = False

        return isOk


class FldLabelHead(FldLabel):
    def __init__(self, parent: tk.Frame, fldDef: FldDef, width: int):
        super().__init__(parent, fldDef, width,
                         noCap=True, isMan=False, default=None, isJson=False)
        self.show(self.fldDef.header)

    def addWidget(self, widget):
        widget.grid(row=0, column=self.column)

    def toStr(self, value) -> str:
        return value

    def fromStr(self, txt: str):
        raise Exception("Should not be use")
        return self.fldDef.fromStr(txt)

    def getAlign(self):
        return tk.CENTER


class FldEntry(Fld):
    def __init__(self, parent: tk.Frame, fldDef: FldDef, width: int,
                 noCap=False, isMan=True, default=None, isJson=True):
        super().__init__(parent, fldDef, width, noCap,
                         isMan=isMan, default=default, isJson=isJson)
        align = "left"
        if self.fldDef.align == "e":
            align = "right"
        self.fldEntry = tk.Entry(self.mainFrame,
                                 textvariable=self.fldVar,
                                 justify=align,
                                 width=self.width
                                 )
        self.addWidget(self.fldEntry)

    def bind(self, seq: str, cb):
        super().bind(seq, cb)
        self.fldEntry.bind(seq, cb)

    def unbind(self, seq: str):
        super().unbind(seq)
        self.fldEntry.unbind(seq)

    def validate(self) -> bool:
        isOk = super().validate()
        txt = self.fldVar.get()
        txt = txt.strip()
        self.fldVar.set(txt)
        if txt == "":
            if self.isMan:
                if self.defaultStr == "":
                    self.setError(True)
                    isOk = False
                else:
                    self.fldVar.set(self.defaultStr)
        else:
            try:
                self.fromStr(txt)
            except ValueError:
                self.setError(True)
                isOk = False

        return isOk


class FldOpt(Fld):
    def __init__(self,
                 parent: tk.Frame,
                 fldDef: FldDef,
                 width: int,
                 options: list,
                 default,
                 noCap=False,
                 isJson=True):
        super().__init__(parent, fldDef, width, noCap, isMan=True,
                         default=default, isJson=isJson)

        self.options: list[str] = list()
        for i in options:
            self.options.append(self.toStr(i))

        self.fldOpt = tk.OptionMenu(self.mainFrame,
                                    self.fldVar,
                                    *self.options)
        self.fldOpt.config(width=self.width)
        self.addWidget(self.fldOpt)

    def bind(self, seq: str, cb):
        super().bind(seq, cb)
        self.fldOpt.bind(seq, cb)

    def unbind(self, seq: str):
        super().unbind(seq)
        self.fldOpt.unbind(seq)

    def addOpt(self, opt):
        strOpt = self.toStr(opt)
        if strOpt not in self.options:
            self.options.append(strOpt)
            menu = self.fldOpt['menu']
            menu.add_command(label=strOpt, command=tk._setit(self.fldVar,
                                                             strOpt))

    def removeOpt(self, opt):
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
        default = self.defaultStr
        if default not in strOpts or self.fldVar.get() not in strOpts:
            raise ValueError
        menu.delete(0, 'end')
        for strOpt in strOpts:
            menu.add_command(label=strOpt, command=tk._setit(self.fldVar,
                                                             strOpt))
        self.options = strOpts


class FldOptJson(FldOpt):
    """
    Option fld based on json object.
    Could be improved with own popup table
    and entry field. To allow for more
    header fields.
    """
    def __init__(self,
                 parent: tk.Frame,
                 fldDef: FldDef,
                 width: int,
                 itemsJson: dict,
                 dpHeadJson: str | None,
                 default,
                 noCap=False,
                 isJson=True
                 ):

        self.itemsJson = itemsJson
        self.dpHeadJson = dpHeadJson

        super().__init__(parent,
                         fldDef,
                         width,
                         self.getSortedOptions(),
                         default,
                         noCap=noCap, isJson=isJson)

    def getSortedOptions(self):
        sortList = None
        if self.dpHeadJson is None:
            sortList = list(sorted(self.itemsJson.items(),
                                   key=lambda item: item[0]))
        else:
            sortList = list(sorted(self.itemsJson.items(),
                                   key=lambda item: item[1][self.dpHeadJson]))
        return sortList

    def toStr(self, value):
        k, jsonItem = value
        if self.dpHeadJson is None:
            return self.fldDef.toStr(k)
        else:
            v = jsonItem[self.dpHeadJson]
            return self.fldDef.toStr(v)

    def fromStr(self, txt):
        res = None
        for key, item in self.itemsJson.items():
            v = None
            if self.dpHeadJson in item.keys():
                v = item[self.dpHeadJson]
            else:
                v = key
            if v == self.fldDef.fromStr(txt):
                res = (key, item)
                break
        return res

    def addOpt(self, opt):
        raise ValueError("Not possible")

    def removeOpt(self, opt):
        raise ValueError("Not possible")

    def replaceOpts(self, itemsJson: dict):
        self.itemsJson = itemsJson
        super().replaceOpts(self.getSortedOptions())


class Table:
    def __init__(self,
                 parent: tk.Frame,
                 initRows: int,
                 sortFldDef: FldDef,
                 rowClickCb,
                 flds: list[FldDef]):
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.fldDefs = flds
        self.sortFldDef = sortFldDef
        self.rowsNo = initRows
        self.rowClickCb = rowClickCb

        self.columnsNo = len(flds)
        self.labels: list[list[tuple[tk.Label, tk.StringVar]]] = list()
        for r in range(self.rowsNo+1):
            row: list[tuple[tk.Label, tk.StringVar]] = list()
            c = 0
            for fldDef in self.fldDefs:
                sVar = tk.StringVar()
                lable = tk.Label(self.mainFrame, textvariable=sVar)
                if r == 0:
                    lable.grid(row=r, column=c)
                else:
                    lable.grid(row=r, column=c, sticky=fldDef.align)
                row.append((lable, sVar))
                c = c + 1
            self.labels.append(row)

        i = 0
        for fldDef in self.fldDefs:
            label, sVar = self.labels[0][i]
            i = i + 1
            sVar.set(fldDef.header)

    def show(self, jsonObj: dict):
        sjsonObj = None
        k = self.sortFldDef.jsonHead
        if not self.sortFldDef.isKey:
            k = self.sortFldDef.jsonHead
            sjsonObj = dict(sorted(jsonObj.items(),
                                   key=lambda item: item[1][k]))
        else:
            sjsonObj = dict(sorted(jsonObj.items(), key=lambda item: item[0]))
        rowsNo = len(sjsonObj)
        diff = rowsNo - self.rowsNo
        if diff > 0:
            for r in range(self.rowsNo, diff+self.rowsNo):
                row: list[tuple[tk.Label, tk.StringVar]] = list()
                c = 0
                for fldDef in self.fldDefs:
                    sVar = tk.StringVar()
                    lable = tk.Label(self.mainFrame, textvariable=sVar)
                    lable.grid(row=r, column=c, sticky=fldDef.align)
                    row.append((lable, sVar))
                    c = c + 1
            self.labels.append(row)
            self.rowsNo = diff+self.rowsNo

        if diff < 0:
            for i in range(self.rowsNo+diff, self.rowsNo):
                row = self.labels[i]
                for (_, v) in row:
                    v.set("")
        rowNo = 1
        columnNo = 0
        for k, v in sjsonObj.items():
            for fldDef in self.fldDefs:
                label, strVar = self.labels[rowNo][columnNo]
                if fldDef.jsonHead in v.keys():
                    label.bind("<ButtonRelease-1>",
                               partial(self.rowcb, k, fldDef.jsonHead))
                    strVar.set(fldDef.toStr(v[fldDef.jsonHead]))
                else:
                    vStr = ""
                    if fldDef.isKey:
                        vStr = fldDef.toStr(k)
                        label.bind("<ButtonRelease-1>",
                                   partial(self.rowcb, k, fldDef.jsonHead))
                    strVar.set(vStr)
                columnNo = columnNo + 1
            rowNo = rowNo + 1
            columnNo = 0

    def rowcb(self, path, head, event):
        self.rowClickCb(path, head)
