from django_filters import rest_framework as filters
from rest_framework.exceptions import ValidationError

from expense.models import Expense, PayCategory


class ExpenseFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='pay_date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='pay_date', lookup_expr='lt')
    year = filters.CharFilter(field_name='pay_date__year')
    date = filters.CharFilter(method='find_date')
    sort = filters.OrderingFilter(
        fields=(
            ('pay_date', 'pay_date'),
        )
    )

    class Meta:
        model = Expense
        fields = ['category', 'date', 'pay_way', 'pay_type', 'pay_date', 'amount', 'sort', 'year']

    def find_date(self, queryset, name, value):
        try:
            date = value.split('-')
            queryset = queryset.filter(pay_date__year=date[0])
            if len(date) == 2:
                queryset = queryset.filter(pay_date__month=date[1])
            if len(date) == 3:
                queryset = queryset.filter(pay_date__month=date[2])
        except:
            raise ValidationError('错误的时间格式(eg:2020-04)')
        return queryset


class PayCategoryFilter(filters.FilterSet):
    sort = filters.OrderingFilter(
        fields=(
            ('sort', 'sort'),
        )
    )

    class Meta:
        model = PayCategory
        fields = ['pay_type', 'sort']
