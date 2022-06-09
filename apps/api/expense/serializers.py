from collections import defaultdict

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core import serpy
from core.mixin.serializers import UniqueTogetherValidatorMixin, MappedChoiceField, BulkCreateListSerializer
from expense.models import PayCategory, Expense, PayWay


class PayCategorySerializer(serpy.Serializer):
    id = serpy.IntField()
    icon = serpy.StrField()
    name = serpy.StrField()
    color = serpy.StrField()
    sort = serpy.IntField()
    pay_type = serpy.IntField()


class PayCategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayCategory
        fields = ['icon', 'name', 'color', 'pay_type', 'sort', 'id']
        read_only_fields = ['sort', 'id']
        validators = [
            UniqueTogetherValidatorMixin(
                queryset=model.objects.all(),
                fields=('name', 'pay_type'),
            )
        ]


class ExpenseDateGroupSerializer(serpy.Serializer):

    def __init__(self, instance=None, many=False, data=None, context=None,
                 **kwargs):
        if context['action'] == 'list':
            # 查出每个日期内的账单, 不查询转账
            result = defaultdict(list)
            if len(instance) > 0:  # 没有分组数据，直接跳过
                qs = Expense.objects.filter().exclude_other()
                if len(instance) == 1:  # 一个分组，只查询当天的，
                    qs = qs.filter(pay_date=instance[0].pay_date)
                elif len(instance) > 1:
                    qs = qs.filter(pay_date__gte=instance[-1].pay_date,
                                   pay_date__lte=instance[0].pay_date)
                qs = qs.prefetch_related('created_by', 'category')
                for obj in qs:
                    result[str(obj.pay_date)].append(obj)
            context['expenses'] = result
        super(ExpenseDateGroupSerializer, self).__init__(instance=instance, many=many, data=data, context=context,
                                                         **kwargs)

    pay_date = serpy.DateTimeField(fmt='%m/%d %a')
    expenses = serpy.MethodField()

    def get_expenses(self, obj):
        return ExpenseSerializer(instance=self.context['expenses'][str(obj.pay_date)], many=True).data


class ExpenseSerializer(serpy.Serializer):
    id = serpy.StrField()
    note = serpy.StrField()
    addr = serpy.JsonField()
    category = serpy.MethodField()
    pay_way = serpy.StrField(attr='get_pay_way_display')
    pay_type = serpy.IntField()
    pay_date = serpy.StrField()
    amount = serpy.StrField()
    created_by = serpy.StrField()

    def get_category(self, obj):
        return PayCategorySerializer(obj.category).data


class ExpenseCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Expense
        fields = ['note', 'addr', 'category', 'pay_way', 'pay_type', 'pay_time', 'pay_date', 'amount', 'created_by']
        extra_kwargs = {'note': {'required': False}, 'addr': {'required': False},
                        # 'pay_way': {'error_messages': {'invalid_choice': "不存在的"}}
                        }


class ExpenseImportSerializer(serializers.ModelSerializer):
    addr = serializers.CharField(required=False)
    pay_way = MappedChoiceField(choices=PayWay.choices, default=PayWay.BANK_CARD)
    category_id = serializers.CharField()

    pay_date = serializers.CharField()
    pay_time = serializers.CharField(required=False)

    def create(self, validated_data):
        instance = Expense(**validated_data)
        if isinstance(self._kwargs['data'], dict):  # 字典为单个创建， 批量创建为list
            instance.save()
        return instance

    class Meta:
        model = Expense
        fields = ['note', 'addr', 'category_id', 'pay_way', 'pay_type', 'pay_date', 'pay_time', 'amount']
        extra_kwargs = {'note': {'required': False}}
        list_serializer_class = BulkCreateListSerializer

    def validate(self, attrs):
        d, t = attrs['pay_date'].split(' ')
        attrs['pay_date'] = d.replace('/', '-')
        attrs['pay_time'] = t
        return attrs

    def validate_addr(self, value):
        if isinstance(value, str):
            return {'name': value}
        return value

    def validate_category_id(self, value):
        return self.context['categories'][value]


class ExcelImportSerializer(serializers.Serializer):
    method = serializers.CharField()
    file = serializers.FileField()

    def validate_file(self, file):
        if file.name.split('.')[-1] not in ['xlsx', 'xls', 'csv']:
            raise ValidationError('错误的文件类型')
        return file
