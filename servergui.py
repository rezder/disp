import tkinter as tk
import time

from gui import BORDER_COLOR, BORDER_WIDTH
import guistatus
import guidisp
import guimenu
import guialarms
import guipaths
import guiserial
from server import DispServer


class GuiDispServer:
    """
    The gui of the display server.
    """
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Display Server")
        self.server = DispServer()

        # Main Frames
        self.leftFrame = tk.Frame(self.window,
                                  highlightthickness=BORDER_WIDTH,
                                  highlightbackground=BORDER_COLOR)
        self.leftFrame.pack(side=tk.LEFT,
                            fill=tk.Y,
                            expand=True,
                            padx=(0, 10))

        self.centreFrame = tk.Frame(self.window,
                                    highlightthickness=BORDER_WIDTH,
                                    highlightbackground=BORDER_COLOR)
        self.centreFrame.pack(side=tk.LEFT,
                              fill=tk.Y,
                              expand=True,
                              padx=(0, 10))

        self.rightFrame = tk.Frame(self.window,)
        self.rightFrame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Right Frame
        self.stButton = guistatus.Button(self.window,
                                         self.server.start,
                                         self.server.stop,
                                         self.server.stopClean)

        self.statusGui = guistatus.Status(self.rightFrame,
                                          self.stButton,
                                          self.server.getStatus)
        self.statusGui.mainFrame.pack()

        # Left Frame
        self.dispListGui = guidisp.List(self.leftFrame,
                                        self.server.changeDisp,
                                        self.server.disableDisp)

        self.dispListGui.show(self.server.conf.defaultTab,  # TODO should not be used here
                              self.server.conf.dispGet(),
                              self.server.conf.tabsGetIds(),
                              self.server.conf.dispGetBles())
        self.dispListGui.mainFrame.pack()

        # Centre Frame
        self.alarmsGui = guialarms.Alarms(self.centreFrame,
                                          self.server.alarmDisable)
        pathsJson, alarmsJson, _ = self.server.conf.pathsGet()
        self.alarmsGui.show(pathsJson, alarmsJson)
        self.alarmsGui.mainFrame.pack()

        # Menu bar
        self.menuBar = tk.Menu(self.window, tearoff=0)

        # Menu Registor
        menuRegistor = tk.Menu(self.menuBar, tearoff=0)
        # Upd
        udpFrame, _ = guimenu.addWinMenuItem(self.window,
                                             menuRegistor,
                                             "Udp Display Registor",
                                             titleMenu="Udp")
        self.udpGui = guiserial.Udp(udpFrame,
                                    self.server.addNewUdpDisp,
                                    self.logger)
        self.udpGui.mainFrame.pack()
        self.udpGui.show(self.server.conf.getSubPort())
        # Ble
        bleFrame, _ = guimenu.addWinMenuItem(self.window,
                                             menuRegistor,
                                             "Ble Display Registor",
                                             "Ble")
        self.bleGui = guiserial.Ble(bleFrame,
                                    self.server.addNewBleDisp,
                                    self.logger)
        self.bleGui.mainFrame.pack()
        self.bleGui.show()

        # Menu settings
        menuSettings = tk.Menu(self.menuBar, tearoff=0)
        # Paths
        pathsFrame, pathsWin = guimenu.addWinMenuItem(self.window,
                                                      menuSettings,
                                                      "Paths")
        self.pathsGui = guipaths.Paths(pathsWin,
                                       pathsFrame,
                                       self.logger,
                                       self.server.pathsDelete,
                                       self.server.pathsSave)
        self.pathsGui.mainFrame.pack()
        self.pathsGui.show(self.server.conf.pathsGet())
        # Add  Menu bar
        self.menuBar.add_cascade(label="Registor Display",
                                 menu=menuRegistor,
                                 background="grey26")
        self.menuBar.add_cascade(label="Settings",
                                 menu=menuSettings)

        self.window.config(menu=self.menuBar)

        # Gui inter connectioncs
        self.stButton.subscribeOnOff(self.bleGui.serverOn)
        self.stButton.subscribeOnOff(self.udpGui.serverOn)
        self.stButton.subscribeOnOff(self.pathsGui.serverOn)
        self.stButton.subscribeOnOff(self.alarmsGui.setOnOff)

        self.statusGui.subscribeOns(self.dispListGui.serverOns)
        self.statusGui.subscribeAlarms(self.alarmsGui.alarmMsg)

        self.udpGui.subScribeNewIds(self.dispListGui.newId)
        self.bleGui.subScribeNewIds(self.dispListGui.newId)

        self.pathsGui.subScribePathUpd(self.alarmsGui.updDatePaths)

        # window callbacks
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def logger(self, txt):
        self.statusGui.write(txt)
        self.window.update_idletasks()

    def on_closing(self):
        self.logger("Clossing server")
        self.window.update_idletasks()
        self.statusGui.updateStatus()
        while not self.server.stop():
            print("Waiting for stop to return")
            time.sleep(1)
        self.window.after(1000, self.on_closingStopCheck)

    def on_closingStopCheck(self):
        self.statusGui.updateStatus()
        if self.server.stopClean():
            self.window.update_idletasks()
            time.sleep(2)
            self.window.destroy()
        else:
            self.window.after(2000, self.on_closingStopCheck)

    def start(self):
        self.window.after(1000, self.statusLoop())

        self.window.mainloop()

    def statusLoop(self):
        self.statusGui.updateStatus()
        self.window.after(3000, self.statusLoop)


dp = GuiDispServer()
dp.start()
