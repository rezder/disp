import tkinter as tk
import guiserial
import guipaths


class Settings:
    def __init__(self,
                 parentWin: tk.Toplevel,
                 parentMenu: tk.Menu,
                 savePath,
                 tPathsJson,
                 deletePath,
                 logger):
        self.parentWin = parentWin
        self.parentMenu = parentMenu
        self.logger = logger
        self.pathsWindow, windowFrame = createWindow(self.parentWin,
                                                     "Paths")
        self.pathsGui = guipaths.Paths(windowFrame,
                                       self.logger,
                                       deletePath,
                                       savePath)
        self.pathsGui.mainFrame.pack()
        self.pathsGui.show(tPathsJson[0])
        self.menuSettings = tk.Menu(self.parentMenu, tearoff=0)
        self.menuSettings.add_command(label="Paths", command=self.pathCreaWin)
        self.pathsWindow.withdraw()

    def pathCreaWin(self):
        self.pathsWindow.deiconify()

    def getMenu(self) -> tk.Menu:
        return self.menuSettings

    def serverOn(self, isOn: bool):
        self.pathsGui.serverOn(isOn)


class Registor:
    def __init__(self,
                 parentWin: tk.Toplevel,
                 parentMenu: tk.Menu,
                 addNewUdpDisp,
                 addNewBleDisp,
                 logger,
                 port: int):
        self.parent = parentWin
        self.parentMenu = parentMenu
        self.addNewUdpDisp = addNewUdpDisp
        self.addNewBleDisp = addNewBleDisp
        self.logger = logger
        self.udpWindow, windowFrame = createWindow(self.parentWin,
                                                   "Udp Display Registor")
        self.udpGui = guiserial.Udp(windowFrame,
                                    self.addNewUdpDisp,
                                    self.logger)
        self.udpGui.mainFrame.pack(pady=(10, 0))  # TODO remove pady it leftover

        self.bleWindow, windowFrame = createWindow(self.parent,
                                                   "Ble Display Registor")
        self.bleGui = guiserial.Ble(windowFrame,
                                    self.addNewUdpDisp,
                                    self.logger)
        self.bleGui.mainFrame.pack(pady=(10, 0))

        self.menuRegistor = tk.Menu(self.parentMenu, tearoff=0)
        self.menuRegistor.add_command(label="Ble", command=self.bleRegistor)
        self.menuRegistor.add_command(label="Udp", command=self.udpRegistor)
        self.udpGui.show(port)
        self.bleGui.show()
        self.udpWindow.withdraw()
        self.bleWindow.withdraw()

    def getMenu(self) -> tk.Menu:
        return self.menuRegistor

    def bleRegistor(self):
        self.bleWindow.deiconify()

    def udpRegistor(self):
        self.udpWindow.deiconify()

    def serverOn(self, isOn: bool):
        self.bleGui.serverOn(isOn)
        self.udpGui.serverOn(isOn)


class Bar:
    def __init__(self,
                 menuBar: tk.Menu,
                 menuReg: tk.Menu,
                 menuSett: tk.Menu):
        self.menuBar = menuBar
        self.menuRegistor = menuReg
        self.menuSett = menuSett

    def createMenuBar(self):
        self.menuBar.add_cascade(label="Registor Display",
                                 menu=self.menuRegistor,
                                 background="grey26")
        self.menuBar.add_cascade(label="Settings",
                                 menu=self.menuSett)


def createWindow(parent: tk.Toplevel, title: str) -> tuple[tk.Toplevel, tk.Frame]:
    w = tk.Toplevel(parent)
    w.title(title)
    w.protocol("WM_DELETE_WINDOW", w.withdraw)
    wf = tk.Frame(w)
    wf.pack()
    return (w, wf)
