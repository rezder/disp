import asyncio
import time

from status import Status
from skdata import SkData
import ble
from config import Config
from dispdata import DispData


def creatDummyMsg(skData, path, value, bufSize) -> bytes:
    if bufSize > 0:
        for i in range(bufSize-1):
            skData.getPath(path).createDispData(value)
    b = skData.getPath(path).createDispData(value)
    return b


async def main():
    conf = Config()
    status = Status()
    skData = SkData(conf, status)
    dds = dict()
    path = "navigation.speedOverGround"
    dd = creatDummyMsg(skData, path, 10.1, 4)
    dds[path] = dd
    path = "environment.depth.belowTransducer"
    dd = creatDummyMsg(skData, path, 39, 0)
    dd = creatDummyMsg(skData, path, None, 0)
    dds[path] = dd

    print(dds)
    id = "b1"
    mac = "24:ec:4a:2c:50:09"
    display = ble.Display(id, mac, status)
    view = conf.viewsGetView("Default")
    await display.setView(view)
    print(display)
    await asyncio.sleep(3)
    display.checkConnTask()
    (ok, txt, _, _, _, _) = status.getStatus()
    print(txt)
    if display.connTask is not None:
        print("Conncting to {} failed".format(mac))
        return
    ts = time.monotonic()
    curPaths = set()
    curPaths.add(path)
    await display.display(curPaths, dds)
    print(time.monotonic()-ts)
    (ok, txt, _, _, _, _) = status.getStatus()
    print(txt)
    sleepSec = 0.5
    await asyncio.sleep(sleepSec)
    b1 = b'\x03\x01\x00\x00knotSTW13\x00'
    await display.disp_sendMsg(b1)
    await asyncio.sleep(sleepSec)
    b2 = b'\x00\x01\x00\x01m\x00\x00\x00DBT43\x00'
    await display.disp_sendMsg(b2)
    await asyncio.sleep(sleepSec)
    b3 = b'\x01\x00\x00\x00deg\x00COG44\x00'
    await display.disp_sendMsg(b3)
    await asyncio.sleep(sleepSec)
    b4 = b'\x02\x01\x00\x00knotSOG18\x00'
    await display.disp_sendMsg(b4)

    await asyncio.sleep(5.2)
    await display.disp_sendClearAll()
    await asyncio.sleep(0.200)
    b = b'\x03\x01\x00\x00knotSTW13\x00\x00\x01\x00\x01m\x00\x00\x00DBT43\x00\x01\x00\x00\x00deg\x00COG43\x00\x02\x01\x00\x00knotSOG18\x00'
    await display.disp_sendMsg(b)
    await asyncio.sleep(10)
    await display.turnOff()
    # await asyncio.sleep(5)

if __name__ == "__main__":

    asyncio.run(main())
