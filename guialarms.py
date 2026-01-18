import tkinter as tk

from guijsontable import Table
from flds import alarms_server as alarms
from config import Config
from gui import BORDER_COLOR, BORDER_WIDTH
from guiflds import Fld
from status import AlarmMsg
from flds import fldsDict as fd


class Alarms:
    def __init__(self, parentWin: tk.Toplevel, parent: tk.Frame, disActFn):
        self.disActFn = disActFn
        self.parentWin = parentWin
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        title = tk.Label(self.mainFrame, text=fd.alarms.header)
        title.pack()
        self.bgColor = self.parent.cget("bg")
        tabFlds = [alarms.pathId, alarms.label, alarms.min,
                   alarms.val, alarms.max, alarms.dis]
        self.tab = Table(self.parentWin,
                         self.mainFrame,
                         alarms.pathId,
                         tabFlds,
                         postChgCb=self.checkMarkCb)
        self.tab.mainFrame.config(highlightbackground=BORDER_COLOR)
        self.tab.mainFrame.config(highlightthickness=BORDER_WIDTH)
        self.tab.mainFrame.pack()

    def checkMarkCb(self, pathId: str, fld: Fld):
        if fld is alarms.dis.fld:
            isDis = self.tab.getFldVal(fld, pathId)
            label = self.tab.getFldVal(alarms.label.fld, pathId)
            self.disActFn(pathId, label, isDis)

    def serverOnOff(self, isOn: bool, rconf: Config):
        if isOn:
            pathsJson, alarmsJson, _ = rconf.pathsGet()

            fldsJson = {alarms.pathId.fld.jId: pathsJson}
            self.tab.setTabFldsJson(fldsJson)
            self.tab.show(alarmsJson)
        else:
            self.tab.removeRows()

    def alarmMsg(self, msgs: list[AlarmMsg]):
        for msg in msgs:
            if msg.isOn:
                self.tab.setFldVal(alarms.val.fld, msg.path, msg.value)
                self.tab.getFld(alarms.val.fld, msg.path).setError(True)
            else:
                self.tab.getFld(alarms.val.fld, msg.path).setError(False)
                self.tab.getFld(alarms.val.fld, msg.path).clear()
