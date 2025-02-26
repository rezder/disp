import tkinter as tk
import guipaths as gp
import guiflds as gf
import guijsondef as gdef
import guijsontable as gt


def cb(path, head):
    print(path)
    print(head)


paths = {"environment.depth.belowTransducer": {
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
            jsonObj, dels, chgkeys = self.table3.get()
            for k, v in jsonObjDel.items():
                if k not in jsonObj:
                    print("ERrror key is missing: {}".format(k))
                else:
                    if not gf.compJson(v, jsonObjDel[k]):
                        print("Error on key:{}".format(k))

    def createTable(self, classFld):
        sortGuiFldDef = None
        tabFlds: list[gdef.GuiFld] = list()
        for guiFldDef in self.row.getGuiFldDefs():
            tabFld = guiFldDef.cp()
            tabFld.fldClass = classFld
            if tabFld.jsonFld.isKey:
                sortGuiFldDef = tabFld
            tabFlds.append(tabFld)

        return gt.Table(self.window,
                        sortGuiFldDef,
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
