class Settings:
    def __init__(self, shopNames,
                 mode,
                 filter: list,
                 createStartTime,
                 createEndTime,
                 orderStatus: list,
                 isPrintOwn,
                 limitDeliveredTime:list,
                 isPrintUnitPrice):
        self.shopName = shopNames
        self.mode = mode
        self.filter = filter
        self.createStartTime = createStartTime
        self.createEndTime = createEndTime
        self.orderStatus = orderStatus
        self.isPrintOwn = isPrintOwn
        self.limitDeliveredTime = limitDeliveredTime
        self.isPrintUnitPrice = isPrintUnitPrice
