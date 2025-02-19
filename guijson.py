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


class Fld:
    def __init__(self,
                 parent: tk.Frame,
                 header: str,
                 width: int,
                 isMandatory: bool,
                 toStr,
                 fromStr,
                 default=None
                 ):
        self.header = header
        self.toStr = toStr
        self.fromStr = fromStr
        self.parent = parent
        self.width = width
        self.isMan = isMandatory
        if default is None:
            self.defaultStr = ""
        else:
            self.defaultStr = self.toStr(default)
        self.mainFrame = tk.Frame(self.parent)
        self.mainFrame.columnconfigure(1, weight=1)
        self.mainFrame.columnconfigure(0, weight=0)
        self.mainFrame.config(highlightbackground=BCE)
        self.mainFrame.config(highlightthickness=0)
        txt = "{}:  ".format(self.header)
        self.fldLabel = tk.Label(self.mainFrame, text=txt)
        self.fldLabel.grid(row=0, column=0)
        self.fldVar = tk.StringVar(value=self.defaultStr)
        self.fldEntry = tk.Entry(self.mainFrame,
                                 textvariable=self.fldVar,
                                 justify="right",
                                 width=self.width
                                 )
        self.fldEntry.grid(sticky="e", row=0, column=1)

    def show(self, data):
        self.fldVar.set(self.toStr(data))

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

    def getHeader(self) -> str:
        return self.header

    def getToStr(self):
        return self.toStr

    def validate(self) -> bool:
        isOk = True
        self.setError(isOk)
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

    def setError(self, isError: bool):
        if isError:
            self.mainFrame.config(highlightthickness=3)
        else:
            self.mainFrame.config(highlightthickness=0)


class FldOpt:
    def __init__(self,
                 parent: tk.Frame,
                 header: str,
                 width: int,
                 default,
                 toStr,
                 fromStr,
                 options: list
                 ):
        self.header = header
        self.width = width
        self.toStr = toStr
        self.fromStr = fromStr
        self.defaultStr = toStr(default)
        self.options: list[str] = list()
        for i in options:
            self.options.append(self.toStr(i))

        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.mainFrame.columnconfigure(1, weight=1)
        self.mainFrame.columnconfigure(0, weight=0)
        self.mainFrame.config(highlightbackground=BCE)
        self.mainFrame.config(highlightthickness=0)
        txt = "{}:  ".format(self.header)
        self.fldLabel = tk.Label(self.mainFrame, text=txt)
        self.fldLabel.grid(row=0, column=0)
        self.fldVar = tk.StringVar(value=self.defaultStr)
        self.fldOpt = tk.OptionMenu(self.mainFrame,
                                    self.fldVar,
                                    *self.options)
        self.fldOpt.config(width=self.width)
        self.fldOpt.grid(sticky="e", row=0, column=1)

    def getHeader(self) -> str:
        return self.header

    def getToStr(self):
        return self.toStr

    def show(self, data):
        self.fldVar.set(self.toStr(data))

    def get(self):
        return self.fromStr(self.fldVar.get())

    def clear(self):
        self.fldVar.set(self.defaultStr)
        self.mainFrame.config(highlightthickness=0)

    def validate(self) -> bool:
        self.setError(False)
        return True

    def setError(self, isError: bool):
        if isError:
            self.mainFrame.config(highlightthickness=3)
        else:
            self.mainFrame.config(highlightthickness=0)

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
        if self.default == strOpt or self.fldVar.get() == strOpt:
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
        if self.default not in strOpts or self.fldVar.get() not in strOpts:
            raise ValueError
        menu.delete(0, 'end')
        for strOpt in strOpts:
            menu.add_command(label=strOpt, command=tk._setit(self.fldVar,
                                                             strOpt))
        self.options = strOpts


class Table:
    def __init__(self,
                 parent: tk.Frame,
                 jsonObj: dict,
                 keyHeader: str,
                 sortHeader: str,
                 conv: dict,
                 rowClickCb,
                 dpHeaders: dict | None = None):
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.dpHeaders = dpHeaders
        self.keyHead = keyHeader
        self.conv = conv
        self.sortHead = sortHeader
        self.rowsNo = len(jsonObj)
        self.rowClickCb = rowClickCb
        #  Get all fields
        value = None
        vl = 0
        bigk = None
        for k, v in jsonObj.items():
            ll = len(v)
            if ll > vl:
                vl = ll
                bigk = k

        value = jsonObj[bigk]

        self.columnsNo = len(value)+1
        self.labels: list[list[tuple[tk.Label, tk.StringVar]]] = list()
        for r in range(self.rowsNo+1):
            row: list[tuple[tk.Label, tk.StringVar]] = list()
            for c in range(self.columnsNo):
                sVar = tk.StringVar()
                lable = tk.Label(self.mainFrame, textvariable=sVar)
                lable.grid(row=r, column=c)
                row.append((lable, sVar))
            self.labels.append(row)
        self.headers: list[str] = list()
        self.headers.append(self.keyHead)
        self.headers.extend(value.keys())
        for i in range(self.columnsNo):
            label, sVar = self.labels[0][i]
            sVar.set(self.headXhead(self.headers[i]))

    def headXhead(self, jsonHead) -> str:
        if self.dpHeaders is None:
            return jsonHead
        else:
            return self.dpHeaders[jsonHead]

    def show(self, jsonObj: dict):
        sjsonObj = None
        if self.sortHead != self.headers[0]:
            sjsonObj = dict(sorted(jsonObj.items(),
                                   key=lambda item: item[1][self.sortHead]))
        else:
            sjsonObj = dict(sorted(jsonObj.items(), key=lambda item: item[0]))
        rowsNo = len(sjsonObj)
        diff = rowsNo - self.rowsNo
        if diff > 0:
            for r in range(self.rowsNo, diff+self.rowsNo):
                row: list[tuple[tk.Label, tk.StringVar]] = list()
                for c in range(self.columnsNo):
                    sVar = tk.StringVar()
                    lable = tk.Label(self.mainFrame, textvariable=sVar)
                    lable.grid(row=r, column=c)
                    row.append((lable, sVar))
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
            labelH, strVarH = self.labels[rowNo][columnNo]
            strVarH.set(self.conv[self.keyHead](k))
            labelH.bind("<ButtonRelease-1>",
                        partial(self.rowcb, k, self.keyHead))
            columnNo = columnNo + 1
            for head in self.headers[1:]:
                if head in v.keys():
                    labelC, strVarC = self.labels[rowNo][columnNo]
                    labelC.bind("<ButtonRelease-1>",
                                partial(self.rowcb, k, head))
                    strVarC.set(self.conv[head](v[head]))
                else:
                    label, strVar = self.labels[rowNo][columnNo]
                    strVar.set("")
                columnNo = columnNo + 1
            rowNo = rowNo + 1
            columnNo = 0

    def rowcb(self, path, head, event):
        self.rowClickCb(path, head)
