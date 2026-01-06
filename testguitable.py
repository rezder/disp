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
        path = "navigation.courseRhumbline.nextPoint.bearingTrue"
        self.rowFrame = tk.Frame(self.window)
        self.rowFrame.pack()
        self.row = gp.Path(self.rowFrame)
        self.row.show(path, self.jsonObj[path])
        if not self.row.validateFlds():
            print("Faild data should be fine")

        path2, jsonObj2 = self.row.get()
        if path2 != path:
            print("failed there should be no change")
        if not gf.compJson(jsonObj2, self.jsonObj[path]):
            print("failed there should be no change")

        self.row.mainFrame.pack()

        self.table2 = self.createTable(gf.FldLabel)
        self.table2.show(self.jsonObj)
        jsonObjDel = dict(self.jsonObj)
        del jsonObjDel["environment.depth.belowTransducer"]
        self.table2.show(jsonObjDel)

        self.table2.mainFrame.pack()
        self.table3 = self.createTable(gf.FldEntry)
        self.table3.mainFrame.pack()
        self.table3.show(jsonObjDel)

        if not self.table3.validate():
            print("Error should be ok")
        else:
            jsonObj, _, _, _ = self.table3.get()
            for k, v in jsonObjDel.items():
                if k not in jsonObj:
                    print("ERrror key is missing: {}".format(k))
                else:
                    if not gf.compJson(v, jsonObjDel[k]):
                        print("Error on key:{}".format(k))

        tab = self.conf.tabsGetTab("Default")
        tabFlds = [PathsFlds.path, TabsFlds.pos]
        self.tabTable = gt.Table(self.window,
                                 self.window,
                                 PathsFlds.path,
                                 tabFlds)
        self.tabTable.bindAllVisFields("<ButtonRelease-1>", self.cb)
        self.tabTable.mainFrame.pack()
        self.tabTable.show(tab)
        tabNew, _, _, _ = self.tabTable.get()
        if not gf.compJson(tab, tabNew):
            print(tab)
            print(tabNew)
            print("Error prime table does not match")
        print(gf.jsonInerJoin(self.alarmsJson, self.pathsJson))
        print(gf.jsonInerJoin(self.bigsJson, self.pathsJson))

        tabFlds = [alarms.pathId, alarms.label, alarms.min,
                   alarms.val, alarms.max, alarms.dis]
        self.tabTable = gt.Table(self.window,
                                 self.window,
                                 alarms.pathId,
                                 tabFlds)
        self.tabTable.mainFrame.pack()

        fldsJson = {alarms.pathId.fld.jId: self.pathsJson}
        self.tabTable.setTabFldsJson(fldsJson)
        self.tabTable.show(self.alarmsJson)

    def createTable(self, classFld):
        sortGuiFldDef = None
        tabFlds: list[gf.GuiFldDef] = list()
        for guiFldDef in self.row.getGuiFldDefs():
            tabFld = guiFldDef.cp()
            tabFld.fldClass = classFld
            if tabFld.isKey:
                sortGuiFldDef = tabFld
            tabFlds.append(tabFld)
        tab = gt.Table(self.window,
                       self.window,
                       sortGuiFldDef,
                       tabFlds)
        tab.bindAllVisFields("<ButtonRelease-1>", self.cb)
        return tab

    def cb(self, path, head, event):
        if head != "pathId":
            print(self.jsonObj[path][head])
        else:
            print(path)

    def start(self):
        self.window.mainloop()


dp = TestTable()
dp.start()
