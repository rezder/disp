import tkinter as tk

from gui import BORDER_COLOR, BORDER_WIDTH


class List:

    def __init__(self,
                 parent: tk.Frame,
                 cbTabChg,
                 cbDisable):
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.items: list[Item] = list()
        self.ons = set()
        self.cbTabChg = cbTabChg
        self.cbDisable = cbDisable

    def show(self,
             defaultTab: str,
             ids: dict,
             tabs: list,
             macs: dict):
        self.tabs = tabs
        self.defaultTab = defaultTab
        for c in self.mainFrame.winfo_children():
            c.destroy()
        self.items.clear()

        title = tk.Label(self.mainFrame, text="Displays")
        title.pack()
        for id, tabId in ids.items():
            macAddr = None
            isDisable = False
            if id in macs:
                macObj = macs[id]
                macAddr = macObj["addr"]
                isDisable = macObj["isDisable"]

            r = Item(self.mainFrame,
                     self.cbTabChg,
                     self.cbDisable)
            r.show(id,
                   self.tabs,
                   tabId,
                   macAddr,
                   isDisable)
            r.mainFrame.pack(pady=(0, 5), anchor=tk.W)
            self.items.append(r)

    def newId(self, id: str, macAddr=None):
        isDisable = False
        r = Item(self.mainFrame,
                 self.cbTabChg,
                 self.cbDisable)
        r.show(id,
               self.tabs,
               self.defaultTab,
               macAddr,
               isDisable)
        r.mainFrame.pack(pady=(0, 5), anchor=tk.W)
        self.items.append(r)

    def serverOns(self, ons: set):
        if self.ons != ons:
            for r in self.items:
                found = False
                for o in ons:
                    if r.getId() == o:
                        r.setOnOff(True)
                        found = True
                        break
                if not found:
                    r.setOnOff(False)
            self.ons = ons


class Item:

    def __init__(self,
                 parent: tk.Frame,
                 cbTabChg,
                 cbDisable):

        self.parent = parent
        self.cbTabChg = cbTabChg
        self.mainFrame = tk.Frame(
            self.parent,
            highlightthickness=BORDER_WIDTH,
            highlightbackground=BORDER_COLOR)

        self.idFrame = tk.Frame(self.mainFrame)
        self.idFrame.columnconfigure(1, weight=1)
        self.idFrame.columnconfigure(0, weight=0)
        self.idFrame.pack(fill="x")
        lH = tk.Label(self.idFrame, text="Id:")
        lH.grid(row=0, column=0)
        self.idVar = tk.StringVar()
        lId = tk.Label(self.idFrame, textvariable=self.idVar)
        lId.grid(sticky="e", row=0, column=1)

        self.bleFrame = tk.Frame(self.mainFrame)
        self.bleFrame.pack()

        self.radioFrame = tk.Frame(self.mainFrame,
                                   highlightthickness=BORDER_WIDTH,
                                   highlightbackground=BORDER_COLOR)
        self.radioFrame.pack(anchor=tk.W)
        self.selTabVar = tk.StringVar()

        self.bgColor = self.mainFrame.cget("bg")
        self.selectColor = "blue"
        self.cbDisable = cbDisable

    def show(self,
             id: str,
             tabs: list,
             selectedTab: str,
             macAddr: str,
             isDisable):
        self.idVar.set(id)
        self.isDisableOld = isDisable
        self.oldSelTab = selectedTab
        self.selTabVar.set(self.oldSelTab)

        for c in self.bleFrame.winfo_children():
            c.destroy()
        for c in self.radioFrame.winfo_children():
            c.destroy()

        if macAddr is not None:
            macAddrTxt = "Mac Address:   {}".format(macAddr)
            macVar = tk.StringVar(value=macAddrTxt)
            macLabel = tk.Label(self.bleFrame, textvariable=macVar)
            macLabel.pack(anchor=tk.CENTER)
            v = 0
            if self.isDisableOld:
                v = 1
            self.disableVar = tk.IntVar(value=v)
            self.disableB = tk.Checkbutton(self.bleFrame,
                                           variable=self.disableVar,
                                           onvalue=1,
                                           offvalue=0,
                                           text="Disable",
                                           command=self.checkBoxDisable,
                                           selectcolor="grey10")
            self.disableB.pack(anchor=tk.W)

        for header in tabs:
            r = tk.Radiobutton(
                self.radioFrame,
                text=header,
                selectcolor='grey',
                variable=self.selTabVar,
                value=header,
                command=self.radioCb)
            r.pack(anchor=tk.W)

    def radioCb(self):
        newValue = self.selTabVar.get()
        if not self.cbTabChg(self.idVar.get(), newValue):
            self.selTabVar.set(self.oldSelTab)
        else:
            self.oldSelTab = newValue

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

        if self.cbDisable(self.idVar.get(), newValue):
            self.isDisableOld = newValue
        else:  # reset
            v = 1
            if newValue:
                v = 0
            self.disableVar.set(v)

    def getId(self) -> str:
        return self.idVar.get()
