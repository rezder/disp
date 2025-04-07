
import units


class DispData:
    def __init__(self,
                 value: float,
                 decimals: int,
                 label: str,
                 units: int,
                 isAlarm: bool
                 ):
        self.value = value
        self.decimals = decimals
        self.label = label
        self.units = units
        vtxt, sign = formatNo(decimals, value)
        self.valueTxt = vtxt
        self.sign = sign
        self.isAlarm = isAlarm

    def __str__(self) -> str:
        txt = "DispData: value:{},dec:{},label:{},unit:{},"\
            "valueTxt:{},sign:{},isAlarm:{}"
        txt = txt.format(self.value,
                         self.decimals,
                         self.label,
                         units.shortTxt(self.units),
                         self.valueTxt,
                         self.sign,
                         self.isAlarm)
        return txt

    def __repr__(self) -> str:
        return self.__str__()

    def encode(self, pos: int) -> bytearray:
        """
        Create a 14 size bytearray:
        Pos(uint8),Decimals(uint8),sign(uint8/bool),
        isAlarm(uint8/bool),
        units(4char),label(3char),value(3char).
        """
        # treats all values a unsign int under 255
        res = bytearray((pos,
                         self.decimals,
                         self.sign,
                         self.isAlarm))
        # txt have full size padded with \0
        txt = units.shorts4[self.units] + self.label + self.valueTxt
        res.extend(txt.encode("ascii"))
        return res

    def decode(buff: bytearray):
        if len(buff) < 14:
            raise Exception("buffer to small")
        # pos = buff[0]
        dec = buff[1]
        sign = bool(buff[2])
        isAlarm = bool(buff[3])
        unitsTxt = buff[4:8].decode("ascii")
        label = buff[8:11].decode("ascii")
        valueTxt = buff[11:14].decode("ascii")
        valueTxt = valueTxt.rstrip('\0')
        value = float(valueTxt)/(dec*10)
        if sign:
            value = value*-1
        unit = units.noShort4(unitsTxt)
        dp = DispData(value, dec, label, unit, isAlarm)
        return dp


def formatNo(dec: int, x: float) -> (str, bool):
    """
    format value float to a text value.
    All text numbers is 3 char left aligned.
    With \0 as extension.
    Eksample -1.2 to 12\0,True.
    Eksample 2 to 2\0\0,False
    :param dec: Numbers of decimals.
    :param x: the float value.
    :return: A tuple of the text and sign
    """
    if x is not None:
        sign = False
    #  Remove sign
        if x < 0:
            x = x * -1
            sign = True
    #  Round
        # x = round(x, dec)  # Maybe not necessary

    #  Cap
        x = x * pow(10, dec)
        if x > 999:  # Could add a secondary unit
            x = 999
        x = x/pow(10, dec)

    #  Add decimals zeros and round
        tf = "{:." + str(dec) + "f}"
        txt = tf.format(x)

    #  Remove decimal
        txt = txt.replace(".", "")

    #  Allign
        if len(txt) < 3:
            m = 3-len(txt)
            if m == 1:
                txt = txt+"\0"
            if m == 2:
                txt = txt+"\0\0"
    else:
        txt = "NON"

    return (txt, sign)
