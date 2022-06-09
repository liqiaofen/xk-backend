from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from api.expense.flters import PayCategoryFilter, ExpenseFilter
from api.expense.serializers import PayCategoryCreateSerializer, PayCategorySerializer, ExpenseCreateSerializer, \
    ExpenseDateGroupSerializer, ExpenseImportSerializer, ExcelImportSerializer
from core.file_import.import_factory import ImportFactory
from core.mixin.views import BaseAPIViewMixin
from expense.models import PayCategory, Expense


class PayCategoryApiViewSet(BaseAPIViewMixin, ModelViewSet):
    queryset = PayCategory.objects.filter()
    filterset_class = PayCategoryFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return PayCategoryCreateSerializer
        return PayCategorySerializer

    @action(methods=['post'], detail=True)
    def move(self, request, **kwargs):
        obj = self.get_object()

        new_sort = int(request.data.get('sort', None))
        if new_sort is None:
            raise ValidationError('请提供新的位置')
        if new_sort < 0:
            raise ValidationError('请提供的位置>=0')
        PayCategory.objects.move(obj, new_sort)

        return Response()


class ExpenseApiViewSet(BaseAPIViewMixin, mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    queryset = Expense.objects.filter()
    filterset_class = ExpenseFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return ExpenseCreateSerializer
        if self.action == 'import_excel':
            return ExpenseImportSerializer
        return ExpenseDateGroupSerializer

    def get_queryset(self):
        queryset = super(ExpenseApiViewSet, self).get_queryset()
        if self.action == 'list':
            queryset = queryset.exclude_other().order_by('-pay_date').distinct('pay_date')
        return queryset

    @action(methods=['post'], detail=False, url_path='bill')
    def import_bill(self, request, **kwargs):
        ser = ExcelImportSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        bill_factory = ImportFactory()
        bill_factory.get_import(ser.validated_data['method'], ser.validated_data['file']).save(self.request)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False)
    def export_bill(self, request):
        pass

    @action(methods=['get'], detail=False, url_path='statistical/aggregate')
    def statistical_aggregate(self, request, **kwargs):
        """统计指定时间的支出综合"""
        qs = self.filter_queryset(self.get_queryset())  # ?date=2022-06 根据时间筛选了
        spending_amount = qs.spending().sum_amount()['sum_amount']
        income_amount = qs.income().sum_amount()['sum_amount']
        data = {
            'spending_sum': spending_amount if spending_amount else 0,
            'income_sum': income_amount if income_amount else 0
        }
        return Response(data)

    @action(methods=['get'], detail=False, url_path='statistical/day')
    def statistical_day(self, request, **kwargs):
        """每日支出消费金额"""
        qs = self.filter_queryset(self.get_queryset())

        start = self.request.GET.get('start_date', None)
        end = self.request.GET.get('end_date', None)
        if not start or not end:
            raise ValidationError('请传入查询的日期范围')
        spending_result = Expense.statistical_group_day(qs.spending(), start, end)

        most_spending = Expense.statistical_most_category_number_and_amount(qs.spending())  # 最多支出
        category_list, num_list, amount_list = list(zip(*most_spending)) if most_spending else [(), (), ()]

        income_result = Expense.statistical_group_day(qs.income(), start, end)

        return Response(data={
            'expense': {
                'categories': [i[5:] for i in spending_result.keys()],
                'spending': spending_result.values(),
                'income': income_result.values(),
            },
            'spending_num': [category_list, num_list],
            'spending_amount': [{'name': category, 'data': amount_list[index]} for index, category in
                                enumerate(category_list)],

        })

    @action(methods=['get'], detail=False, url_path='statistical/month')
    def statistical_month(self, request, **kwargs):
        """每月支出金额"""
        qs = self.filter_queryset(self.get_queryset())
        spending_result = dict.fromkeys([i for i in range(1, 13)], 0)
        spending = qs.spending().statistical_group_by_month()
        spending_result.update(spending)

        return Response(data={
            'expense': {
                'categories': spending_result.keys(),
                'spending': spending_result.values(),
            },
        })

    @action(methods=['get'], detail=False, url_path='statistical/year')
    def statistical_year(self, request, **kwargs):
        """每年支出金额"""
        qs = self.filter_queryset(self.get_queryset())
        spending_result = qs.spending().statistical_group_by_year()
        categories, spending = zip(*spending_result)
        return Response(data={
            'expense': {
                'categories': categories,
                'spending': spending,
            },
        })
