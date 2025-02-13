import tkinter as tk
from gui import BORDER_COLOR, BORDER_WIDTH


class List:

    def __init__(self,
                 parent: tk.Frame,
                 ids: dict,
                 values: list,
                 macs: dict,
                 defaultVal: str,
                 cbTabChg,
                 cbDisable):
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.radios = list()
        self.ons = set()
        self.cbTabChg = cbTabChg
        self.cbDisable = cbDisable
        self.values = values
        self.ids = ids
        self.defaultVal = defaultVal
        self.macs = macs

    def create(self):
        title = tk.Label(self.mainFrame, text="Displays")
        title.pack()
        for id, tabId in self.ids.items():
            macAddr = None
            isDisable = False
            if id in self.macs:
                macObj = self.macs[id]
                macAddr = macObj["addr"]
                isDisable = macObj["isDisable"]

            r = Item(self.mainFrame,
                     id,
                     self.values,
                     tabId,
                     macAddr,
                     isDisable,
                     self.cbTabChg,
                     self.cbDisable)
            r.create()
            r.mainFrame.pack(pady=(0, 5), anchor=tk.W)
            self.radios.append(r)

    def newId(self, id: str, macAddr=None):
        isDisable = False
        r = Item(self.mainFrame,
                 id,
                 self.values,
                 self.defaultVal,
                 macAddr,
                 isDisable,
                 self.cbTabChg,
                 self.cbDisable)
        r.create()
        r.mainFrame.pack(pady=(0, 5), anchor=tk.W)
        self.radios.append(r)

    def serverOns(self, ons: set):
        if self.ons != ons:
            for r in self.radios:
                found = False
                for o in ons:
                    if r.id == o:
                        r.setOnOff(True)
                        found = True
                        break
                if not found:
                    r.setOnOff(False)
            self.ons = ons


class Item:

    def __init__(self,
                 parent: tk.Frame,
                 id: str,
                 values: list,
                 currentValue: str,
                 macAddr: str,
                 isDisable,
                 cbTabChg,
                 cbDisable):

        self.parent = parent
        self.id = id
        self.oldValue = currentValue
        self.valueVar = None
        self.radioFrame = None
        self.values = values
        self.cbTabChg = cbTabChg
        self.mainFrame = tk.Frame(
            self.parent,
            highlightthickness=BORDER_WIDTH,
            highlightbackground=BORDER_COLOR)
        self.bgColor = self.mainFrame.cget("bg")
        self.selectColor = "blue"
        self.macAddr = macAddr
        self.isDisableOld = isDisable
        self.idLabel = None
        self.cbDisable = cbDisable

    def create(self):
        f = tk.Frame(self.mainFrame)
        f.columnconfigure(1, weight=1)
        f.columnconfigure(0, weight=0)
        f.pack(fill="x")
        lH = tk.Label(f, text="Id:")
        lH.grid(row=0, column=0)
        lId = tk.Label(f, text=self.id)
        lId.grid(sticky="e", row=0, column=1)

        if self.macAddr is not None:
            macAddrTxt = "Mac Address:   {}".format(self.macAddr)
            macVar = tk.StringVar(value=macAddrTxt)
            macLabel = tk.Label(self.mainFrame, textvariable=macVar)
            macLabel.pack(anchor=tk.CENTER)
            v = 0
            if self.isDisableOld:
                v = 1
            self.disableVar = tk.IntVar(value=v)
            self.disableB = tk.Checkbutton(self.mainFrame,
                                           variable=self.disableVar,
                                           onvalue=1,
                                           offvalue=0,
                                           text="Disable",
                                           command=self.checkBoxDisable,
                                           selectcolor="grey10")
            self.disableB.pack(anchor=tk.W)

        self.valueVar = tk.StringVar(value=self.oldValue)
        self.radioFrame = tk.Frame(self.mainFrame,
                                   highlightthickness=BORDER_WIDTH,
                                   highlightbackground=BORDER_COLOR)
        self.radioFrame.pack(anchor=tk.W)
        for header in self.values:
            r = tk.Radiobutton(
                self.radioFrame,
                text=header,
                selectcolor='grey',
                variable=self.valueVar,
                value=header,
                command=self.radioCb)
            r.pack(anchor=tk.W)

    def radioCb(self):
        newValue = self.valueVar.get()
        if not self.cbTabChg(self.id, newValue):
            self.valueVar.set(self.oldValue)
        else:
            self.oldValue = newValue

    def setOnOff(self, on: bool):
        if on is True:
            self.mainFrame.config(highlightbackground=self.selectColor)
            self.mainFrame.config(highlightthickness=4)

        else:
            self.mainFrame.config(highlightbackground=BORDER_COLOR)
            self.mainFrame.config(highlightthickness=BORDER_WIDTH)

    def checkBoxDisable(self):
        newValue = False
        if self.disableVar.get() == 1:
            newValue = True

        if self.cbDisable(self.id, newValue):
            self.isDisableOld = newValue
        else:  # reset
            v = 1
            if newValue:
                v = 0
            self.disableVar.set(v)
