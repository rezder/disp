import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from functools import partial

import cmd
import state
from config import Config


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
            isOk, rconf = self.startCb()
            if isOk:
                self.butVar.set("stop")
                self.executeOnOff(True, rconf)
        else:
            if self.stopCb():
                self.button.config(state=tk.DISABLED)
                self.window.after(1000, self.butCbStopCheck)

    def butCbStopCheck(self):
        print("call clean check")
        if self.stoppedCb():
            self.butVar.set("start")
            self.button.config(state=tk.NORMAL)
            self.executeOnOff(False, None)
        else:
            self.window.after(2000, self.butCbStopCheck)

    def subscribeOnOff(self, fn):
        self.subOnOffList.append(fn)

    def executeOnOff(self, isOn: bool, rconf: Config):
        for f in self.subOnOffList:
            f(isOn, rconf)


class Status:
    def __init__(self,
                 parentWin: tk.Toplevel,
                 parent: tk.Frame,
                 stButton: Button,
                 statusCb):
        self.parentWin = parentWin
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
        menu = self.createCopyPaste(self.statusTbox, self.parentWin)
        self.statusTbox.bind("<Button-3><ButtonRelease-3>",
                             partial(popMenuUp, menu))
        heading = "Display server"
        self.statusTbox.insert(tk.END, heading)
        self.startButton.create(self.bottomFrame)
        self.startButton.getButton().pack(side=tk.LEFT)

        self.stateGui = State(self.bottomFrame)
        self.stateGui.mainFrame.pack(side=tk.RIGHT)

        self.bottomFrame.pack(expand=True, fill=tk.BOTH)

    def createCopyPaste(self, widget: tk.Widget, win) -> tk.Menu:
        popMenu = tk.Menu(win, tearoff=0)
        popMenu.add_command(label="Cut",
                            command=lambda: widget.event_generate("<<Cut>>"))
        popMenu.add_command(label="Copy",
                            command=lambda: widget.event_generate("<<Copy>>"))
        popMenu.add_command(label="Paste",
                            command=lambda: widget.event_generate("<<Paste>>"))
        popMenu.add_separator()
        popMenu.add_command(label="Select All",
                            command=partial(selectAll, widget))
        popMenu.bind("<FocusOut>", partial(popMenuUnPost, popMenu))
        return popMenu

    def write(self, txt):
        self.statusTbox.insert(tk.END, "\n"+txt)

    def subscribeOns(self, fn):
        self.subOnsList.append(fn)

    def subscribeAlarms(self, fn):
        self.subAlarmsList.append(fn)

    def executeOns(self, ons: dict):
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


def popMenuUp(menu: tk.Menu, event: tk.Event):
    try:
        menu.tk_popup(event.x_root,
                      event.y_root)
    finally:
        menu.grab_release()


def popMenuUnPost(menu: tk.Menu, event):
    menu.unpost()


def selectAll(widget: tk.Widget):
    if isinstance(widget, tk.Text):
        w: tk.Text = widget
        w.tag_add(tk.SEL, "1.0", tk.END)
    else:
        raise Exception("Type:{} not implement".format(type(widget)))
