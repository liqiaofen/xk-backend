from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Subquery
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from album.models import Album, Picture
from api.album.flters import PictureFilter
from api.album.serializers import AlbumCreateSerializer, AlbumListSerializer, PictureCreateSerializer, \
    PictureListSerializer, AlbumBaseSerializer
from core.mixin.views import BaseAPIViewMixin

User = get_user_model()


class AlbumApiViewSet(BaseAPIViewMixin, mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    queryset = Album.objects.filter()

    def get_serializer_class(self):
        if self.action == 'create':
            return AlbumCreateSerializer
        elif self.action == 'list':
            return AlbumListSerializer
        return AlbumBaseSerializer

    def get_queryset(self):
        queryset = super(AlbumApiViewSet, self).get_queryset()
        if self.action == 'list':
            # 使用子查询：查询每个相册最近的一张照片
            newest = Picture.objects.filter(album=OuterRef('pk')).order_by('-created').values('image')[:1]
            queryset.aggregate(newest=Subquery(newest))
        return queryset


class PictureApiViewSet(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    queryset = Picture.objects.filter()
    filterset_class = PictureFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return PictureCreateSerializer
        return PictureListSerializer

    @action(methods=['get'], detail=False, url_path='recent')
    def recent_pictures(self, request):
        # 首页显示最近六张图片
        queryset = self.queryset.order_by('-created')[:6]
        return Response(self.get_serializer(instance=queryset, many=True).data)
