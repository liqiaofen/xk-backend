from django.db import models


class PayWay(models.IntegerChoices):
    WECHAT_PAY = 0, '微信'
    ALI_PAY = 1, '花呗'
    BANK_CARD = 2, '银行卡'
    CASH = 3, '现金'
    OTHER = 4, '其他'


class PayType(models.IntegerChoices):
    SPENDING = 0, '支出'
    INCOME = 1, '收入'
    OTHER = 2, '其他'
