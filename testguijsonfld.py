import tkinter as tk
import guijson as gt
import units


class TestFlds:

    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Test table")
        self.fld = gt.Fld(self.window,
                          "test",
                          str,
                          int)
        self.fld.show(4)
        self.fld.mainFrame.pack()
        self.fldOpt = gt.FldOpt(self.window,
                                "Units",
                                units.m,
                                units.shortTxt,
                                units.noShort,
                                units.all())
        self.fldOpt.show(units.ms)
        self.fld.mainFrame.pack()
        print(self.fldOpt.get())
        print(self.fld.get())

    def start(self):
        self.window.mainloop()


dp = TestFlds()
dp.start()
