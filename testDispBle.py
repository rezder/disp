import asyncio
import time

from status import Status
from skdata import SkData
import ble
from config import Config


def creatDummyMsg(skData) -> bytes:
    path = "navigation.speedOverGround"
    value = 10.1
    for i in range(3):
        skData.getPath(path).createDispData(value)
    b = skData.getPath(path).createDispData(value)
    return (b, path)


async def main():
    conf = Config()
    status = Status()
    skData = SkData(conf, status)
    id = "b1"
    mac = "f0:f5:bd:76:91:9d"
    display = ble.Display(id, mac, status)
    view = conf.viewsGetView("Default")
    display.setView(view)
    print(display)
    await asyncio.sleep(2)

    display.checkConnTask()
    (ok, txt, _, _, _, _) = status.getStatus()
    print(txt)
    if display.connTask is not None:
        print("Conncting to {} failed".format(mac))
        return
    b, path = creatDummyMsg(skData)
    ts = time.monotonic()
    await display.display(b, path)
    print(time.monotonic()-ts)
    (ok, txt, _, _, _, _) = status.getStatus()
    print(txt)
    await display.turnOff()
    # await asyncio.sleep(5)

if __name__ == "__main__":

    asyncio.run(main())
