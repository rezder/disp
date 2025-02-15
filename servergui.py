import tkinter as tk
import time

from gui import BORDER_COLOR, BORDER_WIDTH
import guistatus
import guidisp
import guimenu
import guidisable
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

        self.dispListGui.show(self.server.conf.defaultTab,
                              self.server.conf.getCurTabs(),
                              self.server.conf.getTabNames(),
                              self.server.conf.getMacs())
        self.dispListGui.mainFrame.pack()

        # Centre Frame
        self.disTabGui = guidisable.Table(self.centreFrame,
                                          self.server.alarmDisable)
        self.disTabGui.show(self.server.conf.getPathJson())
        self.disTabGui.mainFrame.pack()

        # Menu bar
        self.menuBar = tk.Menu(self.window, tearoff=0)
        self.menuRegGui = guimenu.Registor(self.window,
                                           self.menuBar,
                                           self.server.addNewUdpDisp,
                                           self.server.addNewBleDisp,
                                           self.logger)
        self.menuRegGui.show(self.server.conf.getSubPort())

        self.menuBarGui = guimenu.Bar(self.menuBar,
                                      self.menuRegGui.menuRegistor)
        self.menuBarGui.createMenuBar()

        self.window.config(menu=self.menuBarGui.menuBar)

        # Gui inter connectioncs
        self.stButton.subscribeOnOff(self.menuRegGui.udpGui.serverOn)
        self.stButton.subscribeOnOff(self.menuRegGui.bleGui.serverOn)
        self.stButton.subscribeOnOff(self.disTabGui.setOnOff)

        self.statusGui.subscribeOns(self.dispListGui.serverOns)
        self.statusGui.subscribeAlarms(self.disTabGui.alarmMsg)

        self.menuRegGui.udpGui.subScribeNewIds(self.dispListGui.newId)
        self.menuRegGui.bleGui.subScribeNewIds(self.dispListGui.newId)

        # window callbacks
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def logger(self, txt):
        self.statusGui.write(txt)

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
