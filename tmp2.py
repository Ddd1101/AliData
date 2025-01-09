def GetBeihuoJson(
        self,
        orders,
        is_print_own,
        mode=0,
        limit_delivered_time={},
        isPrintUnitPrice=False,
):
    self.Logout("start GetBeihuoJson", "debug")
    beihuo_json = {}

    for order in orders:
        if mode != 0 and (
                "sellerRemarkIcon" not in order["baseInfo"]
                or order["baseInfo"]["sellerRemarkIcon"] != str(mode)
        ):
            continue
        if "sellerRemarkIcon" in order["baseInfo"] and (
                order["baseInfo"]["sellerRemarkIcon"] == "2"
                or order["baseInfo"]["sellerRemarkIcon"] == "3"
        ):
            continue

        for product_item in order["productItems"]:
            if "refund" in product_item and product_item["refund"] > 0:
                continue
            cargo_number_tag = (
                "cargoNumber"
                if "cargoNumber" in product_item
                else "productCargoNumber"
            )
            cargo_number = product_item[cargo_number_tag]
            color = product_item["skuInfos"][0]["value"]
            height = product_item["skuInfos"][1]["value"]

            cargo_number = cargo_number.split("【")[-1]

            product_dict = beihuo_json.setdefault(cargo_number, {}).setdefault(
                color,
                {"products": {}, "productImgUrl": product_item["productImgUrl"][1]},
            )
            product_dict["products"].setdefault(height, {"quantity": 0})
            product_dict["products"][height]["quantity"] += product_item["quantity"]
            product_dict["products"][height]["price"] = GetCost(
                cargo_number, height
            )
            product_dict["products"][height]["cost"] = (
                    product_dict["products"][height]["price"]
                    * product_dict["products"][height]["quantity"]
            )

    self.GetTable(beihuo_json, is_print_own, isPrintUnitPrice)
    self.Logout("end GetBeihuoJson", "debug")


def GetTable(self, BeihuoJson, isPrintOwn, isPrintUnitPrice):
    self.Logout("start GetTable", "debug")
    # 制表
    productsCountByShopName = {}
    BeihuoList = []
    BeihuoTable = []
    for item in BeihuoJson:
        BeihuoList.append(item)
        adressAndShopName = GetAdressAndShopName(item)
        BeihuoList.append(adressAndShopName[2])
        BeihuoList.append(adressAndShopName[1])
        BeihuoList.append(adressAndShopName[0])
        if adressAndShopName[2] not in productsCountByShopName:
            productsCountByShopName[adressAndShopName[2]] = [0, 0]
        for color in BeihuoJson[item]:
            BeihuoList.append(color)
            BeihuoList.append(BeihuoJson[item][color]["productImgUrl"])
            heightTable = []
            heightList = []
            for height in BeihuoJson[item][color]["products"]:
                heightList.append(height)
                heightList.append(
                    BeihuoJson[item][color]["products"][height]["quantity"]
                )
                productsCountByShopName[adressAndShopName[2]][0] += BeihuoJson[
                    item
                ][color]["products"][height][
                    "quantity"
                ]  # 叠加总数
                productsCountByShopName[adressAndShopName[2]][1] += (
                        BeihuoJson[item][color]["products"][height]["quantity"]
                        * BeihuoJson[item][color]["products"][height]["price"]
                )
                heightList.append(
                    BeihuoJson[item][color]["products"][height]["price"]
                )
                heightTable.append(heightList.copy())
                heightList.clear()
            heightTable.sort(key=lambda x: x[0])
            BeihuoList.append(heightTable)
            BeihuoTable.append(BeihuoList.copy())
            BeihuoList.pop()
            BeihuoList.pop()
            BeihuoList.pop()
        BeihuoList.pop()
        BeihuoList.pop()
        BeihuoList.pop()
        BeihuoList.pop()

    self.Logout("制表结束", "info")

    # 排序 拿货地规整
    BeihuoTable.sort(key=lambda x: [x[1], x[2]])

    # 写表
    savePath = self.ui.saveFilePath.toPlainText().split(".")[0]

    # 保存备货单
    BH_wb = xlsxwriter.Workbook(
        savePath + "/" + datetime.now().strftime("%m_%d_%H_%M_%S") + ".xlsx"
    )
    BH_sheet = BH_wb.add_worksheet("BH")
    BH_pay_sheet = BH_wb.add_worksheet("pay")
    BH_x = 0
    BH_y = 0

    shopNameTmp = ""

    sumCountX = 0

    piecesCount = 0  # 统计总价格
    sumReporter = GetFactoryGrid()
    for _list in BeihuoTable:
        if (not isPrintOwn) and (_list[1] == "朝新" or _list[2] == "朝新"):
            continue
        BH_sheet.write(BH_x, BH_y, _list[0])  # 货号
        BH_y += 1
        BH_sheet.write(BH_x, BH_y, _list[1])
        BH_y += 1
        # BH_sheet.write(BH_x, BH_y, _list[2])
        # BH_y += 1
        BH_sheet.write(BH_x, BH_y, _list[3])
        BH_y += 1
        BH_sheet.write(BH_x, BH_y, _list[4])
        BH_y += 1

        # 多尺码序列化
        amount = ""
        amount_with_price = ""
        for height in _list[6]:
            if amount != "":
                amount += "\n"

            if amount_with_price != "":
                amount_with_price += "\n"

            if isPrintUnitPrice:
                amount_with_price = (
                        amount_with_price
                        + NumFormate4Print(height[0])
                        + " "
                        + str(height[1])
                        + "件"
                        + " "
                        + str(height[2])
                )

            amount = (
                    amount + NumFormate4Print(height[0]) + " " + str(height[1]) + "件"
            )

        BH_sheet.write(BH_x, BH_y, amount)
        if amount_with_price:
            BH_sheet.write(BH_x, BH_y + 3, amount_with_price)

        BH_y += 1

        # 多尺码标识
        if len(amount.split("\n")) >= 2:
            BH_sheet.write(BH_x, BH_y + 3, "多尺码")

        # 插图
        imageName = _list[5].split(".jpg")[0].split("/")[-1]

        if ImageHandler.IsImageExist(imageName):
            time.sleep(0.2)
            # 本地存有图片，读出
            self.Logout("before ReadImageFromDir" + imageName, "debug")
            imageData = ImageHandler.ReadImageFromDir(imageName)
            self.Logout("after ReadImageFromDir" + imageName, "debug")

            self.Logout("读取本地图片")

        else:
            self.Logout("下载图片")
            # time.sleep(0.5)
            rt = self.RequestPic(_list[5])

            if rt == 420:
                # 本地存有图片，读出
                self.Logout("before ReadImageFromDir" + imageName, "debug")
                imageData = ImageHandler.ReadImageFromDir(imageName)
                self.Logout("after ReadImageFromDir" + imageName, "debug")

                self.Logout("读取到手动下载图片")
            elif rt == 400:
                imageData = ImageHandler.ReadImageFromDir(imageName)
            else:
                self.Logout("before 1 ReadImageFromD net " + imageName, "debug")
                imageDataRaw = rt.read()
                self.Logout("2  ReadImageFromD net " + imageName, "debug")

                imageData = io.BytesIO(imageDataRaw)
                self.Logout("after ReadImageFromD net " + imageName, "debug")

                BH_sheet.insert_image(BH_x, BH_y, _list[4],
                                      {'image_data': imageData, 'x_offset': 5, 'x_scale': 0.1, 'y_scale': 0.1})
                # 保存图片
                ImageHandler.SaveImage(imageData.getvalue(), imageName)
                self.Logout("save ReadImageFromD net " + imageName)

        self.Logout("before insert_image", "debug")

        width, height = Image.open(imageData).size

        x_scale = (800 * 0.14) / width
        y_scale = (800 * 0.14) / height

        BH_sheet.insert_image(
            BH_x,
            BH_y,
            _list[4],
            {
                "image_data": imageData,
                "x_offset": 3,
                "x_scale": x_scale,
                "y_scale": y_scale,
            },
        )
        self.Logout("after insert_image", "debug")

        # 只能处理到倒数第二个厂商
        if _list[1] != shopNameTmp:
            if shopNameTmp != "":
                piecesCount += productsCountByShopName[shopNameTmp][1]
                self.Logout2(
                    shopNameTmp
                    + " 总件数："
                    + str(productsCountByShopName[shopNameTmp][0])
                    + " | 货款："
                    + str(round(productsCountByShopName[shopNameTmp][1], 3))
                )
                # 输出字体
                priceStyle = BH_wb.add_format(
                    {
                        # "fg_color": "yellow",  # 单元格的背景颜色
                        "bold": 1,  # 字体加粗
                        "align": "left",  # 对齐方式
                        "valign": "vcenter",  # 字体对齐方式
                        "font_color": "red",  # 字体颜色
                    }
                )
                writeStr = (
                        shopNameTmp
                        + " 总件数："
                        + str(productsCountByShopName[shopNameTmp][0])
                )
                BH_sheet.merge_range(
                    "A" + str(sumCountX + 1) + ":D" + str(sumCountX + 1),
                    writeStr,
                    priceStyle,
                )

                # 商家 & 货款  信息收集
                shopNameSplited = shopNameTmp[
                                  0: SplitChineseAndPinyin(shopNameTmp) + 1
                                  ]

                if shopNameSplited not in sumReporter:
                    sumReporter[shopNameSplited] = {}
                sumReporter[shopNameSplited]["num"] = productsCountByShopName[
                    shopNameTmp
                ][0]
                sumReporter[shopNameSplited]["payment"] = round(
                    productsCountByShopName[shopNameTmp][1], 3
                )

            shopNameTmp = _list[1]

        # 最后一个单独处理
        if _list == BeihuoTable[-1]:
            sumCountX += 6
            if shopNameTmp != "":
                piecesCount += productsCountByShopName[shopNameTmp][1]
                self.Logout2(
                    shopNameTmp
                    + " 总件数："
                    + str(productsCountByShopName[shopNameTmp][0])
                    + " | 货款："
                    + str(round(productsCountByShopName[shopNameTmp][1], 3))
                )
                # 输出字体
                priceStyle = BH_wb.add_format(
                    {
                        # "fg_color": "yellow",  # 单元格的背景颜色
                        "bold": 1,  # 字体加粗
                        "align": "left",  # 对齐方式
                        "valign": "vcenter",  # 字体对齐方式
                        "font_color": "red",  # 字体颜色
                    }
                )
                writeStr = (
                        shopNameTmp
                        + " 总件数："
                        + str(productsCountByShopName[shopNameTmp][0])
                )
                BH_sheet.merge_range(
                    "A" + str(sumCountX + 1) + ":D" + str(sumCountX + 1),
                    writeStr,
                    priceStyle,
                )

                # 商家 & 货款  信息收集
                shopNameSplited = shopNameTmp[
                                  0: SplitChineseAndPinyin(shopNameTmp) + 1
                                  ]

                if shopNameSplited not in sumReporter:
                    sumReporter[shopNameSplited] = {}
                sumReporter[shopNameSplited]["num"] = productsCountByShopName[
                    shopNameTmp
                ][0]
                sumReporter[shopNameSplited]["payment"] = round(
                    productsCountByShopName[shopNameTmp][1], 3
                )

            shopNameTmp = _list[1]

        sumCountX = BH_x + 1

        if len(_list[6]) >= 5:
            BH_x += 2
        else:
            theta = 5 - len(_list[6])
            BH_x = BH_x + theta + 2

        BH_y = 0

    sumCountX += 6

    # 输出统计信息
    self.PrintSumReporter(BH_wb, BH_pay_sheet, sumReporter, piecesCount)

    try:
        BH_wb.close()
    except Exception as e:
        print("程序出现异常:", e)

    self.Logout("end GetTable", "debug")