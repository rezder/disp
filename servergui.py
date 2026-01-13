import tkinter as tk
import time

from gui import BORDER_COLOR, BORDER_WIDTH
import guistatus
import guidisp
import guimenu
import guialarms
import guipaths
import guidispconf
from guisettings import Sett
from server import DispServer
from flds import fldsDict as fd


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

        self.statusGui = guistatus.Status(self.window,
                                          self.rightFrame,
                                          self.stButton,
                                          self.server.getStatus)
        self.statusGui.mainFrame.pack()

        # Left Frame
        self.dispListGui = guidisp.List(self.leftFrame,
                                        self.server.chgDispView)

        self.dispListGui.show()
        self.dispListGui.mainFrame.pack()

        # Centre Frame
        self.alarmsGui = guialarms.Alarms(self.window,
                                          self.centreFrame,
                                          self.server.alarmDisable)

        self.alarmsGui.mainFrame.pack()

        # Menu bar
        self.menuBar = tk.Menu(self.window, tearoff=0)

        # Menu settings
        menuSettings = tk.Menu(self.menuBar, tearoff=0)
        # Paths
        pathsFrame, pathsWin = guimenu.addWinMenuItem(self.window,
                                                      menuSettings,
                                                      fd.paths.header
                                                      )
        self.pathsGui = guipaths.Paths(pathsWin,
                                       pathsFrame,
                                       self.logger,
                                       self.server.pathsSave)
        self.pathsGui.mainFrame.pack()
        self.pathsGui.show(*self.server.conf.pathsGet())
        # Displays conf
        dispsFrame, dispsWin = guimenu.addWinMenuItem(self.window,
                                                      menuSettings,
                                                      fd.displays.header)
        self.dispsGui = guidispconf.Disp(dispsWin,
                                         dispsFrame,
                                         self.logger,
                                         self.server.displaysSave,
                                         self.server.conf.getSubPort(),
                                         self.server.newDispIdValidation)
        self.dispsGui.mainFrame.pack()
        self.dispsGui.show(*self.server.conf.dispsGet())
        # Sett conf
        settFrame, settWin = guimenu.addWinMenuItem(self.window,
                                                    menuSettings,
                                                    "Misc")
        self.settGui = Sett(settWin,
                            settFrame,
                            self.server.settingsSave)
        self.settGui.mainFrame.pack()
        self.settGui.show(self.server.conf.settingsGet())

        # Add  Menu bar

        self.menuBar.add_cascade(label="Settings",
                                 menu=menuSettings)

        self.window.config(menu=self.menuBar)

        # Gui inter connectioncs
        self.stButton.subscribeOnOff(self.alarmsGui.serverOnOff)
        self.stButton.subscribeOnOff(self.dispListGui.serverOnOff)

        self.statusGui.subscribeOns(self.dispListGui.displayOns)
        self.statusGui.subscribeAlarms(self.alarmsGui.alarmMsg)

        self.pathsGui.subScribePathUpd(self.dispsGui.pathsChg)
        self.settGui.subScribeUpd(self.dispsGui.settingsUpd)

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
