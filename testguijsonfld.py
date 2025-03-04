import tkinter as tk
import guiflds as gf
import units
from config import Config
from guiflddefs import paths, FldDef
from flds import Fld, Link


def createFldDefs() -> dict[str, FldDef]:
    flds: dict[str, gf.GuiFldDef] = dict()
    jf = Fld("entryInt",
             "Long Int",
             "Sh Int",
             str,
             int,
             "e"
             )
    flds[jf.jsonHead] = FldDef(jf, 10, 5, gf.FldEntry)

    jf = Fld("entryStr",
             "Long Str",
             "Sh Str",
             str,
             gf.strJson,
             "w"
             )
    flds[jf.jsonHead] = FldDef(jf, 8, 5, gf.FldEntry)
    flds["manda"] = FldDef(jf, 8, 5, gf.FldEntry, isMan=False)

    jf = Fld("options",
             "Long options",
             "Opts",
             units.shortTxt,
             units.noShort,
             "w"
             )
    flds[jf.jsonHead] = FldDef(jf, 4, 5, gf.FldOpt,
                               options=units.all(),
                               defaultVal=units.m
                               )
    jf = Fld("label",
             "test4Label",
             "label",
             str,
             str,
             "w")
    flds[jf.jsonHead] = FldDef(jf, 15, 5, gf.FldLabel)

    jf = Fld("jsonTabs",
             "Json Tabs",
             "Tabs",
             str,
             str,
             "e"
             )
    flds[jf.jsonHead] = FldDef(jf, 10, 5, gf.FldOpt,
                               options=None,
                               defaultVal="Default"
                               )

    jf = Fld("jsonPaths",
             "Json Paths",
             "Paths",
             str,
             str,
             "e"
             )
    flds[jf.jsonHead] = FldDef(jf, 10, 5, gf.FldOpt,
                               options=None,
                               linkDef=Link(flds["label"].fld, jf),
                               defaultVal=("DBT")
                               )

    return flds


class TestFlds:

    def __init__(self):
        self.fldDefs = createFldDefs()
        self.flds: dict[str, gf.Fld] = dict()
        self.window = tk.Tk()
        self.window.title("Test table")
        if paths.dec != paths.dec:
            print("Some thing is wrong")
        if paths.dec == paths.dpUnit:
            print("something wrong")

        self.testFldEntry()

        self.testFldOpt()

        self.testFldJsonOpt()
        self.testFldJsonOptPaths()
        self.testFldLabel()
        self.testPathsFlds()
        self.testFldBool()

    def testPathsFlds(self):
        paths.dec
        key = "pathsDec"
        fld = paths.dec.createFld(self.window)
        self.flds[key] = fld
        fld.mainFrame.pack(fill="x")
        fld.show(3)

    def testFldOpt(self):
        key = "options"
        fld = self.fldDefs[key].createFld(self.window)
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
        fld = self.fldDefs[key].createFld(self.window)
        fld.mainFrame.pack(fill="x")
        self.flds[key] = fld

        fld.show(4)
        fld.setError(True)

        key = "entryStr"
        fld = self.fldDefs[key].createFld(self.window)
        fld.mainFrame.pack(fill="x")
        self.flds[fld.id] = fld

        fld.show("")
        fld.validate()

        key = "manda"
        fld = self.fldDefs[key].createFld(self.window)
        fld.mainFrame.pack(fill="x")
        self.flds[key] = fld

        fld.show("")
        fld.validate()
        if fld.get() is not None:
            print("Failed ValueError raise on str")

    def testFldBool(self):
        fld = paths.dis.createFld(self.window)
        fld.mainFrame.pack(fill="x")
        if fld.get():
            print("Error expected false")
        fld.show(True)
        if not fld.get():
            print("Error expected True")

    def testFldLabel(self):
        key = "label"
        fld = self.fldDefs[key].createFld(self.window)
        fld.mainFrame.pack(fill="x")
        self.flds[key] = fld

        fld.show("asdfh34j")
        fld.validate()

        jsonDef = self.fldDefs["label"].fld
        key = "head"
        fld = gf.FldLabelHead(self.window, jsonDef)
        fld.mainFrame.pack(fill="x")
        self.flds[key] = fld

        fld.fldLabelOut.configure(bg="blue")
        fld.mainFrame.pack(fill="x")

    def testFldJsonOpt(self):
        conf = Config(isDefault=True)
        tabsJson = conf.tabsGet()
        pathsJson, alarmsJson, bigsJson = conf.pathsGet()

        key = "jsonTabs"
        df = self.fldDefs[key]
        fld: gf.FldOpt = self.fldDefs[key].createFld(self.window)
        fld.setJsonObj(tabsJson)
        fld.mainFrame.pack(fill="x")
        self.flds[key] = fld

        fld.show("Default")
        fld.validate()
        key = "jsonPaths"
        df = self.fldDefs[key]
        fld: gf.FldOpt = self.fldDefs[key].createFld(self.window)
        fld.setJsonObj(pathsJson)
        fld.mainFrame.pack(fill="x")
        self.flds[key] = fld

        newId = "navigation.courseRhumbline.nextPoint.distance"
        defaultId = "environment.depth.belowTransducer"
        v = fld.get()
        exV = pathsJson[defaultId][df.linkDef.dpFld.jsonHead]
        if exV != v:
            print("Error")
        fld.show(pathsJson[newId][df.linkDef.dpFld.jsonHead])
        fld.validate()
        v = fld.get()
        exV = pathsJson[newId][df.linkDef.dpFld.jsonHead]

        if v != exV:
            print("Error")

    def testFldJsonOptPaths(self):
        conf = Config(isDefault=True)
        #  tabsJson = conf.tabsGet()
        pathsJson, alarmsJson, bigsJson = conf.pathsGet()
        fldMaster: gf.FldOpt = paths.pathJs.createFld(self.window)
        fldMaster.setJsonObj(pathsJson)
        fldMaster.mainFrame.pack(fill="x")
        fldLabel: gf.FldOpt = paths.labelJs.createFld(self.window)
        fldLabel.mainFrame.pack(fill="x")
        fldUnit: gf.FldOpt = paths.dpUnitJs.createFld(self.window)
        fldUnit.mainFrame.pack(fill="x")
        fldMaster.jsonFilter.setSlave(fldLabel)
        fldMaster.jsonFilter.setSlave(fldUnit)

    def start(self):
        self.window.mainloop()


dp = TestFlds()
dp.start()
