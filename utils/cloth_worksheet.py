import global_params
import xlrd


class ClothWorksheet:
    def __init__(self, filepath, shop_type):
        """初始化 Person 对象"""
        self.filepath = filepath
        workbook = xlrd.open_workbook(filepath)
        sheetsName = workbook.sheet_names()
        self.worksheet = workbook.sheet_by_name(
            sheetsName[0]
        )  # 获取工作簿中所有表格中的的第一个表格
        self.shop_type = shop_type

    def get_sheet(self):
        return self.worksheet

    def get_price_sheet(self):
        workbook = xlrd.open_workbook(self.filepath)
        sheetsName = workbook.sheet_names()
        self.worksheet = workbook.sheet_by_name(
            sheetsName[0]
        )  # 获取工作簿中所有表格中的的第一个表格

    def GetCost(self, cargoNumber, skuInfosValue, colNum=0):
        if self.worksheet == None:
            worksheet = self.get_price_sheet()
        if self.shop_type == global_params.SHOPTYPE_ALI_CHILD_CLOTH:
            rowIndex = -1
            for t in range(1, worksheet.nrows):
                value = worksheet.cell(t, colNum).value
                if isinstance(value, int) or isinstance(value, float):
                    value = int(value)
                # print(str(cargoNumber), str(value))
                if str(cargoNumber) == str(value):
                    rowIndex = t
                    break
            if rowIndex == -1:
                print(cargoNumber + " ： 未找到对应货号1")
                return 0
            colIndex = self.CalPriceColByName(skuInfosValue)
            if colIndex != -1:
                _price = worksheet.cell(rowIndex, int(colIndex)).value
            else:
                _price = ""
            if _price == "":
                print(
                    "货号："
                    + cargoNumber
                    + " 规格： "
                    + skuInfosValue
                    + " ： 未找到对应价格"
                )
                _price = 0
            return float(_price)

        # todo: 饰品结算
        # elif global_SHOPTYPE == SHOPTYPE_ALI_ACCESSOR:
        #     rowIndex = -1
        #     for t in range(1, worksheet.nrows):
        #         if str(cargoNumber) == str(worksheet.cell(t, colNum).value):
        #             rowIndex = t
        #             break
        #     if rowIndex == -1:
        #         print(str(cargoNumber) + " ： 未找到对应货号2")
        #         return 0
        #     colIndex = 2
        #     if colIndex != None:
        #         _price = worksheet.cell(rowIndex, int(colIndex)).value
        #     else:
        #         _price = ""
        #     return float(_price)

    def CalPriceColByName(self, _size, worksheet):
        """
            根据尺码名字自动查找列位置
        """
        _size = _size.upper()
        if _size == "2XL":
            _size = "XXL"
        elif _size == "3XL":
            _size = "XXXL"
        if _size[0] in global_params.en_code:
            _size = self.CalENCode(_size)
            for col in range(worksheet.ncols):
                if worksheet.cell_value(0, col) == _size:
                    return col

        for col in range(worksheet.ncols):
            if worksheet.cell_value(0, col) == self.CalSize(_size):
                return col
        return -1

    def CalENCode(self, _size):
        """
            规格化英文尺码
        """
        if _size[0] == "S" or _size[0] == "s":
            return "S"

        if _size[0] == "M" or _size[0] == "m":
            return "M"

        if _size[0] == "L" or _size[0] == "l":
            return "L"

        if _size[0] == "x" or _size[0] == "X":
            if _size[1] == "L" or _size[1] == "l":
                return "XL"
            elif _size[1] == "x" or _size[1] == "X":
                if _size[2] == "L" or _size[2] == "l":
                    return "XXL"
                elif _size[2] == "x" or _size[2] == "X":
                    return "XXL"

        return -1

    def CalSize(self, sizeDescription):
        """
            对尺码进行智能识别
        """
        _size = 0
        for i in range(len(sizeDescription)):
            if sizeDescription[i] >= "0" and sizeDescription[i] <= "9":
                _size = _size * 10 + int(sizeDescription[i])
            else:
                break
        return _size

    # 由货号得到产品名 - 厂家地址 - 厂家名
    def GetAdressAndShopName(self, cargoNumber):
        """
            对尺码进行智能识别
        """
        rowIndex = -1
        for t in range(1, self.worksheet.nrows):
            value = self.worksheet.cell(t, 0).value
            if isinstance(value, int) or isinstance(value, float):
                value = int(value)
            if str(cargoNumber) == str(value):
                rowIndex = t
                break
        if rowIndex == -1:
            print(str(cargoNumber) + " 没找到厂家")
            return ["", "", ""]
        productName = self.worksheet.cell(rowIndex, 1).value
        adress = self.worksheet.cell(rowIndex, 2).value
        shopName = self.worksheet.cell(rowIndex, 2).value
        return [productName, adress, shopName]

    def CalPriceLocation(self, _size):
        """
            计算尺码列位置
        """
        if _size[0] in global_params.en_code:
            return self.CalPriceLocationENCode(_size)
        theta = (self.CalSize(_size) - 90) / 5
        _col = 5 + theta
        return _col
