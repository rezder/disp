import tkinter as tk
import guipaths as gp
import guijson as gj
import guijsontable as gt


def cb(path, head):
    print(path)
    print(head)


paths = {
    "environment.depth.belowTransducer": {
        "minPeriod": 1000,
        "decimals": 1,
        "units": 0,
        "dispUnits": 0,
        "label": "DBT",
        "bufSize": 4,
        "bufFreq": 4
    },
    "navigation.speedOverGround": {
        "minPeriod": 1000,
        "decimals": 1,
        "units": 10,
        "dispUnits": 11,
        "label": "SOG",
        "bufSize": 4,
        "bufFreq": 4
    },
    "navigation.courseOverGroundTrue": {
        "minPeriod": 1000,
        "decimals": 0,
        "units": 20,
        "dispUnits": 21,
        "label": "COG",
        "bufSize": 4,
        "bufFreq": 4
    },
    "navigation.speedThroughWater": {
        "minPeriod": 2000,
        "decimals": 1,
        "units": 10,
        "dispUnits": 11,
        "label": "STW",
        "bufSize": 0,
        "bufFreq": 0
    },
    "navigation.courseRhumbline.crossTrackError": {
        "minPeriod": 4000,
        "decimals": 0,
        "units": 0,
        "dispUnits": 0,
        "label": "XTE",
        "bufSize": 0,
        "bufFreq": 0
    },
    "navigation.courseRhumbline.nextPoint.bearingTrue": {
        "minPeriod": 1000,
        "decimals": 0,
        "units": 20,
        "dispUnits": 21,
        "label": "BEA",
        "bufSize": 4,
        "bufFreq": 4
    },
    "navigation.courseRhumbline.nextPoint.distance": {
        "minPeriod": 4000,
        "decimals": 0,
        "units": 0,
        "dispUnits": 0,
        "label": "DIS",
        "bufSize": 0,
        "bufFreq": 0,
        "bigValue": 999,
        "bigDispUnit": 1,
        "bigDecimals": 1
    }
}


class TestTable:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Test table")
        self.jsonObj = paths
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

        if not gj.compJson(jsonObj2, self.jsonObj[path]):
            print("failed there should be no change")

        self.row.mainFrame.pack()

        sortFldDef = None
        for fldDef in self.row.getFldDefs():
            if fldDef.isKey:
                sortFldDef = fldDef

        self.table = gj.Table(self.window,
                              len(self.jsonObj),
                              sortFldDef,
                              self.cb,
                              self.row.getFldDefs())
        self.table.show(self.jsonObj)
        self.table.mainFrame.pack()

        self.table2 = self.createTable(gj.FldLabel)
        self.table2.show(self.jsonObj)
        jsonObjDel = dict(self.jsonObj)
        del jsonObjDel["environment.depth.belowTransducer"]
        self.table2.show(jsonObjDel)

        self.table2.mainFrame.pack()
        self.table3 = self.createTable(gj.FldEntry)
        self.table3.mainFrame.pack()
        self.table3.show(jsonObjDel)

        if not self.table3.validate():
            print("Error should be ok")
        else:
            jsonObj, dels, chgkeys = self.table3.get()
            for k, v in jsonObjDel.items():
                if k not in jsonObj:
                    print("ERrror key is missing: {}".format(k))
                else:
                    if not gj.compJson(v, jsonObjDel[k]):
                        print("Error on key:{}".format(k))

    def createTable(self, classFld):
        sortTabFldDef = None
        tabFlds = list()
        widths = [45, 8, 8, 6, 7, 5, 10, 10, 7, 7, 8, 8, 11]
        i = 0
        for id, fld in self.row.getFlds().items():
            fldDef = fld.fldDef
            width = widths[i]
            isMan = fld.isMan
            if fld.id == "bigDispUnit":
                isMan = False
            tabFld = gt.TabFldDef(fldDef, width, classFld, isMan=isMan)
            if fldDef.isKey:
                sortTabFldDef = tabFld
            tabFlds.append(tabFld)
            i = i + 1

        return gt.Table(self.window,
                        sortTabFldDef,
                        self.cb,
                        tabFlds)

    def cb(self, path, head):
        if head != "path":
            print(self.jsonObj[path][head])
        else:
            print(path)

    def start(self):
        self.window.mainloop()


dp = TestTable()
dp.start()
