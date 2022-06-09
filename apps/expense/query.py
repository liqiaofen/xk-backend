from django.db import models
from django.db.models import Sum
from django.db.models.functions import ExtractYear, ExtractMonth

from expense.choices import PayType


class PayCategoryQuerySet(models.QuerySet):

    def pay_type(self, pay_type):
        return self.filter(pay_type=pay_type)


class ExpenseQuerySet(models.QuerySet):

    def spending(self):
        # 支出
        return self.filter(pay_type=PayType.SPENDING)

    def income(self):
        # 收入
        return self.filter(pay_type=PayType.INCOME)

    def sum_amount(self):
        return self.filter().aggregate(sum_amount=Sum('amount'))

    def exclude_other(self):
        return self.exclude(pay_type=PayType.OTHER)

    def statistical_group_by_year(self, values_list=None):
        """统计-根据年分组"""
        if values_list is None:
            values_list = ['year', 'total']
        return self.annotate(year=ExtractYear('pay_date')).values('year').annotate(
            total=Sum('amount')).values_list(*values_list).order_by()

    def statistical_group_by_month(self, values_list=None):
        """统计-根据月分组"""
        if values_list is None:
            values_list = ['month', 'total']
        return self.annotate(month=ExtractMonth('pay_date')).values('month').annotate(
            total=Sum('amount')).values_list(*values_list).order_by()
