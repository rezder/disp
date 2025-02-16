import tkinter as tk
import guijson as gt
import units


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
                "largeValue": 999,
                "largePath": "1"
            },
            "1": {
                "decimals": 1,
                "units": 0,
                "dispUnits": 1,
                "label": "DIS",
                "bufSize": 0,
                "bufFreq": 0
            }
        }

        conv = {"path": str,
                "minPeriod": int,
                "decimals": int,
                "units": units.shortTxt,
                "dispUnits": units.shortTxt,
                "label": str,
                "bufSize": int,
                "bufFreq": int,
                "largeValue": int,
                "largePath": str
                }

        self.table = gt.Table(self.window,
                              self.jsonObj,
                              "path",
                              "path",
                              conv,
                              self.cb)
        self.table.show(self.jsonObj)
        self.table.mainFrame.pack()

    def cb(self, path, head):
        if head != "path":
            print(self.jsonObj[path][head])
        else:
            print(path)

    def start(self):
        self.window.mainloop()


dp = TestTable()
dp.start()
