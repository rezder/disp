import tkinter as tk
from functools import partial
import guijson as gj


class TabFldDef:
    def __init__(self,
                 fldDef: gj.FldDef,
                 fldClass,
                 isVis: bool = True,
                 options:  list | None = None,
                 optJson: dict | None = None,
                 defaultVal=None,
                 isMandatory: bool = True,
                 isKey: bool = False
                 ):
        pass


class Table:
    def __init__(self,
                 parent: tk.Frame,
                 initRows: int,
                 keyHeader: str,
                 sortHeader: str,
                 rowClickCb,
                 fldDefs: dict[str, gj.FldDef]):
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)

        self.keyJsonHead = keyHeader
        self.sortJsonHead = sortHeader
        self.rowsNo = initRows
        self.rowClickCb = rowClickCb

        self.fldDefs = fldDefs
        self.labels: list[list[tuple[tk.Label, tk.StringVar]]] = list()
        self.columnsNo = len(self.flddefs)

        self.tabFlds = list()
        self.delKeys: list[str] = list()
        self.headFlds: list[gj.FldLabelHead] = list()
        self.rowFlds: list[list[gj.Fld]] = list()

        for r in range(self.rowsNo+1):
            row: list[tuple[tk.Label, tk.StringVar]] = list()
            c = 0
            for fldDef in self.fldDefs.values():
                sVar = tk.StringVar()
                lable = tk.Label(self.mainFrame, textvariable=sVar)
                if r == 0:  # Init Headers
                    lable.grid(row=r, column=c)
                else:  # Init Rows
                    lable.grid(row=r, column=c, sticky=fldDef.align)
                row.append((lable, sVar))
                c = c + 1
            self.labels.append(row)

        # Set Header content
        i = 0
        for fldDef in self.fldDefs.values():
            label, sVar = self.labels[0][i]
            i = i + 1
            sVar.set(fldDef.header)

    def show(self, jsonObj: dict):
        # Sort
        sjsonObj = None
        if self.sortJsonHead != self.keyJsonHead:
            sjsonObj = dict(sorted(jsonObj.items(),
                                   key=lambda item: item[1][self.sortJsonHead]))
        else:
            sjsonObj = dict(sorted(jsonObj.items(), key=lambda item: item[0]))
        rowsNo = len(sjsonObj)

        diff = rowsNo - self.rowsNo
        if diff > 0:  # New
            for r in range(self.rowsNo, diff+self.rowsNo):
                row: list[tuple[tk.Label, tk.StringVar]] = list()
                c = 0
                for fldDef in self.fldDefs.values():
                    sVar = tk.StringVar()
                    lable = tk.Label(self.mainFrame, textvariable=sVar)
                    lable.grid(row=r, column=c, sticky=fldDef.align)
                    row.append((lable, sVar))
                    c = c + 1
            self.labels.append(row)
            self.rowsNo = diff+self.rowsNo

        if diff < 0:  # Hide
            for i in range(self.rowsNo+diff, self.rowsNo):
                row = self.labels[i]
                for (_, v) in row:
                    v.set("")
        #  Set content
        rowNo = 1
        columnNo = 0
        for k, v in sjsonObj.items():
            labelH, strVarH = self.labels[rowNo][columnNo]
            strVarH.set(self.fldDefs[self.keyJsonHead].toStr(k))
            labelH.bind("<ButtonRelease-1>",
                        partial(self.rowcb, k, self.keyJsonHead))
            columnNo = columnNo + 1
            for head, fldDef in self.fldDefs.items():
                if head != self.keyJsonHead:
                    if head in v.keys():  # replace content flds
                        labelC, strVarC = self.labels[rowNo][columnNo]
                        labelC.bind("<ButtonRelease-1>",
                                    partial(self.rowcb, k, head))
                        strVarC.set(fldDef.toStr(v[head]))
                    else:  # Clear cont flds
                        label, strVar = self.labels[rowNo][columnNo]
                        strVar.set("")
                    columnNo = columnNo + 1
            rowNo = rowNo + 1
            columnNo = 0

    def rowcb(self, path, head, event):
        self.rowClickCb(path, head)
