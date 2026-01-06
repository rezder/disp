"""
Queue request domain chgView(1): change the view on display
 alarmDis(2): disable or enable the alarm
"""
chgView = 1
alarmDis = 2


class GuiReq:
    def __init__(self, tp: int, id: str):
        self.tp = tp
        self.id = id
        self.data = None

    def __str__(self) -> str:
        res = "tp:{},id:{},data:{}".format(self.tp, self.id, self.data)
        return res

    def setData(self, data):
        self.data = data
