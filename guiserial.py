import serial
import serial.tools.list_ports as sTools
import time
import tkinter as tk

from gui import BORDER_COLOR, BORDER_WIDTH
from flds import flds as ff


DEFAULT_BAUDRATE = 115200


class Udp:

    def __init__(self, parent: tk.Frame, receiverfn, logger, validateFn):
        self.parent = parent
        self.logger = logger
        self.mainFrame = tk.Frame(self.parent,
                                  highlightthickness=BORDER_WIDTH,
                                  highlightbackground=BORDER_COLOR)

        self.receiverFn = receiverfn
        self.validateFn = validateFn

        self.pwVar = tk.StringVar()
        self.portVar = tk.StringVar()
        self.ssidVar = tk.StringVar()
        self.idVar = tk.StringVar()
        self.pathVar = tk.StringVar()

        gridFrame = tk.Frame(self.mainFrame)
        gridFrame.pack()

        pathLab = tk.Label(gridFrame, text="Id: ", anchor=tk.W)
        pathLab.grid(row=0, column=0, sticky="w")
        pathEnt = tk.Entry(gridFrame, textvariable=self.idVar)
        pathEnt.grid(row=0, column=1)

        pathLab = tk.Label(gridFrame, text="Serial: ", anchor=tk.W)
        pathLab.grid(row=3, column=0, sticky="w")
        pathEnt = tk.Entry(gridFrame,
                           textvariable=self.pathVar,
                           state=tk.DISABLED)
        pathEnt.grid(row=3, column=1)

        ssidLab = tk.Label(gridFrame, text="SSID: ", anchor=tk.W)
        ssidLab.grid(row=1, column=0, sticky="w")
        ssidEnt = tk.Entry(gridFrame,
                           textvariable=self.ssidVar)
        ssidEnt.grid(row=1, column=1)

        pwLab = tk.Label(gridFrame, text="Password:", anchor=tk.W)
        pwLab.grid(row=2, column=0, sticky="w")
        pwEnt = tk.Entry(gridFrame,
                         textvariable=self.pwVar)
        pwEnt.grid(row=2, column=1)

        portLab = tk.Label(gridFrame, text="Sub port: ", anchor=tk.W)
        portLab.grid(row=4, column=0, sticky="w")
        portEnt = tk.Entry(gridFrame,
                           textvariable=self.portVar,
                           state=tk.DISABLED,
                           justify="right")
        portEnt.grid(row=4, column=1)

        self.updBut = tk.Button(self.mainFrame,
                                text="Update",
                                command=self.updateCb)
        self.updBut.pack()

    def show(self, port):
        self.portVar.set(port)
        path = getSerialPath()
        self.pathVar.set(path)

    def settingsUpd(self, settJso: dict):
        self.portVar.set(settJso[ff.broadCP.jId])

    def updateCb(self):
        dispId = self.idVar.get()
        path = self.pathVar.get()
        isOk, errTxt = self.validateFn(dispId)
        if path == "":
            errTxt = "\nSerial port is missing"
        if errTxt == "":
            port = int(self.portVar.get())
            ssid = self.ssidVar.get()
            pw = self.pwVar.get()
            try:
                con = serial.Serial(path,
                                    baudrate=DEFAULT_BAUDRATE,
                                    timeout=2)
                txt = dispId+'\n'+ssid+'\n'+pw+'\n'
                data = bytearray(txt.encode(encoding="ascii"))
                dataTmp = port.to_bytes(4, byteorder="little")
                for b in dataTmp:
                    data.append(b)
                con.write(data)
                con.flush()
                con.close()
                self.logger("Wifi data send")
                self.receiverFn(dispId)

            except serial.SerialException as ex:
                txt = "\nConnection failed with: {}".format(ex)
                self.logger(txt)
        else:
            self.logger(errTxt)


class Ble:
    def __init__(self, parent: tk.Frame, receiverFn, logger, validateFn):
        self.parent = parent
        self.logger = logger
        self.mainFrame = tk.Frame(self.parent,
                                  highlightthickness=BORDER_WIDTH,
                                  highlightbackground=BORDER_COLOR)
        self.path = getSerialPath()
        self.receiver = receiverFn
        self.validateFn = validateFn

        self.macVar = tk.StringVar()
        self.idVar = tk.StringVar()
        self.pathVar = tk.StringVar()

        gridFrame = tk.Frame(self.mainFrame)
        gridFrame.pack()
        pathLab = tk.Label(gridFrame, text="Id: ", anchor=tk.W)
        pathLab.grid(row=0, column=0, sticky="w")
        pathEnt = tk.Entry(gridFrame,
                           textvariable=self.idVar)
        pathEnt.grid(row=0, column=1)

        pathLab = tk.Label(gridFrame, text="Serial: ", anchor=tk.W)
        pathLab.grid(row=2, column=0, sticky="w")
        pathEnt = tk.Entry(gridFrame,
                           textvariable=self.pathVar,
                           state=tk.DISABLED)
        pathEnt.grid(row=2, column=1)

        macLab = tk.Label(gridFrame, text="Mac address: ", anchor=tk.W)
        macLab.grid(row=1, column=0, sticky="w")
        macEnt = tk.Entry(gridFrame,
                          textvariable=self.macVar,
                          state=tk.DISABLED
                          )
        macEnt.grid(row=1, column=1, sticky="w")

        self.updBut = tk.Button(self.mainFrame,
                                text="Update",
                                command=self.updateCb)
        self.updBut.pack()

    def show(self):
        path = getSerialPath()
        self.pathVar.set(path)  # Hope None works

    def updateCb(self):
        dispId = self.idVar.get()
        path = self.pathVar.get()
        isOk, errTxt = self.validateFn(dispId, True)
        if path == "":
            errTxt = "\nSerial port is missing"
        if errTxt == "":
            try:
                self.logger("Create Serial connection")
                con = serial.Serial(path,
                                    baudrate=DEFAULT_BAUDRATE,
                                    timeout=10)
                cmd = 'M'
                data = bytearray(cmd.encode(encoding="ascii"))
                self.logger("Send serial data: {}".format(cmd))
                con.write(data)
                con.flush()
                time.sleep(1.0)
                dataSize = 17
                bts = con.read(size=dataSize)
                self.logger("Close serial connection")
                con.close()
                if len(bts) == dataSize:
                    mac = bts.decode("ascii")
                    self.macVar.set(mac)
                    self.logger("Mac data recieved: {}".format(mac))
                    self.receiver(dispId, mac)
                else:  # timeout
                    data = bts.decode("ascii")
                    self.logger("Time out data recieved: {}".format(data))

            except serial.SerialException as ex:
                txt = "\nConnection failed with: {}".format(ex)
                self.logger(txt)
        else:
            self.logger("No device connect")


def getSerialPath() -> str:
    ports = sTools.comports()
    path = None
    for p in ports:
        if p.product == "Nano ESP32" or p.manufacturer == "Espressif":
            path = p.device
    return path
