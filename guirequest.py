chgTab = 1
alarmDis = 2
disDisp = 3


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
