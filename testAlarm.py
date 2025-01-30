import asyncio
from status import Status
from skdata import Alarm


async def main():
    status = Status()
    path = "environment.depth.belowTransducer"
    label = "DBT"
    max = None
    min = 1.7
    minTime = 4
    alarm = Alarm(path, label, max, min, minTime, status)
    raiseAlarm = alarm.eval(1.8)
    if raiseAlarm:
        print("Did not expect an alarm")
    else:
        print("Ok")
    raiseAlarm = alarm.eval(1.6)  # Alarm is triggered
    await asyncio.sleep(1)
    if not raiseAlarm:
        print("Expected an alarm")
    else:
        print("Ok")
    await asyncio.sleep(1)  # start loop 4 second task
    raiseAlarm = alarm.eval(1.8)
    if not raiseAlarm:
        print("Expected an alarm as alarm is triggered")
    else:
        print("Ok")
    await asyncio.sleep(4)
    raiseAlarm = alarm.eval(1.8)
    if raiseAlarm:
        print("Did not expect an alarm as time have pased")
    else:
        print("Ok")


if __name__ == "__main__":

    asyncio.run(main())
