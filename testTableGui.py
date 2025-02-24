import tkinter as tk
import guijson as gt
import guipaths as gp
import guijson as gj


def cb(path, head):
    print(path)
    print(head)


class TestTable:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Test table")
        self.jsonObj = {
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
        path = "navigation.courseRhumbline.nextPoint.bearingTrue"
        self.rowFrame = tk.Frame(self.window)
        self.rowFrame.pack()
        self.row = gp.Path(self.rowFrame)
        self.row.show(path, self.jsonObj[path])
        print()
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

        self.table = gt.Table(self.window,
                              len(self.jsonObj),
                              sortFldDef,
                              self.cb,
                              self.row.getFldDefs())
        self.table.show(self.jsonObj)
        self.table.mainFrame.pack()

# No header change is towork must make jsonfld to flddef 
#        self.table2 = gt.Table(self.window,
#                               self.jsonObj,
#                               "path",
#                               "path",
#                               conv,
#                              self.cb
#                               )
#       self.table2.show(self.jsonObj)
#      self.table2.mainFrame.pack()

    def cb(self, path, head):
        if head != "path":
            print(self.jsonObj[path][head])
        else:
            print(path)

    def start(self):
        self.window.mainloop()


dp = TestTable()
dp.start()
