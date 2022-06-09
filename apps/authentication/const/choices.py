from django.db import models


# https://blog.csdn.net/weixin_42134789/article/details/107273847
class GenderChoice(models.TextChoices):
    GENDER_MALE = 'XX', '男'
    GENDER_FEMALE = 'XY', '女'
    GENDER_ALIEN = 'ET', '外星人'
