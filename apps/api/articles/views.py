from django.contrib.auth import get_user_model
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.articles.serializers import FolderListSerializer, FolderCreateSerializer, ArticleCreateSerializer, \
    ArticleListSerializer, ArticleUpdateSerializer, ArticleImageUploadSerializer, ArticleDetailSerializer
from articles.models import Folder, Article
from core.mixin.views import LoverAPIViewMixin

User = get_user_model()


class ArticleApiViewSet(LoverAPIViewMixin, mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    queryset = Article.objects.filter()

    def get_queryset(self):
        queryset = super(ArticleApiViewSet, self).get_queryset()
        if self.action == 'list':
            return queryset.publish()
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return ArticleCreateSerializer
        elif self.action == 'partial_update':  # 更新
            return ArticleUpdateSerializer
        elif self.action == 'upload_image':
            return ArticleImageUploadSerializer
        elif self.action == 'retrieve':
            return ArticleDetailSerializer
        return ArticleListSerializer

    @action(methods=['POST'], detail=False, url_path='upload', permission_classes=[])
    def upload_image(self, request):
        """markdown 图片上传"""
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        obj = ser.save()
        return Response(data={'success': 1, 'url': obj.file.url})

    @action(methods=['PATCH'], detail=True, url_path='status')
    def change_status(self, request, pk):
        # 改变状态
        status = request.data.get('status', None)
        self.get_object().change_status(status)
        return Response()


class FolderApiViewSet(mixins.CreateModelMixin,
                       mixins.DestroyModelMixin,
                       GenericViewSet):
    queryset = Folder.objects.filter()

    def get_serializer_class(self):
        if self.action == 'create':
            return FolderCreateSerializer
        return FolderListSerializer
