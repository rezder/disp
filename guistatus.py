import tkinter as tk
import tkinter.scrolledtext as scrolledtext

import cmd
import state


class State:

    def __init__(self, parent: tk.Frame):
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.stateVar = tk.StringVar()
        self.cmdVar = tk.StringVar()
        self.bgColor = self.parent.cget("bg")
        self.stateLabel = tk.Label(self.mainFrame, textvariable=self.stateVar)
        self.stateLabel.grid(row=0, column=0)
        self.cmdLabel = tk.Label(self.mainFrame, textvariable=self.cmdVar)
        self.cmdLabel.grid(row=0, column=2, sticky=tk.E)
        s = tk.Label(self.mainFrame, text=":")
        s.grid(row=0, column=1, sticky=tk.NE)

    def updStateCmd(self, c, st):
        self.cmdVar.set(cmd.shortTxt(c))
        self.stateVar.set(state.shortTxt(st))
        if st == state.broke:
            self.stateLabel.config(bg="red")
        else:
            self.stateLabel.config(bg=self.bgColor)


class Button:

    def __init__(self, window, startCb, stopCb, stoppedCb):
        self.butVar = tk.StringVar(value="start")
        self.startCb = startCb
        self.stopCb = stopCb
        self.stoppedCb = stoppedCb
        self.subOnOffList = list()
        self.window = window

    def create(self, frame):
        self.button = tk.Button(frame,
                                textvariable=self.butVar,
                                command=self.butCb)

    def getButton(self) -> tk.Button:
        return self.button

    def butCb(self):
        if self.butVar.get() == "start":
            if self.startCb():
                self.butVar.set("stop")
                self.executeOnOff(True)
        else:
            if self.stopCb():
                self.button.config(state=tk.DISABLED)
                self.window.after(1000, self.butCbStopCheck)

    def butCbStopCheck(self):
        print("call clean check")
        if self.stoppedCb():
            self.butVar.set("start")
            self.button.config(state=tk.NORMAL)
            self.executeOnOff(False)
        else:
            self.window.after(2000, self.butCbStopCheck)

    def subscribeOnOff(self, fn):
        self.subOnOffList.append(fn)

    def executeOnOff(self, isOn: bool):
        for f in self.subOnOffList:
            f(isOn)


class Status:
    def __init__(self, parent: tk.Frame, stButton: Button, statusCb):
        self.parent = parent
        self.statusCb = statusCb
        self.mainFrame = tk.Frame(self.parent)
        self.bottomFrame = tk.Frame(self.mainFrame)
        self.startButton = stButton
        self.subOnsList = list()
        self.subAlarmsList = list()
        self.statusTbox = scrolledtext.ScrolledText(self.mainFrame, undo=True)
        self.statusTbox['font'] = ('consolas', '12')
        self.statusTbox.pack(fill=tk.BOTH, expand=True)
        heading = "Display server"

        self.statusTbox.insert(tk.END, heading)
        self.startButton.create(self.bottomFrame)
        self.startButton.getButton().pack(side=tk.LEFT)

        self.stateGui = State(self.bottomFrame)
        self.stateGui.mainFrame.pack(side=tk.RIGHT)

        self.bottomFrame.pack(expand=True, fill=tk.BOTH)

    def write(self, txt):
        self.statusTbox.insert(tk.END, "\n"+txt)

    def subscribeOns(self, fn):
        self.subOnsList.append(fn)

    def subscribeAlarms(self, fn):
        self.subAlarmsList.append(fn)

    def executeOns(self, ons: set):
        for f in self.subOnsList:
            f(ons)

    def executeAlarms(self, alarms: list):
        for f in self.subAlarmsList:
            f(alarms)

    def updateStatus(self):
        ok, txt, st, c, ons, dms = self.statusCb()
        if txt != "":
            self.statusTbox.insert(tk.END, txt)
        if ok:
            self.stateGui.updStateCmd(c, st)
            self.executeOns(ons)
            self.executeAlarms(dms)
