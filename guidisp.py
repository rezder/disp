import tkinter as tk

from gui import BORDER_COLOR, BORDER_WIDTH
from flds import flds as ff
from flds import fldsDict as fd
from config import Config


class List:

    def __init__(self,
                 parent: tk.Frame,
                 cbTabChg):
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.items: list[Item] = list()
        self.cbTabChg = cbTabChg
        self.viewIds = None
        self.macs = None

    def show(self):
        for c in self.mainFrame.winfo_children():
            c.destroy()
        self.items.clear()

        title = tk.Label(self.mainFrame, text=fd.displays.header)
        title.pack()

    def newId(self, dispId: str, viewId: str):
        r = Item(self.mainFrame,
                 self.cbTabChg)
        macAddr = None
        if dispId in self.macs:
            macAddr = self.macs[dispId][ff.addr.jId]
        r.show(dispId,
               self.viewIds,
               viewId,
               macAddr)
        r.mainFrame.pack(pady=(0, 5), anchor=tk.W)
        self.items.append(r)

    def serverOnOff(self, isOn: bool, rconf: Config):
        if isOn:
            self.viewIds = rconf.viewsGetIds()
            self.macs = rconf.dispGetBles()
        else:
            self.viewIds = None
            self.macs = None
            self.show()

    def displayOns(self, dispView: dict[str, str]):
        for dispId, viewId in dispView.items():
            found = False
            for r in self.items:
                if r.getId() == dispId:
                    found = True
                    r.setSelectedView(viewId)
                    break
            if not found:
                self.newId(dispId, viewId)


class Item:

    def __init__(self,
                 parent: tk.Frame,
                 cbTabChg):

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

    def show(self,
             id: str,
             tabs: list,
             selectedTab: str,
             macAddr: str):
        self.idVar.set(id)
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

        for header in tabs:
            r = tk.Radiobutton(
                self.radioFrame,
                text=header,
                selectcolor='grey',
                variable=self.selTabVar,
                value=header,
                command=self.radioCb)
            r.pack(anchor=tk.W)

    def setSelectedView(self, viewId: str):
        self.selTabVar.set(viewId)
        self.oldSelTab = viewId

    def radioCb(self):
        newValue = self.selTabVar.get()
        if not self.cbTabChg(self.idVar.get(), newValue):
            self.selTabVar.set(self.oldSelTab)
        else:
            self.oldSelTab = newValue

    def getId(self) -> str:
        return self.idVar.get()
