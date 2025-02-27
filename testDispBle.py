from status import Status
from skdata import SkData
import ble
import asyncio
from config import Config
from handler import createDispMsq
import time


def creatDummyMsg(skData) -> bytes:
    path = "navigation.speedOverGround"
    value = 10.1
    for i in range(3):
        createDispMsq(skData, path, value)
    b = createDispMsq(skData, path, value)
    return (b, path)


async def main():
    conf = Config()
    status = Status()
    skData = SkData(conf, status)
    id = "b1"
    mac = "f0:f5:bd:76:91:9d"
    display = ble.Display(id, mac, status)
    tab = conf.tabsGetTab("Default")
    display.setTab(tab)
    print(display)
    await asyncio.sleep(2)

    display.checkConnTask()
    (ok, txt, _, _, _, _) = status.getStatus()
    print(txt)
    if not display.on:
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
