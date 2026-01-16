import tkinter as tk
import sys

import guijsontable as gt
from flds import alarms_server as alarms
from config import Config


class TestTable:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Test table")
        self.conf = Config(isDefault=True)
        pathsJson, alarmsJson, bigsJson, = self.conf.pathsGet()
        self.pathsJson = pathsJson
        self.alarmsJson = alarmsJson
        self.bigsJson = bigsJson
        self.jsonObj = pathsJson
        self.tabFrame = tk.Frame(self.window)
        self.tabFrame.pack()
        tabFlds = [alarms.pathId, alarms.label, alarms.min,
                   alarms.val, alarms.max, alarms.dis]
        self.tabTable = gt.Table(self.window,
                                 self.tabFrame,
                                 alarms.pathId,
                                 tabFlds,
                                 postChgCb=self.cb)
        self.tabTable.mainFrame.pack()

        fldsJson = {alarms.pathId.fld.jId: self.pathsJson}
        self.tabTable.setTabFldsJson(fldsJson)

        self.tabTable.show(self.alarmsJson)

        key = "environment.depth.belowTransducer"
        print(self.tabTable.getFldVal(alarms.pathId.fld, key))

    def cb(self, pathId, fld):
        if fld is alarms.dis.fld:
            b = self.tabTable.getFldVal(fld, pathId)
            print(b)

    def stop(self):
        self.window.destroy()

    def start(self):
        if len(sys.argv) > 1 and sys.argv[1] == "-t":
            self.window.after(1000, self.stop)
        self.window.mainloop()


dp = TestTable()
dp.start()
