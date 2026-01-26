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
    await asyncio.sleep(2)
    path = "navigation.speedThroughWater"
    pos = view[path]
    buff = DispData.encodeClear(pos)
    print(buff)
    display.checkConnTask()
    (ok, txt, _, _, _, _) = status.getStatus()
    print(txt)
    if display.connTask is not None:
        print("Conncting to {} failed".format(mac))
        return
    ts = time.monotonic()
    await display.display(path, dds)
    print(time.monotonic()-ts)
    (ok, txt, _, _, _, _) = status.getStatus()
    print(txt)
    time.sleep(5)
    await display.turnOff()
    # await asyncio.sleep(5)

if __name__ == "__main__":

    asyncio.run(main())
