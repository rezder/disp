import cmd
import state
import threading
import copy


class AlarmMsg:
    def __init__(self, path, isOn, label, value=None):
        self.path = path
        self.isOn = isOn
        self.label = label
        self.value = value


class Status:
    """
    The Status object is mainly used to
    communicate from asyncio thread
    to the normal thread.
    The object has a thread lock.
    Thread lock is expensive
    Don't hold two locks
    or always in same order.
    Be aware the async makes the order
    unpredictable.
    It also used to keep the qui
    from doing something bad.

    Text is cleared after get.
    """
    def __init__(self):
        self.txt = "\nServer version 0.1"
        self.lock = threading.Lock()
        self.state = state.none
        self.cmd = cmd.none
        self.dispOnSet = set()
        self.alarms: list[AlarmMsg] = list()

    def setStartServer(self) -> bool:
        ok = False
        isMine = self.lock.acquire()  # blocks
        if isMine:
            if self.state == state.none:
                self.state = state.running
                ok = True
            self.lock.release()
        return ok

    def setStopServer(self) -> bool:
        ok = False
        isMine = self.lock.acquire()  # blocks
        if isMine:
            if self.cmd != cmd.stop and self.state != state.none:
                self.cmd = cmd.stop
                txt = "Sending shutdown event"
                self.txt = self.txt + "\n" + txt
                ok = True
            self.lock.release()
        return ok

    def setUpdateQueue(self, id, tab) -> bool:
        ok = False
        isMine = self.lock.acquire()  # blocks
        if isMine:
            if self.cmd == cmd.none and self.state == state.running:
                self.cmd = cmd.queue  # TODO Is it necessary limits queue to one
                txt = "User request display: {} change to: {}".format(id, tab)
                self.txt = self.txt + "\n" + txt
                ok = True
            self.lock.release()
        return ok

    def setAlarmDis(self, label: str, isDis: bool):
        ok = False
        isMine = self.lock.acquire()  # blocks
        if isMine:
            if self.cmd == cmd.none and self.state == state.running:
                self.cmd = cmd.queue  # TODO Is it necessary limit queue to one
                atxt = "enable"
                if isDis:
                    atxt = "disable"
                txt = "User request alarm on {} {}".format(label, atxt)
                self.txt = self.txt + "\n" + txt
                ok = True
            self.lock.release()
        return ok

    def setServerDone(self):
        isMine = self.lock.acquire()  # blocks
        if isMine:
            self.cmd = cmd.none
            self.state = state.none
            self.txt = self.txt + "\n" + "Server is stopped"
            self.dispOnSet.clear()
            self.lock.release()

    def setDoneCmd(self):
        isMine = self.lock.acquire()  # blocks
        if isMine:
            if self.cmd != cmd.none:
                txt = "{} is done"
                txt = txt.format(cmd.shortTxt(self.cmd))
                self.txt = self.txt + "\n" + txt
                self.cmd = cmd.none
            self.lock.release()

    def updateRunningStat(self, st: int, txt: str):
        isMine = self.lock.acquire()  # blocks
        if isMine:
            self.state = st
            self.txt = self.txt + "\n" + txt
            self.lock.release()

    def addOn(self, id: str):
        isMine = self.lock.acquire()  # blocks
        if isMine:
            self.dispOnSet.add(id)
            self.lock.release()

    def getStatus(self) -> (bool, str, int, int, set, list):
        """
        :returns:
        - Ok    - If lock was acquired
        - Txt   - New status txt
        - St    - State
        - c     - Command
        - s     - Connected displays ids
        - a     - The alarms message
        """
        isMine = self.lock.acquire(timeout=2.0)
        txt = ""
        c = cmd.none
        st = state.none
        isOk = False
        s = set()
        if isMine:
            if self.txt:
                txt = copy.copy(self.txt)
                self.txt = ""
            c = self.cmd
            st = self.state
            s = set(self.dispOnSet)
            a = list(self.alarms)
            self.alarms.clear()
            self.lock.release()
            isOk = True
        else:
            self.txt = self.txt + "\n" + "failed to get lock"

        return (isOk, txt, st, c, s, a)

    def setTxt(self, txt):
        isMine = self.lock.acquire()
        if isMine:
            self.txt = self.txt + "\n" + txt
            self.lock.release()
        else:
            print("Failed to get status this should not happen")

    def alarmSet(self, msg: AlarmMsg):
        isMine = self.lock.acquire()
        if isMine:
            self.alarms.append(msg)
            self.lock.release()
        else:
            print("Failed to get status this should not happen")

    def alarmGet(self) -> list[AlarmMsg]:
        isMine = self.lock.acquire()
        if isMine:
            res = list(self.alarms)
            self.alarms.clear()
        else:
            print("Failed to get status this should not happen")
        return res
