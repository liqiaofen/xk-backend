from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.validators import qs_exists


class UniqueTogetherValidatorMixin(UniqueTogetherValidator):
    """联合唯一校验"""
    message = '当前{message0}下已经存在相同的{message1}'

    def filter_queryset(self, attrs, queryset, serializer):
        queryset = super().filter_queryset(attrs, queryset, serializer)
        # 改下了下面的内容，通过model找到model中定义的联合唯一字段，只过滤company这个字段，其他字段并不会过滤
        if isinstance(serializer, serializers.ModelSerializer):
            model = serializer.Meta.model
            unique_togethers = model._meta.unique_together
            unique_together_fields = []
            for unique_together in unique_togethers:
                unique_together_fields.extend(unique_together)
            # 判断是否含有特殊字段，可进行处理，例如： company
        return queryset

    def __call__(self, attrs, serializer):
        # 这边代码来自于UniqueTogetherValidator中
        # company相关的联合校验在filter_queryset中进行，如果model中定义了其他的联合唯一，在下面进行处理。
        self.enforce_required_fields(attrs, serializer)
        queryset = self.queryset
        queryset = self.filter_queryset(attrs, queryset, serializer)
        queryset = self.exclude_current_instance(attrs, queryset, serializer.instance)

        # Ignore validation if any field is None
        checked_values = [
            value for field, value in attrs.items() if field in self.fields
        ]
        if None not in checked_values and qs_exists(queryset):
            # 改写了原方法中下面的内容
            # self.fields 是实例化时传入的字段，代表要进一步过滤哪些字段来处理联合唯一。
            # 由于serializer中都不会有company字段，如果有和公司相关的联合唯一，不用传入company，self.fields中没有company，
            # 只会有另一个联合唯一校验字段，这样就方便前端在具体某个字段上显示错误信息
            first_field = self.fields[0]
            message1 = serializer.fields[first_field].label + f'({checked_values[0]})'
            message0 = ''
            for field in self.fields[1:]:
                message0 += serializer.fields[field].label + '、'

            errors = {first_field: self.message.format(message0=message0[:-1], message1=message1)}  # 这里主要是 指定报错字段
            raise ValidationError(errors)


# 参考 https://riptutorial.com/django-rest-framework/example/7832/speed-up-serializers-queries
# 也可以看看 http://blog.oneapm.com/apm-tech/304.html
# 这个也可以参考下：https://stackoverflow.com/questions/26593312/optimizing-database-queries-in-django-rest-framework/26598897#26598897
class QuerySerializerMixin:
    """根据情况联表查询，减少sql次数"""
    PREFETCH_FIELDS = []  # for M2M fields
    RELATED_FIELDS = []  # for ForeignKeys

    @classmethod
    def get_related_queries(cls, queryset):
        # This method we will use in our ViewSet
        # for modify queryset, based on RELATED_FIELDS and PREFETCH_FIELDS
        if cls.RELATED_FIELDS:
            queryset = queryset.select_related(*cls.RELATED_FIELDS)
        if cls.PREFETCH_FIELDS:
            queryset = queryset.prefetch_related(*cls.PREFETCH_FIELDS)
        return queryset


class BaseDynamicFieldsPlugin:
    def __init__(self, serializer):
        self.serializer = serializer

    def can_dynamic(self):
        # 判断是请求是不是GET方法
        try:
            request = self.get_request()
            method = request.method
        except (AttributeError, TypeError, KeyError):
            # The serializer was not initialized with request context.
            return False

        if method != 'GET':
            return False
        return True

    def get_request(self):
        return self.serializer.context['request']

    def get_query_params(self):
        request = self.get_request()
        try:
            query_params = request.query_params
        except AttributeError:
            # DRF 2
            query_params = getattr(request, 'QUERY_PARAMS', request.GET)
        return query_params

    def get_exclude_field_names(self):
        return set()


class QueryFieldsMixin(BaseDynamicFieldsPlugin):
    # https://github.com/wimglenn/djangorestframework-queryfields/

    # If using Django filters in the API, these labels mustn't conflict with any model field names.
    include_arg_name = 'fields'  # 表示需要返回哪些字段
    exclude_arg_name = 'fields!'  # 表示返回内容中排除哪些字段

    # Split field names by this string.  It doesn't necessarily have to be a single character.
    # Avoid RFC 1738 reserved characters i.e. ';', '/', '?', ':', '@', '=' and '&'
    delimiter = ','

    def get_exclude_field_names(self):
        query_params = self.get_query_params()
        includes = query_params.getlist(self.include_arg_name)
        include_field_names = {name for names in includes for name in names.split(self.delimiter) if name}

        excludes = query_params.getlist(self.exclude_arg_name)
        exclude_field_names = {name for names in excludes for name in names.split(self.delimiter) if name}

        if not include_field_names and not exclude_field_names:
            # No user fields filtering was requested, we have nothing to do here.
            return []

        serializer_field_names = set(self.serializer.fields)
        fields_to_drop = serializer_field_names & exclude_field_names

        if include_field_names:
            fields_to_drop |= serializer_field_names - include_field_names
        return fields_to_drop


class DynamicFieldsMixin:
    """
    可以控制显示不同的字段，mini 最少，small 不包含关系
    """
    dynamic_fields_plugins = [QueryFieldsMixin]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        exclude_field_names = set()
        for cls in self.dynamic_fields_plugins:
            # cls就是QueryFieldsMixin，实例化时候需要传入serializer参数，self就是当前view中调用的serializer
            plugin = cls(self)
            if not plugin.can_dynamic():
                continue
            exclude_field_names |= set(plugin.get_exclude_field_names())

        for field in exclude_field_names or []:
            self.fields.pop(field, None)


class BulkCreateListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = super(BulkCreateListSerializer, self).create(validated_data)
        try:
            self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise ValidationError(e)
        # 信号量处理
        return result


class MappedChoiceField(serializers.ChoiceField):
    # https://stackoverflow.com/questions/28945327/django-rest-framework-with-choicefield

    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return ''
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == '' and self.allow_blank:
            return ''

        for key, val in self._choices.items():
            if val == data:
                return key
        if self.default:
            return self.default
        self.fail('invalid_choice', input=data)
