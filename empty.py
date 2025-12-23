"""
Empty domain ok(0), noZero(1), noEmpty(2), noNaN(3),
noFld(4), noNanZero(5)
"""
ok = 0
noZero = 1
noEmpty = 2
noNaN = 3
noNaNZero = 4

txts = {0: "ok",  # Ok all legal values is allowed
        1: "noZero",  # Used for numbers to disallowe zero
        2: "noEmpty",  # used for str to disallowe empty strings
        3: "noNaN",  # used for float to disallowe Not a Number
        4: "noNaNZero"  # used for float to dis NaN and zero
        }

invTxts = {"ok": 0,
           "noZero": 1,
           "noEmpty": 2,
           "noNaN": 3,
           "noNanZero": 4
           }


def all() -> set[int]:
    return set(txts.keys())


def numToTxt(no) -> str:
    return txts[no]


def txtToNum(txt) -> int:
    return invTxts[txt]
