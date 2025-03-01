import tkinter as tk
from guipaths import Paths
from config import Config


class TestPaths:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Test paths")
        conf = Config(True)
        self.pathsJson, self.alarmsJson, self.bigsJson = conf.pathsGet()
        self.paths = Paths(self.window,
                           self.logger,
                           self.delete,
                           self.save)
        self.paths.mainFrame.pack()
        self.paths.show(self.pathsJson)

    def start(self):
        self.window.mainloop()

    def logger(self, txt):
        print(txt)

    def save(self, path, itemJson):
        isOk = False
        errFlds = ["minPeriod", "path"]
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
