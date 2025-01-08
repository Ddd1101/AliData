import math

import global_params


def SplitChineseAndPinyin(shopNameRaw):
    """
        拆分中文和英文
    """
    ret = -1
    for i in range(len(str)):
        if (str[i] >= "a" and str[i] <= "z") or (
                str[i] >= "A" and str[i] <= "Z"
        ):
            break
        ret = i
    return ret


def NumFormate4Print(numStr):
    """
        规格化尺码
    """
    res = ""
    if numStr[0] in global_params.en_code:
        for item in numStr:
            if item in global_params.en_code:
                res += item
            else:
                break
        fomateSpaceNum = 5 - len(res)
        for k in range(fomateSpaceNum):
            res = " " + res
    else:
        for item in numStr:
            if item >= "0" and item <= "9":
                res += item
            else:
                if len(res) and res[0] == "9":
                    res += " "
                break
        res += "cm"
    return res


def CalPriceLocationENCode(_size):
    """
        对英文码进行规格化处理
    """
    if _size == "":
        return -1

    if _size[0] == "S" or _size[0] == "s":
        return 24

    if _size[0] == "M" or _size[0] == "m":
        return 25

    if _size[0] == "L" or _size[0] == "l":
        return 26

    if _size[0] == "x" or _size[0] == "X":
        if _size[1] == "L" or _size[1] == "l":
            return 27
        elif _size[1] == "x" or _size[1] == "X":
            if _size[2] == "L" or _size[2] == "l":
                return 28
            elif _size[2] == "x" or _size[2] == "X":
                return 29

    return -1



def CalPageNum(totalRecord):
    return math.ceil(totalRecord / 20)


