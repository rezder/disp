import tkinter as tk
from functools import partial

from status import AlarmMsg
from gui import BORDER_COLOR, BORDER_WIDTH
from flds import flds as ff
from flds import fldsDict as fd
from config import Config


class Alarms:
    def __init__(self, parent: tk.Frame, disActFn):
        self.disActFn = disActFn
        self.pathsGui = dict()
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        title = tk.Label(self.mainFrame, text=fd.alarms.jId)
        title.pack()
        self.tabFrame = tk.Frame(self.mainFrame,
                                 highlightthickness=BORDER_WIDTH,
                                 highlightbackground=BORDER_COLOR)
        self.bgColor = self.parent.cget("bg")
        self.tabFrame.pack()

    def show(self):
        self.pathsGui.clear()
        for c in self.tabFrame.winfo_children():
            c.destroy()
        # Headers
        la = tk.Label(self.tabFrame, text=ff.label.shortHeader)
        la.grid(row=0, column=0)
        la = tk.Label(self.tabFrame, text=ff.min.shortHeader, width=6)
        la.grid(row=0, column=1)
        la = tk.Label(self.tabFrame, text="Value")  # not a json fld
        la.grid(row=0, column=2)
        la = tk.Label(self.tabFrame, text=ff.max.shortHeader, width=6)
        la.grid(row=0, column=3)
        la = tk.Label(self.tabFrame, text="Disable")  # not a json fld maybe
        #  it should be.
        la.grid(row=0, column=4)

    def checkFn(self, path, label, checkVar: tk.IntVar):
        if checkVar.get() == 1:
            self.disActFn(path, label, True)
        else:
            self.disActFn(path, label, False)

    def alarmMsg(self, msgs: list[AlarmMsg]):
        for msg in msgs:
            (valueVar, valueLabel, checkBox) = self.pathsGui[msg.path]
            if msg.isOn:
                vTxt = "{:.1f}".format(msg.value)
                valueVar.set(vTxt)
                valueLabel.config(bg="red")
            else:
                valueVar.set("")
                valueLabel.config(bg=self.bgColor)

    def serverOnOff(self, isOn: bool, rconf: Config):
        if isOn:
            pathsJson, alarmsJson, _ = rconf.pathsGet()
            # Table Data
            i = 1
            for (path, alarmJson) in alarmsJson.items():
                pathJson = pathsJson[path]
                label = tk.Label(self.tabFrame, text=pathJson[ff.label.jId])
                label.grid(row=i, column=0)
                txt = ""
                if ff.min.jId in alarmJson:
                    txt = alarmJson[ff.min.jId]
                minl = tk.Label(self.tabFrame, text=txt)
                minl.grid(row=i, column=1)
                valueVar = tk.StringVar(value="")
                vl = tk.Label(self.tabFrame, textvariable=valueVar)
                vl.grid(row=i, column=2)
                txt = ""
                if ff.max.jId in alarmJson:
                    txt = alarmJson[ff.max.jId]
                maxl = tk.Label(self.tabFrame, text=txt)
                maxl.grid(row=i, column=3)
                checkVar = tk.IntVar(value=0)
                fn = partial(self.checkFn,
                             path, pathJson[ff.label.jId], checkVar)
                checkB = tk.Checkbutton(self.tabFrame,
                                        variable=checkVar,
                                        onvalue=1,
                                        offvalue=0,
                                        command=fn,
                                        # selectcolor="grey10",
                                        state=tk.NORMAL)
                txtcolor: str = self.tabFrame.cget("bg")
                if int(txtcolor[1:3], 16) < 100:
                    checkB.config(selectcolor="#1a1a1a")
                checkB.grid(row=i, column=4)
                self.pathsGui[path] = (valueVar, vl, checkB)
                i = i + 1
        else:
            self.show()
