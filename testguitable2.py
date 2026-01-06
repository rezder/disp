import tkinter as tk

import guipaths as gp
import guiflds as gf
import guijsontable as gt
from flds import paths as PathsFlds
from flds import tabs as TabsFlds
from flds import alarms_server as alarms
from config import Config


def cb(path, head, event):
    print(path)
    print(head)


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
                                 tabFlds)
        self.tabTable.mainFrame.pack()
        fldsJson = {alarms.pathId.fld.jId: self.pathsJson}
        self.tabTable.setTabFldsJson(fldsJson)
        print(self.alarmsJson)
        self.tabTable.show(self.alarmsJson)
        key = "environment.depth.belowTransducer"
        print(self.tabTable.getFld(alarms.pathId.fld, key))

    def cb(self, path, head, event):
        if head != "pathId":
            print(self.jsonObj[path][head])
        else:
            print(path)

    def start(self):
        self.window.mainloop()


dp = TestTable()
dp.start()
