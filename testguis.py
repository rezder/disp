import tkinter as tk
import sys

from guisettings import Sett
from guidispconf import Disp
from jsonptr import ErrPtr
from flds import settings as dd
from config import Config


class TestGui:

    def __init__(self):
        self.conff = Config()
        self.window = tk.Tk()
        self.window.title("Test Gui")
        self.mainFrame = tk.Frame(self.window)
        self.mainFrame.pack()
        self.setFram = tk.Frame(self.mainFrame)
        self.setFram.pack()
        self.dispFrame = tk.Frame(self.mainFrame)
        self.dispFrame.pack()
        self.settGui = Sett(self.window, self.setFram, self.saveFn)
        self.settGui.mainFrame.pack()
        self.data1 = {dd.broadCP.fld.jId: 9090,
                      dd.iface.fld.jId: "wpsidsfhg",
                      dd.disSub.fld.jId: True}
        self.data2 = {dd.broadCP.fld.jId: 90,
                      dd.iface.fld.jId: "wps",
                      dd.disSub.fld.jId: False}
        self.settGui.show(self.data1)
        self.dispGui = Disp(self.window, self.dispFrame,
                            self.logger,
                            self.dispSaveFn,
                            9090,
                            self.dispValidateFn)
        self.dispGui.mainFrame.pack()
        disps, macs, views, paths = self.getdispdata()
        self.dispGui.show(disps, macs, views, paths)

    def getdispdata(self) -> tuple[dict, dict, dict, dict]:

        disps, macs, views, paths = self.conff.dispsGet()
        return disps, macs, views, paths

    def logger(self, txt: str):
        print(txt)

    def validateFn(self) -> tuple[str, list[ErrPtr]]:
        txt = ""
        errPtrs = list()
        return txt, errPtrs

    def saveFn(self) -> dict:
        res = self.data2
        return res

    def dispSaveFn(self) -> dict:
        res = dict()
        return res

    def dispValidateFn(self) -> tuple[str, list[ErrPtr]]:
        txt = ""
        errPtrs = list()
        return txt, errPtrs

    def stop(self):
        self.window.destroy()

    def start(self):
        if len(sys.argv) > 1 and sys.argv[1] == "-t":
            self.window.after(1000, self.stop)
        self.window.mainloop()


dp = TestGui()
dp.start()
