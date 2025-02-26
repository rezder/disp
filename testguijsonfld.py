import tkinter as tk
import guiflds as gf
import guijsondef as gd
import units
from config import Config
from flds import paths


def createFldDefs() -> dict[str, gd.GuiFld]:
    flds: dict[str, gd.GuiFld] = dict()
    jf = gd.JsonFld("entryInt",
                    "Long Int",
                    "Sh Int",
                    str,
                    int,
                    "e"
                    )
    flds[jf.jsonHead] = gd.GuiFld(jf, 10, 5, gf.FldEntry)

    jf = gd.JsonFld("entryStr",
                    "Long Str",
                    "Sh Str",
                    str,
                    gf.strJson,
                    "w"
                    )
    flds[jf.jsonHead] = gd.GuiFld(jf, 8, 5, gf.FldEntry)
    flds["manda"] = gd.GuiFld(jf, 8, 5, gf.FldEntry, isMan=False)

    jf = gd.JsonFld("options",
                    "Long options",
                    "Opts",
                    units.shortTxt,
                    units.noShort,
                    "w"
                    )
    flds[jf.jsonHead] = gd.GuiFld(jf, 4, 5, gf.FldOpt,
                                  options=units.all(),
                                  defaultVal=units.m
                                  )
    jf = gd.JsonFld("label",
                    "test4Label",
                    "label",
                    str,
                    str,
                    "w")
    flds[jf.jsonHead] = gd.GuiFld(jf, 15, 5, gf.FldLabel)

    conf = Config(isDefault=True)

    tabsJson = conf.getTabsJson()
    jf = gd.JsonFld("jsonTabs",
                    "Json Tabs",
                    "Tabs",
                    str,
                    str,
                    "e"
                    )
    flds[jf.jsonHead] = gd.GuiFld(jf, 10, 5, gf.FldOptJson,
                                  optJson=tabsJson,
                                  optJsonHead=None,
                                  defaultVal=("Default", {})
                                  )
    pathsJson = conf.getPathsJson()
    key = "DBT"
    v = pathsJson["environment.depth.belowTransducer"]
    jf = gd.JsonFld("jsonPaths",
                    "Json Paths",
                    "Paths",
                    str,
                    str,
                    "e"
                    )
    flds[jf.jsonHead] = gd.GuiFld(jf, 10, 5, gf.FldOptJson,
                                  optJson=pathsJson,
                                  optJsonHead="label",
                                  defaultVal=((key, v))
                                  )
    return flds


class TestFlds:

    def __init__(self):
        self.fldDefs = createFldDefs()
        self.flds: dict[str, gf.Fld] = dict()
        self.window = tk.Tk()
        self.window.title("Test table")

        self.testFldEntry()

        self.testFldOpt()

        self.testFldJsonOpt()

        self.testFldLabel()
        self.testPathsFlds()

    def testPathsFlds(self):
        paths.dec
        key = "pathsDec"
        fld = gf.createFld(self.window, paths.dec)
        self.flds[key] = fld
        fld.mainFrame.pack(fill="x")
        fld.show(3)

    def testFldOpt(self):
        key = "options"
        fld = gf.createFld(self.window, self.fldDefs[key])
        self.flds[key] = fld
        fld.mainFrame.pack(fill="x")

        fld.show(units.ms)
        fld.setError(True)
        fld.removeOpt(20)
        fld.addOpt(20)
        lx = False
        try:
            fld.replaceOpts([1, 10, 20])
        except ValueError:
            lx = True
        if not lx:
            print("faild no value error")

        fld.replaceOpts([0, 1, 10, 20])

        print(fld.get())
        print(fld.get())

    def testFldEntry(self):
        key = "entryInt"
        fld = gf.createFld(self.window, self.fldDefs[key])
        fld.mainFrame.pack(fill="x")
        self.flds[key] = fld

        fld.show(4)
        fld.setError(True)

        key = "entryStr"
        fld = gf.createFld(self.window, self.fldDefs[key])
        fld.mainFrame.pack(fill="x")
        self.flds[fld.id] = fld

        fld.show("")
        fld.validate()

        key = "manda"
        fld = gf.createFld(self.window, self.fldDefs[key])
        fld.mainFrame.pack(fill="x")
        self.flds[key] = fld

        fld.show("")
        fld.validate()
        lx = True
        try:
            fld.get()
        except ValueError:
            lx = False
        if lx:
            print("Failed ValueError raise on str")

    def testFldLabel(self):
        key = "label"
        fld = gf.createFld(self.window, self.fldDefs[key])
        fld.mainFrame.pack(fill="x")
        self.flds[key] = fld

        fld.show("asdfh34j")
        fld.validate()

        jsonDef = self.fldDefs["label"].jsonFld
        key = "head"
        fld = gf.FldLabelHead(self.window, jsonDef, 6)
        fld.mainFrame.pack(fill="x")
        self.flds[key] = fld

        fld.fldLabelOut.configure(bg="blue")
        fld.mainFrame.pack(fill="x")

    def testFldJsonOpt(self):

        key = "jsonTabs"
        df = self.fldDefs[key]
        tabsJson = df.optJson
        fld = gf.createFld(self.window, self.fldDefs[key])
        fld.mainFrame.pack(fill="x")
        self.flds[key] = fld

        fld.show(("Default", tabsJson["Default"]))
        fld.validate()

        key = "jsonPaths"
        df = self.fldDefs[key]
        pathsJson = df.optJson
        fld = gf.createFld(self.window, self.fldDefs[key])
        fld.mainFrame.pack(fill="x")
        self.flds[key] = fld

        newId = "navigation.courseRhumbline.nextPoint.distance"
        defaultId = "environment.depth.belowTransducer"
        k, v = fld.get()
        if k != defaultId:
            print("Error")
        fld.show((newId, pathsJson[newId]))
        fld.validate()
        k, v = fld.get()
        if k != newId:
            print("Error")

    def start(self):
        self.window.mainloop()


dp = TestFlds()
dp.start()
