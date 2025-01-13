class OrderAmount:
    def __init__(self, sum_product_payment=0, shipping_fee=0, total_amount=0, refund=0, refund_shipping_fee=0):
        self.id = ""
        self.sum_product_payment = sum_product_payment
        self.shipping_fee = shipping_fee
        self.total_amount = total_amount
        self.refund = refund
        self.refund_shipping_fee = refund_shipping_fee
        self.order_num = 0
