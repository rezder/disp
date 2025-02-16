import tkinter as tk
from functools import partial


class Fld:
    def __init__(self,
                 parent: tk.Frame,
                 header: str,
                 toStr,
                 fromStr,
                 ):
        self.toStr = toStr
        self.fromStr = fromStr
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.mainFrame.columnconfigure(1, weight=1)
        self.mainFrame.columnconfigure(0, weight=0)
        self.mainFrame.pack(fill="x")
        txt = "{}:  ".format(header)
        self.fldLabel = tk.Label(self.mainFrame, text=txt)
        self.fldLabel.grid(row=0, column=0)
        self.fldVar = tk.StringVar()
        self.fldEntry = tk.Entry(self.mainFrame, textvariable=self.fldVar, justify="right")
        self.fldEntry.grid(sticky="e", row=0, column=1)

    def show(self, data):
        self.fldVar.set(self.toStr(data))

    def get(self):
        return self.fromStr(self.fldVar.get())


class FldOpt:
    def __init__(self,
                 parent: tk.Frame,
                 header: str,
                 default,
                 toStr,
                 fromStr,
                 options: list
                 ):

        self.toStr = toStr
        self.fromStr = fromStr
        self.default = toStr(default)
        self.options: list[str] = list()
        for i in options:
            self.options.append(self.toStr(i))

        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.mainFrame.columnconfigure(1, weight=1)
        self.mainFrame.columnconfigure(0, weight=0)
        self.mainFrame.pack(fill="x")
        txt = "{}:  ".format(header)
        self.fldLabel = tk.Label(self.mainFrame, text=txt)
        self.fldLabel.grid(row=0, column=0)
        self.fldVar = tk.StringVar(value=self.default)
        self.fldOpt = tk.OptionMenu(self.mainFrame,
                                    self.fldVar,
                                    *self.options)
        self.fldOpt.grid(sticky="e", row=0, column=1)

    def show(self, data):
        self.fldVar.set(self.toStr(data))

    def get(self):
        return self.fromStr(self.fldVar.get())


class Table:
    def __init__(self,
                 parent: tk.Frame,
                 jsonObj: dict,
                 keyHeader: str,
                 sortHeader: str,
                 conv: dict,
                 rowClickCb):
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.keyHead = keyHeader
        self.conv = conv
        self.sortHead = sortHeader
        self.rowsNo = len(jsonObj)
        self.rowClickCb = rowClickCb
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
                sVar.set
                lable = tk.Label(self.mainFrame, textvariable=sVar)
                lable.grid(row=r, column=c)
                row.append((lable, sVar))
            self.labels.append(row)
        self.headers: list[str] = list()
        self.headers.append(self.keyHead)
        self.headers.extend(value.keys())
        for i in range(self.columnsNo):
            label, sVar = self.labels[0][i]
            sVar.set(self.headers[i])

    def show(self, jsonObj: dict):
        sjsonObj = None
        if self.sortHead != self.headers[0]:
            sjsonObj = dict(sorted(jsonObj.items(),
                                   key=lambda item: item[1][self.sortHead]))
        else:
            sjsonObj = dict(sorted(jsonObj.items(), key=lambda item: item[0]))
        rowsNo = len(sjsonObj)
        print(sjsonObj)
        print(jsonObj)
        diff = rowsNo - self.rowsNo
        if diff > 0:
            for r in range(self.rowsNo, diff+self.rowsNo):
                row: list[tuple[tk.Label, tk.StringVar]] = list()
                for c in range(self.columnsNo):
                    sVar = tk.StringVar()
                    sVar.set
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
                    print(self.conv[head](v[head]))
                    strVarC.set(self.conv[head](v[head]))
                else:
                    label, strVar = self.labels[rowNo][columnNo]
                    strVar.set("")
                columnNo = columnNo + 1
            rowNo = rowNo + 1
            columnNo = 0

    def rowcb(self, path, head, event):
        self.rowClickCb(path, head)
