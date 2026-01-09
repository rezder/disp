import tkinter as tk

import guiflds as gf
from guiflds import Fld
from flds import settings as dd


class Sett:
    def __init__(self,
                 parentWin: tk.Toplevel,
                 parent: tk.Frame,
                 logger,
                 validateFn,
                 saveFn
                 ):
        self.parentWin = parentWin
        self.parent = parent
        self.logger = logger
        self.confValidateFn = validateFn
        self.confSaveFn = saveFn
        self.oldJsoObj = None
        self.mainFrame = tk.Frame(self.parent)
        self.fldsFrame = tk.Frame(self.mainFrame)
        self.fldsFrame.pack()
        self.buttFrame = tk.Frame(self.mainFrame)
        self.buttFrame.pack()
        self.saveButt = tk.Button(self.buttFrame,
                                  text="Save",
                                  command=self.save)
        self.saveButt.pack(side=tk.LEFT)

        self.reloadButt = tk.Button(self.buttFrame,
                                    text="Reload",
                                    command=self.reload)

        self.reloadButt.pack(side=tk.LEFT)

        self.guiflds: dict[str, gf.GuiFld] = dict()

        self.guiflds[dd.iface.fld.jId] = dd.iface.createFld(self.fldsFrame)
        self.guiflds[dd.broadCP.fld.jId] = dd.broadCP.createFld(self.fldsFrame)
        self.guiflds[dd.disSub.fld.jId] = dd.disSub.createFld(self.fldsFrame)
        for fld in self.guiflds.values():
            fld.mainFrame.pack(anchor=tk.W, fill="x")

    def show(self, jsonObj: dict):
        self.oldJsoObj = jsonObj
        for guifld in self.guiflds.values():
            guifld.show(jsonObj[guifld.id])

    def save(self):
        isOk = True
        for guifld in self.guiflds.values():
            isOk = isOk and guifld.validate()
        if isOk:
            errTxt, errPtrs = self.confValidateFn()
            if len(errPtrs) != 0:
                self.logger(errTxt)
            else:
                jsoObj = self.confSaveFn()
                self.show(jsoObj)

    def reload(self):
        self.show(self.oldJsoObj)
