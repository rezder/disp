import tkinter as tk
import sys

from guipaths import Paths
from config import Config
from flds import flds as ff


class TestPaths:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Test paths")
        conf = Config(True)
        self.tPathsJson = conf.pathsGet()
        self.paths = Paths(self.window,
                           self.window,
                           self.logger,
                           self.save)
        self.paths.mainFrame.pack()
        self.paths.show(*self.tPathsJson)

    def stop(self):
        self.window.destroy()

    def start(self):
        if len(sys.argv) > 1 and sys.argv[1] == "-t":
            self.window.after(1000, self.stop)
        self.window.mainloop()

    def logger(self, txt):
        print(txt)

    def save(self, path, itemJson):
        isOk = False
        errFlds = [ff.minPer.jId, ff.pathId.jId]
        errTxt = "Bad blod"
        pathJson = None
        return isOk, errFlds, errTxt, pathJson

    def delete(self, path):
        isOk = False
        errTxt = "Bad blod"
        pathJson = None
        return isOk, errTxt, pathJson


dp = TestPaths()
dp.start()
