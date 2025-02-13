import tkinter as tk
import guiserial


class Registor:
    def __init__(self,
                 parent,
                 parentMenu,
                 port,
                 addNewUdpDisp,
                 addNewBleDisp,
                 logger):
        self.parent = parent
        self.parentMenu = parentMenu
        self.port = port
        self.addNewUdpDisp = addNewUdpDisp
        self.addNewBleDisp = addNewBleDisp
        self.logger = logger

    def create(self):
        self.udpWindow, windowFrame = createWindow(self.parent,
                                                   "Udp Display Registor")
        self.udpGui = guiserial.Udp(windowFrame,
                                    self.port,
                                    self.addNewUdpDisp,
                                    self.logger)
        self.udpGui.create()
        self.udpGui.mainFrame.pack(pady=(10, 0))

        self.bleWindow, windowFrame = createWindow(self.parent,
                                                   "Ble Display Registor")
        self.bleGui = guiserial.Ble(windowFrame,
                                    self.port,
                                    self.addNewUdpDisp,
                                    self.logger)
        self.bleGui.create()
        self.bleGui.mainFrame.pack(pady=(10, 0))

        self.menuRegistor = tk.Menu(self.parentMenu, tearoff=0)
        self.menuRegistor.add_command(label="Ble", command=self.bleRegistor)
        self.menuRegistor.add_command(label="Udp", command=self.udpRegistor)
        self.udpWindow.withdraw()
        self.bleWindow.withdraw()

    def bleRegistor(self):
        self.bleWindow.deiconify()
        print("Ble window")

    def udpRegistor(self):
        self.udpWindow.deiconify()
        print("Udp window")


class Bar:
    def __init__(self, menuBar: tk.Menu, menuReg: tk.Menu):
        self.menuBar = menuBar
        self.menuRegistor = menuReg

    def createMenuBar(self):
        self.menuBar.add_cascade(label="Registor Display",
                                 menu=self.menuRegistor)


def createWindow(parent, title) -> tuple[tk.Toplevel, tk.Frame]:
    w = tk.Toplevel(parent)
    w.title(title)
    w.protocol("WM_DELETE_WINDOW", w.withdraw)
    wf = tk.Frame(w)
    wf.pack()
    return (w, wf)
