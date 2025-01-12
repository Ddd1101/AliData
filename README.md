# AliData
查 "waitbuyerreceive" 订单
baseInfo-refundStatus -> waitselleragree
refund为0, 
productItems-'refundStatus': 'WAIT_SELLER_AGREE',
判断该产品项是否退款

交易关闭也有退款

{
	'baseInfo': {
		'discount': 0,
		'alipayTradeId': 'UNCREATED',

没付款就取消，baseInfo->alipayTradeId = UNCREATED