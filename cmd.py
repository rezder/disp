"""
Command from the qui that is send to the asyncio server
"""
none = 0
stop = 1
queue = 2

shorts = {0: "none",
          1: "stop",
          2: "queue"
          }


def all() -> set[int]:
    return set(shorts.keys())


def shortTxt(no) -> str:
    return shorts[no]
