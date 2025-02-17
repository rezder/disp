import tkinter as tk
import guijson as gt
import units


class TestFlds:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Test table")
        self.fld = gt.Fld(self.window,
                          "test",
                          10,
                          True,
                          str,
                          int)
        self.fld.show(4)
        self.fld.setError(True)
        self.fld.mainFrame.pack(fill="x")
        self.fld2 = gt.Fld(self.window,
                           "test2",
                           10,
                           True,
                           str,
                           gt.strJson)
        self.fld2.show("")
        self.fld2.validate()
        self.fld2.mainFrame.pack(fill="x")
        self.fld3 = gt.Fld(self.window,
                           "test2",
                           10,
                           False,
                           str,
                           gt.strJson)
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

        self.fldOpt = gt.FldOpt(self.window,
                                "Units",
                                4,
                                units.m,
                                units.shortTxt,
                                units.noShort,
                                units.all())
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

    def start(self):
        self.window.mainloop()


dp = TestFlds()
dp.start()
