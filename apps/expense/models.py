from django.db import models, transaction
from django.db.models import Max, Sum, CharField, Count, F
from django.db.models.functions import ExtractMonth, Cast
from safedelete.models import SafeDeleteModel

from core.mixin.models import TimeStampedModel
from core.utils import get_date_range
from expense.choices import PayType, PayWay
from expense.query import PayCategoryQuerySet, ExpenseQuerySet


class PayCategoryManager(models.Manager):

    def get_queryset(self):
        return PayCategoryQuerySet(self.model, using=self._db)

    def pay_type(self, pay_type):
        # 支付类型查询
        return self.get_queryset().pay_type(pay_type)

    def move(self, obj, new_sort):
        qs = self.get_queryset().pay_type(obj.pay_type)
        with transaction.atomic():
            if obj.sort > new_sort:
                qs = qs.filter(sort__lt=obj.sort,
                               sort__gte=new_sort)
                qs.update(sort=F('sort') + 1)
            else:
                qs.filter(sort__lte=new_sort,
                          sort__gt=obj.sort).update(sort=F('sort') - 1)
            obj.sort = new_sort
            obj.save()

    @staticmethod
    def not_exist_to_create(names: list, pay_type, **kwargs):
        # 批量创建不存在的分类
        names = set(names)
        exist = set(
            PayCategory.objects.pay_type(pay_type).filter(name__in=names).values_list('name', flat=True))
        not_exist = names - exist
        if not_exist:
            max_sort = PayCategory.get_max_sort(pay_type)
            PayCategory.objects.bulk_create(
                [PayCategory(name=name, pay_type=pay_type, sort=max_sort + index, icon='naichaxiaochi') for index, name
                 in enumerate(not_exist)])
        # 返回所有的分类
        return PayCategory.objects.pay_type(pay_type).filter(name__in=names).values_list('name', 'id')


class PayCategory(TimeStampedModel):
    icon = models.CharField(verbose_name='图标', max_length=20)
    name = models.CharField(verbose_name='名称', max_length=6)
    color = models.CharField(verbose_name='颜色', max_length=20, default='#333333')
    sort = models.PositiveSmallIntegerField(verbose_name='排序')
    pay_type = models.PositiveSmallIntegerField(verbose_name='类型', choices=PayType.choices, default=PayType.SPENDING)
    objects = PayCategoryManager()

    class Meta:
        verbose_name = "消费类别"
        verbose_name_plural = verbose_name
        ordering = ['pay_type', 'sort']
        unique_together = ['name', 'pay_type']

    def save(self, *args, **kwargs):
        if self.sort is None:
            self.sort = self.get_max_sort(self.pay_type)
        super().save(*args, **kwargs)

    @staticmethod
    def get_max_sort(pay_type):
        """获取最大的sort"""
        result = PayCategory.objects.pay_type(pay_type).aggregate(Max('sort'))
        return result['sort__max'] + 1 if result['sort__max'] else 0


class ExpenseManager(models.Manager):

    def get_queryset(self):
        return ExpenseQuerySet(self.model, using=self._db)


class Expense(TimeStampedModel):
    note = models.CharField(verbose_name='备注', max_length=200, blank=True)
    addr = models.JSONField(verbose_name='消费地址')
    category = models.ForeignKey(PayCategory, on_delete=models.CASCADE, verbose_name='交易分类')
    pay_way = models.PositiveSmallIntegerField(verbose_name='支付方式', choices=PayWay.choices, default=PayWay.CASH)
    pay_type = models.PositiveSmallIntegerField(verbose_name='类型', choices=PayType.choices,
                                                default=PayType.SPENDING)
    pay_date = models.DateField(verbose_name='支付日期')
    pay_time = models.TimeField(verbose_name='支付时间')
    amount = models.DecimalField(verbose_name='支付金额', decimal_places=2, max_digits=6)
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    objects = ExpenseManager()

    class Meta:
        verbose_name = "费用"
        verbose_name_plural = verbose_name
        ordering = ['-pay_date']

    @staticmethod
    def statistical_group_month(qs):
        result = dict.fromkeys([i for i in range(1, 13)], 0)
        qs_values = qs.annotate(month=ExtractMonth('pay_date')).values('month').annotate(
            total=Sum('amount')).values_list('month', 'total').order_by()
        result.update(qs_values)
        return result

    @staticmethod
    def statistical_group_day(qs, start, end):
        result = dict.fromkeys(list(get_date_range(start, end)), 0)  # 获取时间范围字典，默认值为0 {'2022-04-13':0, ...}
        qs_values = qs.values('pay_date').annotate(total=Sum('amount'),
                                                   pay_date_str=Cast('pay_date', CharField())  # 将时间转换成字符串
                                                   ).values_list('pay_date_str', 'total').order_by()
        result.update(qs_values)  # 更新时间范围字典{'2022-04-13':10, ...}
        return result

    @staticmethod
    def statistical_most_category_number_and_amount(qs):
        qs_values = qs.values('category').annotate(
            num=Count('id'),
            amount=Sum('amount')
        ).order_by('-amount').values_list('category__name', 'num', 'amount')
        return qs_values
