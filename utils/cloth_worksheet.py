import global_params
import openpyxl


class ClothWorksheet:
    def __init__(self, filepath, shop_type):
        """初始化 Person 对象"""
        self.filepath = filepath
        workbook = openpyxl.load_workbook(filepath, data_only=True)
        sheetsName = workbook.sheetnames
        self.worksheet = workbook[sheetsName[0]]  # 获取工作簿中所有表格中的的第一个表格
        self.shop_type = shop_type

    def get_sheet(self):
        return self.worksheet

    def get_price_sheet(self):
        workbook = openpyxl.load_workbook(self.filepath, data_only=True)
        sheetsName = workbook.sheetnames
        self.worksheet = workbook[sheetsName[0]]  # 获取工作簿中所有表格中的的第一个表格
        return self.worksheet

    def get_cargo_number_set(self):
        """价格表中所有货号（第一列）的集合，用于识别订单货号去掉规格后缀后的真实货号"""
        if not hasattr(self, "_cargo_number_set"):
            self._cargo_number_set = set()
            for t in range(2, self.worksheet.max_row + 1):
                value = self.worksheet.cell(t, 1).value
                if value is not None:
                    self._cargo_number_set.add(str(value))
        return self._cargo_number_set

    def find_price(self, cargoNumber, skuInfosValue, colNum=0):
        """按货号 + 尺码查价，返回 (价格, 是否找到)"""
        worksheet = self.worksheet
        if worksheet is None:
            worksheet = self.get_price_sheet()
        if self.shop_type == global_params.ShopType.ALI_CHILD_CLOTH:
            rowIndex = -1
            col = colNum + 1  # openpyxl 列从 1 开始
            for t in range(2, worksheet.max_row + 1):
                value = worksheet.cell(t, col).value
                if isinstance(value, int) or isinstance(value, float):
                    value = int(value)
                if str(cargoNumber) == str(value):
                    rowIndex = t
                    break
            if rowIndex == -1:
                return 0, False  # 货号没找到
            colIndex = self.CalPriceColByName(skuInfosValue, worksheet)
            if colIndex == -1:
                return 0, False  # 尺码列没找到
            _price = worksheet.cell(rowIndex, int(colIndex) + 1).value
            if _price is None or _price == "":
                return 0, False  # 尺码对应价格为空
            return float(_price), True
        return 0, False

    def GetCost(self, cargoNumber, skuInfosValue, colNum=0):
        price, found = self.find_price(cargoNumber, skuInfosValue, colNum)
        if not found:
            print(cargoNumber + " 规格：" + skuInfosValue + " ： 未找到对应成本")
        return price

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
        if not _size:
            return -1
        _size = _size.upper()
        if _size == "2XL":
            _size = "XXL"
        elif _size == "3XL":
            _size = "XXXL"
        if _size[0] in global_params.en_code:
            _size = self.CalENCode(_size)
            for col in range(1, worksheet.max_column + 1):
                if worksheet.cell(1, col).value == _size:
                    return col - 1

        for col in range(1, worksheet.max_column + 1):
            if worksheet.cell(1, col).value == self.CalSize(_size):
                return col - 1
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
        for t in range(2, self.worksheet.max_row + 1):
            value = self.worksheet.cell(t, 1).value
            if isinstance(value, int) or isinstance(value, float):
                value = int(value)
            if str(cargoNumber) == str(value):
                rowIndex = t
                break
        if rowIndex == -1:
            print(str(cargoNumber) + " 没找到厂家")
            return ["", "", ""]
        productName = self.worksheet.cell(rowIndex, 2).value
        adress = self.worksheet.cell(rowIndex, 3).value
        shopName = self.worksheet.cell(rowIndex, 3).value
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

    def write_out(self):
        pass
