from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.timeline.flters import TimeLineFilter
from api.timeline.serializers import TimeLineCreateSerializer, TimeLineSerializer, LifeRecordCreateSerializer, \
    LifeRecordImageCreateSerializer, LifeRecordListSerializer
from core.mixin.views import LoverAPIViewMixin
from core.utils import get_object_or_error
from timeline.models import TimeLine, LifeRecord, LifeRecordImage


class TimeLineApiViewSet(LoverAPIViewMixin, ModelViewSet):
    queryset = TimeLine.objects.filter()
    filterset_class = TimeLineFilter

    def get_serializer_class(self):
        if self.action in ['create']:
            return TimeLineCreateSerializer
        return TimeLineSerializer

    def get_queryset(self):
        queryset = super(TimeLineApiViewSet, self).get_queryset()
        if self.action == 'list':
            # 分组月份
            queryset = queryset.annotate_fmt_datetime('exact_date').order_by('-year_month', '-exact_date').distinct(
                'year_month').values('year_month')

        return queryset


class LifeRecordApiView(LoverAPIViewMixin, ModelViewSet):
    queryset = LifeRecord.objects.filter()

    def get_serializer_class(self):
        if self.action in ['create']:
            return LifeRecordCreateSerializer
        elif self.action == 'upload_image':
            return LifeRecordImageCreateSerializer
        return LifeRecordListSerializer

    @action(methods=['POST'], detail=False, url_path='upload')
    def upload_image(self, request):
        """图片上传"""
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return Response(status=status.HTTP_201_CREATED, data={'success': 1, 'url': obj.image_url, 'id': obj.id})

    @action(methods=['DELETE'], detail=False, url_path='image/del')
    def del_image(self, request):
        id = request.data.get('id', None)
        obj = get_object_or_error(LifeRecordImage, err_msg='删除失败', id=id)
        obj.delete()
        return Response()
