import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import time
import serial
import serial.tools.list_ports as sTools

from server import DispServer
import cmd
import state
from functools import partial
from status import AlarmMsg

DEFAULT_BAUDRATE = 115200
BORDER_WIDTH = 1
BORDER_COLOR = "grey14"


def getSerialPath() -> str:
    ports = sTools.comports()
    path = None
    for p in ports:
        if p.product == "Nano ESP32" or p.manufacturer == "Espressif":
            path = p.device
    return path


class DisTableGui:
    def __init__(self, parent: tk.Frame, pathJson: dict, disActFn):
        self.disActFn = disActFn
        self.pathsGui = dict()
        self.pathsJson = pathJson
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.tabFrame = tk.Frame(self.mainFrame,
                                 highlightthickness=BORDER_WIDTH,
                                 highlightbackground=BORDER_COLOR)
        self.bgColor = self.parent.cget("bg")

    def create(self):
        title = tk.Label(self.mainFrame, text="Alarms")
        title.pack()
        la = tk.Label(self.tabFrame, text="Label")
        la.grid(row=0, column=0)
        la = tk.Label(self.tabFrame, text="Min", width=6)
        la.grid(row=0, column=1)
        la = tk.Label(self.tabFrame, text="Value")
        la.grid(row=0, column=2)
        la = tk.Label(self.tabFrame,
                      text="Max",
                      width=6)
        la.grid(row=0, column=3)
        la = tk.Label(self.tabFrame,
                      text="Disable")

        la.grid(row=0, column=4)
        i = 1
        for (path, data) in self.pathsJson.items():
            if "max" in data or "min" in data:
                label = tk.Label(self.tabFrame, text=data["label"])
                label.grid(row=i, column=0)
                txt = ""
                if "min" in data:
                    txt = data["min"]
                minl = tk.Label(self.tabFrame, text=txt)
                minl.grid(row=i, column=1)
                valueVar = tk.StringVar(value="")
                vl = tk.Label(self.tabFrame, textvariable=valueVar)
                vl.grid(row=i, column=2)
                txt = ""
                if "max" in data:
                    txt = data["max"]
                maxl = tk.Label(self.tabFrame, text=txt)
                maxl.grid(row=i, column=3)
                checkVar = tk.IntVar(value=0)
                fn = partial(self.checkFn, path, data["label"], checkVar)
                checkB = tk.Checkbutton(self.tabFrame,
                                        variable=checkVar,
                                        onvalue=1,
                                        offvalue=0,
                                        command=fn,
                                        selectcolor="grey10",
                                        state=tk.DISABLED)
                checkB.grid(row=i, column=4)
                self.pathsGui[path] = (valueVar, vl, checkB)
            self.tabFrame.pack()

    def checkFn(self, path, label, checkVar: tk.IntVar):
        if checkVar.get() == 1:
            self.disActFn(path, label, True)
        else:
            self.disActFn(path, label, False)

    def alarmMsg(self, msgs: list[AlarmMsg]):
        for msg in msgs:
            (valueVar, valueLabel, checkBox) = self.pathsGui[msg.path]
            if msg.isOn:
                vTxt = "{:.1f}".format(msg.value)
                valueVar.set(vTxt)
                valueLabel.config(bg="red")
            else:
                valueVar.set("")
                valueLabel.config(bg=self.bgColor)

    def setOnOff(self, isOn: bool):
        for (path, data) in self.pathsGui.items():
            (_, _,  checkBox) = data
            if isOn:
                checkBox.config(state=tk.NORMAL)
            else:
                checkBox.config(state=tk.DISABLED)


class StateGui:

    def __init__(self, parent: tk.Frame):
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.stateVar = tk.StringVar(value="")
        self.stateLabel = None
        self.cmdVar = tk.StringVar(value="")
        self.cmdLabel = None
        self.bgColor = self.parent.cget("bg")

    def create(self):
        self.stateLabel = tk.Label(self.mainFrame, textvariable=self.stateVar)
        self.stateLabel.grid(row=0, column=0)
        self.cmdLabel = tk.Label(self.mainFrame, textvariable=self.cmdVar)
        self.cmdLabel.grid(row=0, column=2, sticky=tk.E)
        s = tk.Label(self.mainFrame, text=":")
        s.grid(row=0, column=1, sticky=tk.NE)

    def updStateCmd(self, c, st):
        self.cmdVar.set(cmd.shortTxt(c))
        self.stateVar.set(state.shortTxt(st))
        if st == state.broke:
            self.stateLabel.config(bg="red")
        else:
            self.stateLabel.config(bg=self.bgColor)


class ConfTabGui:

    def __init__(self,
                 parent: tk.Frame,
                 ids: dict,
                 values: list,
                 macs: dict,
                 defaultVal: str,
                 cbTabChg,
                 cbDisable):
        self.parent = parent
        self.mainFrame = tk.Frame(self.parent)
        self.radios = list()
        self.ons = set()
        self.cbTabChg = cbTabChg
        self.cbDisable = cbDisable
        self.values = values
        self.ids = ids
        self.defaultVal = defaultVal
        self.macs = macs

    def create(self):
        title = tk.Label(self.mainFrame, text="Displays")
        title.pack()
        for id, tabId in self.ids.items():
            macAddr = None
            isDisable = False
            if id in self.macs:
                macObj = self.macs[id]
                macAddr = macObj["addr"]
                isDisable = macObj["isDisable"]

            r = RadioTab(self.mainFrame,
                         id,
                         self.values,
                         tabId,
                         macAddr,
                         isDisable,
                         self.cbTabChg,
                         self.cbDisable)
            r.create()
            r.mainFrame.pack(pady=(0, 5), anchor=tk.W)
            self.radios.append(r)

    def newId(self, id: str, macAddr=None):
        isDisable = False
        r = RadioTab(self.mainFrame,
                     id,
                     self.values,
                     self.defaultVal,
                     macAddr,
                     isDisable,
                     self.cbTabChg,
                     self.cbDisable)
        r.create()
        r.mainFrame.pack(pady=(0, 5), anchor=tk.W)
        self.radios.append(r)

    def serverOns(self, ons: set):
        if self.ons != ons:
            for r in self.radios:
                found = False
                for o in ons:
                    if r.id == o:
                        r.setOnOff(True)
                        found = True
                        break
                if not found:
                    r.setOnOff(False)
            self.ons = ons


class RadioTab:

    def __init__(self,
                 parent: tk.Frame,
                 id: str,
                 values: list,
                 currentValue: str,
                 macAddr: str,
                 isDisable,
                 cbTabChg,
                 cbDisable):

        self.parent = parent
        self.id = id
        self.oldValue = currentValue
        self.valueVar = None
        self.radioFrame = None
        self.values = values
        self.cbTabChg = cbTabChg
        self.mainFrame = tk.Frame(
            self.parent,
            highlightthickness=BORDER_WIDTH,
            highlightbackground=BORDER_COLOR)
        self.bgColor = self.mainFrame.cget("bg")
        self.selectColor = "blue"
        self.macAddr = macAddr
        self.isDisableOld = isDisable
        self.idLabel = None
        self.cbDisable = cbDisable

    def create(self):
        f = tk.Frame(self.mainFrame)
        f.columnconfigure(1, weight=1)
        f.columnconfigure(0, weight=0)
        f.pack(fill="x")
        lH = tk.Label(f, text="Id:")
        lH.grid(row=0, column=0)
        lId = tk.Label(f, text=self.id)
        lId.grid(sticky="e", row=0, column=1)

        if self.macAddr is not None:
            macAddrTxt = "Mac Address:   {}".format(self.macAddr)
            macVar = tk.StringVar(value=macAddrTxt)
            macLabel = tk.Label(self.mainFrame, textvariable=macVar)
            macLabel.pack(anchor=tk.CENTER)
            v = 0
            if self.isDisableOld:
                v = 1
            self.disableVar = tk.IntVar(value=v)
            self.disableB = tk.Checkbutton(self.mainFrame,
                                           variable=self.disableVar,
                                           onvalue=1,
                                           offvalue=0,
                                           text="Disable",
                                           command=self.checkBoxDisable,
                                           selectcolor="grey10")
            self.disableB.pack(anchor=tk.W)

        self.valueVar = tk.StringVar(value=self.oldValue)
        self.radioFrame = tk.Frame(self.mainFrame,
                                   highlightthickness=BORDER_WIDTH,
                                   highlightbackground=BORDER_COLOR)
        self.radioFrame.pack(anchor=tk.W)
        for header in self.values:
            r = tk.Radiobutton(
                self.radioFrame,
                text=header,
                selectcolor='grey',
                variable=self.valueVar,
                value=header,
                command=self.radioCb)
            r.pack(anchor=tk.W)

    def radioCb(self):
        newValue = self.valueVar.get()
        if not self.cbTabChg(self.id, newValue):
            self.valueVar.set(self.oldValue)
        else:
            self.oldValue = newValue

    def setOnOff(self, on: bool):
        if on is True:
            self.mainFrame.config(highlightbackground=self.selectColor)
            self.mainFrame.config(highlightthickness=4)

        else:
            self.mainFrame.config(highlightbackground=BORDER_COLOR)
            self.mainFrame.config(highlightthickness=BORDER_WIDTH)

    def checkBoxDisable(self):
        newValue = False
        if self.disableVar.get() == 1:
            newValue = True

        if self.cbDisable(self.id, newValue):
            self.isDisableOld = newValue
        else:  # reset
            v = 1
            if newValue:
                v = 0
            self.disableVar.set(v)


class StartButton:

    def __init__(self, window, startCb, stopCb, stoppedCb):
        self.butVar = tk.StringVar(value="start")
        self.startCb = startCb
        self.stopCb = stopCb
        self.stoppedCb = stoppedCb
        self.subOnOffList = list()
        self.window = window

    def create(self, frame: tk.Frame):
        self.button = tk.Button(frame,
                                textvariable=self.butVar,
                                command=self.butCb)

    def getButton(self) -> tk.Button:
        return self.button

    def butCb(self):
        if self.butVar.get() == "start":
            if self.startCb():
                self.butVar.set("stop")
                self.executeOnOff(True)
        else:
            if self.stopCb():
                self.button.config(state=tk.DISABLED)
                self.window.after(1000, self.butCbStopCheck)

    def butCbStopCheck(self):
        print("call clean check")
        if self.stoppedCb():
            self.butVar.set("start")
            self.button.config(state=tk.NORMAL)
            self.executeOnOff(False)
        else:
            self.window.after(2000, self.butCbStopCheck)

    def subscribeOnOff(self, fn):
        self.subOnOffList.append(fn)

    def executeOnOff(self, isOn: bool):
        for f in self.subOnOffList:
            f(isOn)


class TxtGui:
    def __init__(self, parent: tk.Frame, stButton: StartButton, statusCb):
        self.parent = parent
        self.statusCb = statusCb
        self.stateGui = None
        self.butVar = None
        self.mainFrame = tk.Frame(self.parent)
        self.statusTbox = None
        self.bottomFrame = tk.Frame(self.mainFrame)
        self.startButton = stButton
        self.subOnsList = list()
        self.subAlarmsList = list()

    def create(self):

        self.statusTbox = scrolledtext.ScrolledText(self.mainFrame, undo=True)
        self.statusTbox['font'] = ('consolas', '12')
        self.statusTbox.pack(fill=tk.BOTH, expand=True)
        heading = "Display server"

        self.statusTbox.insert(tk.END, heading)
        self.startButton.create(self.bottomFrame)
        self.startButton.getButton().pack(side=tk.LEFT)

        self.stateGui = StateGui(self.bottomFrame)
        self.stateGui.create()
        self.stateGui.mainFrame.pack(side=tk.RIGHT)

        self.bottomFrame.pack(expand=True, fill=tk.BOTH)

    def write(self, txt):
        self.statusTbox.insert(tk.END, "\n"+txt)

    def subscribeOns(self, fn):
        self.subOnsList.append(fn)

    def subscribeAlarms(self, fn):
        self.subAlarmsList.append(fn)

    def executeOns(self, ons: set):
        for f in self.subOnsList:
            f(ons)

    def executeAlarms(self, alarms: list):
        for f in self.subAlarmsList:
            f(alarms)

    def updateStatus(self):
        ok, txt, st, c, ons, dms = self.statusCb()
        if txt != "":
            self.statusTbox.insert(tk.END, txt)
        if ok:
            self.stateGui.updStateCmd(c, st)
            self.executeOns(ons)
            self.executeAlarms(dms)


class UdpGui:

    def __init__(self, parent: tk.Frame, port, cb, logger):
        self.subNewIdsList = list()
        self.parent = parent
        self.logger = logger
        self.port = port
        self.mainFrame = tk.Frame(self.parent,
                                  highlightthickness=BORDER_WIDTH,
                                  highlightbackground=BORDER_COLOR)
        self.path = getSerialPath()
        self.cb = cb

        self.pwVar = tk.StringVar(value="")
        self.portVar = tk.StringVar(value=str(self.port))
        self.ssidVar = tk.StringVar(value="")
        self.idVar = tk.StringVar(value="")
        self.pathVar = tk.StringVar(value="")

        self.updBut = None

    def create(self):
        gridFrame = tk.Frame(self.mainFrame)
        gridFrame.pack()
        txt = ""
        if self.path is not None:
            txt = self.path
        self.pathVar = tk.StringVar(value=txt)

        pathLab = tk.Label(gridFrame, text="Id:")
        pathLab.grid(row=0, column=0)
        pathEnt = tk.Entry(gridFrame, textvariable=self.idVar)
        pathEnt.grid(row=0, column=1)

        pathLab = tk.Label(gridFrame, text="Serial:")
        pathLab.grid(row=3, column=0)
        pathEnt = tk.Entry(gridFrame,
                           textvariable=self.pathVar,
                           state=tk.DISABLED)
        pathEnt.grid(row=3, column=1)

        ssidLab = tk.Label(gridFrame, text="SSID:")
        ssidLab.grid(row=1, column=0)
        ssidEnt = tk.Entry(gridFrame, textvariable=self.ssidVar)
        ssidEnt.grid(row=1, column=1)

        pwLab = tk.Label(gridFrame, text="Password:")
        pwLab.grid(row=2, column=0)
        pwEnt = tk.Entry(gridFrame, textvariable=self.pwVar)
        pwEnt.grid(row=2, column=1)

        portLab = tk.Label(gridFrame, text="Sub port:")
        portLab.grid(row=4, column=0)
        portEnt = tk.Entry(gridFrame,
                           textvariable=self.portVar,
                           state=tk.DISABLED)
        portEnt.grid(row=4, column=1)

        self.updBut = tk.Button(self.mainFrame,
                                text="Update",
                                command=self.updateCb)
        self.updBut.pack()

    def subScribeNewIds(self, fn):
        self.subNewIdsList.append(fn)

    def executeNewIds(self, newId):
        for f in self.subNewIdsList:
            f(newId)

    def serverOn(self, isOn: bool):
        if isOn:
            self.updBut.config(state=tk.DISABLED)
        else:
            self.updBut.config(state=tk.NORMAL)

    def updateCb(self):
        id = self.idVar.get()
        if self.cb(id):  # Only adds if server not running
            for f in self.subNewIdsList:
                f(id)
        path = self.pathVar.get()
        if path != "":
            port = int(self.portVar.get())
            ssid = self.ssidVar.get()
            pw = self.pwVar.get()
            try:
                con = serial.Serial(path,
                                    baudrate=DEFAULT_BAUDRATE,
                                    timeout=2)
                txt = id+'\n'+ssid+'\n'+pw+'\n'
                data = bytearray(txt.encode(encoding="ascii"))
                dataTmp = port.to_bytes(4, byteorder="little")
                for b in dataTmp:
                    data.append(b)
                con.write(data)
                con.flush()
                con.close()
                self.logger("Wifi data send")

            except serial.SerialException as ex:
                txt = "\nConnection failed with: {}".format(ex)
                self.logger(txt)
        else:
            self.logger("No device connect")


class BleGui:

    def __init__(self, parent: tk.Frame, port, cb, logger):
        self.subNewIdsList = list()
        self.parent = parent
        self.logger = logger
        self.mainFrame = tk.Frame(self.parent,
                                  highlightthickness=BORDER_WIDTH,
                                  highlightbackground=BORDER_COLOR)
        self.path = getSerialPath()
        self.cb = cb

        self.macVar = tk.StringVar(value="")
        self.idVar = tk.StringVar(value="")
        self.pathVar = tk.StringVar(value="")

        self.updBut = None

    def create(self):
        gridFrame = tk.Frame(self.mainFrame)
        gridFrame.pack()
        txt = ""
        if self.path is not None:
            txt = self.path
        self.pathVar = tk.StringVar(value=txt)

        pathLab = tk.Label(gridFrame, text="Id:")
        pathLab.grid(row=0, column=0)
        pathEnt = tk.Entry(gridFrame, textvariable=self.idVar)
        pathEnt.grid(row=0, column=1)

        pathLab = tk.Label(gridFrame, text="Serial:")
        pathLab.grid(row=2, column=0)
        pathEnt = tk.Entry(gridFrame,
                           textvariable=self.pathVar,
                           state=tk.DISABLED)
        pathEnt.grid(row=2, column=1)

        macLab = tk.Label(gridFrame, text="Mac address:")
        macLab.grid(row=1, column=0)
        macEnt = tk.Entry(gridFrame,
                          textvariable=self.macVar,
                          state=tk.DISABLED)
        macEnt.grid(row=1, column=1)

        self.updBut = tk.Button(self.mainFrame,
                                text="Update",
                                command=self.updateCb)
        self.updBut.pack()

    def subScribeNewIds(self, fn):
        self.subNewIdsList.append(fn)

    def executeNewIds(self, newId, macAddr):
        for f in self.subNewIdsList:
            f(newId, macAddr)

    def serverOn(self, isOn: bool):
        if isOn:
            self.updBut.config(state=tk.DISABLED)
        else:
            self.updBut.config(state=tk.NORMAL)

    def updateCb(self):
        path = self.pathVar.get()
        if path != "":
            try:
                con = serial.Serial(path,
                                    baudrate=DEFAULT_BAUDRATE,
                                    timeout=10)
                cmd = 'M'
                data = bytearray(cmd.encode(encoding="ascii"))
                con.write(data)
                con.flush()
                time.sleep(1.0)
                dataSize = 17
                bts = con.read(size=dataSize)
                con.close()
                if len(bts) == dataSize:
                    mac = bts.decode("ascii")
                    self.macVar.set(mac)
                    self.logger("Mac data recieved: {}".format(mac))
                    id = self.idVar.get()
                    if self.cb(id, mac):  # Only adds if server not running
                        self.executeNewIds(id, mac)

            except serial.SerialException as ex:
                txt = "\nConnection failed with: {}".format(ex)
                self.logger(txt)
        else:
            self.logger("No device connect")


def createWindow(parent, title) -> tuple[tk.Toplevel, tk.Frame]:
    w = tk.Toplevel(parent)
    w.title(title)
    w.protocol("WM_DELETE_WINDOW", w.withdraw)
    wf = tk.Frame(w)
    wf.pack()
    return (w, wf)


class MenuRegGui:
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
        self.udpGui = UdpGui(windowFrame,
                             self.port,
                             self.addNewUdpDisp,
                             self.logger)
        self.udpGui.create()
        self.udpGui.mainFrame.pack(pady=(10, 0))

        self.bleWindow, windowFrame = createWindow(self.parent,
                                                   "Ble Display Registor")
        self.bleGui = BleGui(windowFrame,
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


class MenuBarGui:
    def __init__(self, menuBar: tk.Menu, menuReg: tk.Menu):
        self.menuBar = menuBar
        self.menuRegistor = menuReg

    def createMenuBar(self):
        self.menuBar.add_cascade(label="Registor Display",
                                 menu=self.menuRegistor)


class DispGui:
    """
    DispGui the gui of the display server.
    """
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Display")
        self.server = DispServer()
        self.radioFrame = tk.Frame(self.window,
                                   highlightthickness=BORDER_WIDTH,
                                   highlightbackground=BORDER_COLOR)
        self.radioFrame.pack(side=tk.LEFT,
                             fill=tk.Y,
                             expand=True,
                             padx=(0, 10))
        self.updFrame = tk.Frame(self.window,
                                 highlightthickness=BORDER_WIDTH,
                                 highlightbackground=BORDER_COLOR)
        self.updFrame.pack(side=tk.LEFT,
                           fill=tk.Y,
                           expand=True,
                           padx=(0, 10))

        self.txtFrame = tk.Frame(self.window,)
        self.txtFrame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.stButton = StartButton(self.window,
                                    self.server.start,
                                    self.server.stop,
                                    self.server.stopClean)

        self.txtGui = TxtGui(self.txtFrame,
                             self.stButton,
                             self.server.getStatus)
        self.txtGui.create()
        self.txtGui.mainFrame.pack()

        self.confTabGui = ConfTabGui(self.radioFrame,
                                     self.server.conf.getCurTabs(),
                                     self.server.conf.getTabNames(),
                                     self.server.conf.getMacs(),
                                     self.server.conf.defaultTab,
                                     self.server.changeDisp,
                                     self.server.disableDisp)

        self.confTabGui.create()
        self.confTabGui.mainFrame.pack()

        self.disTabGui = DisTableGui(self.updFrame,
                                     self.server.getPathsConfig(),
                                     self.server.alarmDisable)
        self.disTabGui.create()
        self.disTabGui.mainFrame.pack()

        self.menuBar = tk.Menu(self.window, tearoff=0)
        self.menuRegGui = MenuRegGui(self.window,
                                     self.menuBar,
                                     self.server.conf.getSubPort(),
                                     self.server.addNewUdpDisp,
                                     self.server.addNewBleDisp,
                                     self.logger)
        self.menuRegGui.create()

        self.menuBarGui = MenuBarGui(self.menuBar,
                                     self.menuRegGui.menuRegistor)
        self.menuBarGui.createMenuBar()

        self.window.config(menu=self.menuBarGui.menuBar)

        self.stButton.subscribeOnOff(self.menuRegGui.udpGui.serverOn)
        self.stButton.subscribeOnOff(self.menuRegGui.bleGui.serverOn)
        self.stButton.subscribeOnOff(self.disTabGui.setOnOff)

        self.txtGui.subscribeOns(self.confTabGui.serverOns)
        self.txtGui.subscribeAlarms(self.disTabGui.alarmMsg)

        self.menuRegGui.udpGui.subScribeNewIds(self.confTabGui.newId)
        self.menuRegGui.bleGui.subScribeNewIds(self.confTabGui.newId)

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def logger(self, txt):
        self.txtGui.write(txt)

    def on_closing(self):
        self.logger("Clossing server")
        self.window.update_idletasks()
        self.txtGui.updateStatus()
        while not self.server.stop():
            print("Waiting for stop to return")
            time.sleep(1)
        self.window.after(1000, self.on_closingStopCheck)

    def on_closingStopCheck(self):
        self.txtGui.updateStatus()
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
        self.txtGui.updateStatus()
        self.window.after(3000, self.statusLoop)


dp = DispGui()
dp.start()
