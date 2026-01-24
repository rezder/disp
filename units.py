"""
Units domain m(0),nm(1),ms(10),knot(11),rad(20),deg(21),txt(99)
"""
m = 0
nm = 1
ms = 10
knot = 11
rad = 20
deg = 21
txt = 99


shorts4 = {0: "m\0\0\0",
           1: "nm\0\0",
           10: "m/s\0",
           11: "knot",
           20: "rad\0",
           21: "deg\0",
           99: "txt\0"
           }

invShorts4 = {"m\0\0\0": 0,
              "nm\0\0": 1,
              "m/s\0": 10,
              "knot": 11,
              "rad\0": 20,
              "deg\0": 21,
              "txt\0": 99
              }
shorts = {0: "m",
          1: "nm",
          10: "m/s",
          11: "knot",
          20: "rad",
          21: "deg",
          99: "txt"
          }

invShorts = {"m": 0,
             "nm": 1,
             "m/s": 10,
             "knot": 11,
             "rad": 20,
             "deg": 21,
             "txt": 99
             }


def all() -> set[int]:
    return set(shorts4.keys())


def shortTxt4(no) -> str:
    return shorts4[no]


def noShort4(txt) -> int:
    return invShorts4[txt]


def shortTxt(no) -> str:
    return shorts[no]


def noShort(txt) -> int:
    return invShorts[txt]


def conversion(inu, outu):
    txt = "Failed conversion from {} to {} not implemented"
    ex = Exception(txt.format(shortTxt(inu), shortTxt(outu)))
    if inu == outu:
        return lambda a: a
    match inu:
        case 0:
            match outu:
                case 1:
                    return lambda a: a*9*6/100000
                case _:
                    raise ex

        case 10:
            match outu:
                case 11:
                    return lambda a: a*3.6*54/100
                case _:
                    raise ex
        case 20:
            match outu:
                case 21:
                    return lambda a: a*180/3.1416
                case _:
                    raise ex
        case _:
            raise ex
