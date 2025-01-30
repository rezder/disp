"""
A domain value for server state.
None is used when there is no asyncio server thread
"""
none = 0
running = 1
conn = 2
broke = 3

shorts = {0: "none",
          1: "running",
          2: "connecting",
          3: "broken"
          }


def all() -> set[int]:
    return set(shorts.keys())


def shortTxt(no) -> str:
    return shorts[no]
