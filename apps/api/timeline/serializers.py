from collections import defaultdict
from datetime import datetime, timedelta

from rest_framework import serializers

from api.authentication.serializers import UserInfoSerializer
from core import serpy
from core.mixin.serializers import QuerySerializerMixin, BulkCreateListSerializer
from timeline.models import TimeLine, LifeRecordImage, LifeRecord


class TimeLineItemSerializer(serpy.Serializer):
    id = serpy.IntField()
    content = serpy.StrField()
    exact_date = serpy.StrField()
    icon = serpy.StrField()
    color = serpy.StrField()
    addr = serpy.JsonField()


class TimeLineSerializer(QuerySerializerMixin, serpy.DictSerializer):
    def __init__(self, instance=None, many=False, data=None, context=None,
                 **kwargs):
        if context['action'] == 'list':
            result = defaultdict(list)
            if len(instance) > 0:  # 没有分组数据，直接跳过
                min_date = datetime.strptime(instance[-1]['year_month'], "%Y-%m")
                # 获取下个月的一号
                max_date = (datetime.strptime(instance[0]['year_month'], "%Y-%m") + timedelta(days=32)).replace(day=1)

                qs = TimeLine.objects.filter(exact_date__gte=min_date, exact_date__lt=max_date).annotate_fmt_datetime(
                    'exact_date')
                for item in qs:
                    result[str(item.year_month)].append(item)
            context['items'] = result
        super(TimeLineSerializer, self).__init__(instance=instance, many=many, data=data, context=context,
                                                 **kwargs)

    year_month = serpy.StrField()
    items = serpy.MethodField()

    def get_items(self, obj):
        return TimeLineItemSerializer(instance=self.context['items'][str(obj['year_month'])], many=True).data


class TimeLineCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = TimeLine
        fields = ['content', 'exact_date', 'icon', 'color', 'created_by', 'addr']


class TimeLineImportSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        instance = TimeLine(**validated_data)
        if isinstance(self._kwargs['data'], dict):  # 字典为单个创建， 批量创建为list
            instance.save()
        return instance

    class Meta:
        model = TimeLine
        fields = ['content', 'exact_date', 'icon', 'color', 'addr']
        list_serializer_class = BulkCreateListSerializer

    def validate_addr(self, value):
        if isinstance(value, str):
            return {'name': value}
        return value


class LifeRecordImageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LifeRecordImage
        fields = ['image']


class LifeRecordCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = LifeRecord
        fields = ['content', 'images', 'created_by']


class LifeRecordImageListSerializer(serpy.Serializer):
    image_url = serpy.StrField()


class LifeRecordListSerializer(QuerySerializerMixin, serpy.Serializer):
    PREFETCH_FIELDS = ['images']
    content = serpy.StrField()
    images = serpy.MethodField()
    id = serpy.StrField()
    created = serpy.DateTimeField(fmt='%m/%d %H:%M')
    created_by = serpy.MethodField()

    def get_images(self, obj):
        images = LifeRecordImageListSerializer(instance=obj.images.all(), many=True).data
        return [image['image_url'] for image in images]

    def get_created_by(self, obj):
        return UserInfoSerializer(instance=obj.created_by).data
