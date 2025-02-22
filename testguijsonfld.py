import tkinter as tk
import guijson as gt
import units
from config import Config

class TestFlds:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Test table")
        fldDef = gt.FldDef("test",
                           10,
                           True,
                           str,
                           int,
                           "e")

        self.fld = gt.FldEntry(self.window, fldDef)
        self.fld.show(4)
        self.fld.setError(True)
        self.fld.mainFrame.pack(fill="x")
        fldDef = gt.FldDef("test2",
                           10,
                           True,
                           str,
                           gt.strJson,
                           "w")
        self.fld2 = gt.FldEntry(self.window, fldDef)
        self.fld2.show("")
        self.fld2.validate()
        self.fld2.mainFrame.pack(fill="x")
        fldDef = gt.FldDef("test3",
                           10,
                           False,
                           str,
                           gt.strJson,
                           "w")
        self.fld3 = gt.FldEntry(self.window, fldDef)
        self.fld3.show("")
        self.fld3.validate()
        lx = True
        try:
            self.fld3.get()
        except ValueError:
            lx = False
        if lx:
            print("Failed ValueError raise on str")

        self.fld3.mainFrame.pack(fill="x")

        fldDef = gt.FldDef("Units",
                           4,
                           True,
                           units.shortTxt,
                           units.noShort,
                           "w",
                           units.m)

        self.fldOpt = gt.FldOpt(self.window, fldDef, units.all())
        self.fldOpt.show(units.ms)
        self.fldOpt.setError(True)
        self.fldOpt.removeOpt(20)
        self.fldOpt.addOpt(20)
        lx = False
        try:
            self.fldOpt.replaceOpts([1, 10, 20])
        except ValueError:
            lx = True

        if not lx:
            print("faild no value error")

        self.fldOpt.replaceOpts([0, 1, 10, 20])
        self.fldOpt.mainFrame.pack(fill="x")
        print(self.fldOpt.get())
        print(self.fld.get())
        self.testFldJsonOpt()
        self.testFldLabel()

    def testFldLabel(self):
        fldDef = gt.FldDef("test4Label",
                           15,
                           True,
                           str,
                           str,
                           "w")
        self.fldL = gt.FldLabel(self.window, fldDef)
        self.fldL.show("asdfh34j")
        self.fldL.validate()
        self.fldL.mainFrame.pack(fill="x")

        fldDef = gt.FldDef("test4Label",
                           15,
                           True,
                           str,
                           str,
                           "w")

        self.fldLNoHead = gt.FldLabel(self.window, fldDef, noCap=True)
        self.fldLNoHead.fldLabelOut.configure(bg="green")
        self.fldLNoHead.show("No header")
        self.fldLNoHead.validate()
        self.fldLNoHead.mainFrame.pack(fill="x")

    def testFldJsonOpt(self):
        conf = Config(isDefault=True)
        tabsJson = conf.getTabsJson()
        pathsJson = conf.getPathsJson()

        fldDef = gt.FldDef("test4JsonOpt",
                           10,
                           True,
                           str,
                           str,
                           "e",
                           default="Default")

        self.fldOptJson = gt.FldOptJson(self.window,
                                        fldDef,
                                        tabsJson,
                                        dpHeadJson="tab",
                                        keyHeadJson="tab"
                                        )
        self.fldOptJson.show(("Default", tabsJson["Default"]))
        self.fldOptJson.validate()
        self.fldOptJson.mainFrame.pack(fill="x")

        fldDef = gt.FldDef("test4JsonOptLabel",
                           10,
                           True,
                           str,
                           str,
                           "e",
                           default="DBT")

        self.fldOptJsonLabel = gt.FldOptJson(self.window,
                                             fldDef,
                                             pathsJson,
                                             dpHeadJson="label",
                                             keyHeadJson="tab"

                                             )
        id = "environment.depth.belowTransducer"
        self.fldOptJsonLabel.show((id, pathsJson[id]))
        self.fldOptJsonLabel.validate()
        self.fldOptJsonLabel.mainFrame.pack(fill="x")
        path2, item2 = self.fldOptJsonLabel.get()
        if path2 != "environment.depth.belowTransducer":
            print("Error")

    def start(self):
        self.window.mainloop()


dp = TestFlds()
dp.start()
