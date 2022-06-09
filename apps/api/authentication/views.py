import os

import shortuuid
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView

from api.authentication.caches import UserProfileCache
from api.authentication.serializers import UserTokenObtainPairSerializer, UserInfoSerializer
from core.utils import get_object_or_error

redis_conn = get_redis_connection()
User = get_user_model()


class RYTDTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        # 缓存用户信息
        UserProfileCache().cache_set(serializer.user.id, data=serializer.validated_data['userinfo'])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserViewSet(GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserInfoSerializer

    @action(detail=False)
    def info(self, request):
        return Response(data=self.get_serializer(self.request.user).data)

    @action(methods=['POST'], detail=False)
    def avatar(self, request):

        avatar_file = request.data.get('image', None)
        if not avatar_file:
            raise ValidationError('未上传任何文件')
        suffix = os.path.splitext(avatar_file.name)[1]
        if not suffix or suffix.lower() not in ['.jpeg', '.png', '.jpg']:
            raise ValidationError("错误的文件格式")

        file_size = avatar_file.size
        limit_mb = 1
        if file_size > limit_mb * 1024 * 1024:
            raise ValidationError(f"头像文件最大是{limit_mb}MB")
        file_name = f'{shortuuid.uuid()}{suffix}'
        avatar = request.user.avatar
        old_avatar = avatar.name
        avatar.save(file_name, ContentFile(avatar_file.read()))
        # 创建成功后删除之前的头像
        if old_avatar != 'avatars/default.png':
            default_storage.delete(old_avatar)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def pairing(self, request):
        # https://www.codeleading.com/article/63042756042/
        # https://testdriven.io/blog/django-low-level-cache/
        # https://rsinger86.github.io/django-lifecycle/
        # https://www.dabapps.com/blog/
        """发起配对"""
        if self.request.user.lover_id:
            raise ValidationError('接触配对后，才能重新发送配对！')
        lover_name = request.data.get('lover')
        lover = get_object_or_error(User, err_msg='当前用户还未注册', username=lover_name)
        redis_conn.sadd(f'lover:{lover.id}', self.request.user.id)  # 添加到请求者id集合(Set)中
        return Response(data='已经成功发送配对请求,正在等待对方的回应')

    @action(detail=False)
    def pairings(self, request):
        """配对列表"""
        # if self.request.user.lover_id:
        #     return Response(data=[])
        ids = [user_id.decode() for user_id in redis_conn.smembers(f'lover:{self.request.user.id}')]
        # 先查询缓存
        result, missing = UserProfileCache().cache_get_many(*ids)
        missing_result = UserInfoSerializer(instance=User.objects.filter(id__in=missing), many=True).data
        missing_result.extend(result.values())
        return Response(data=missing_result)

    @action(detail=False, url_path='accept/pairing', methods=['POST'])
    def accept_pairing(self, request):
        """同意配对"""
        if self.request.user.lover_id:
            raise ValidationError('你已经存在配对。')
        lover_id = request.data.get('lover', None)
        lover = get_object_or_error(User, err_msg='未找到配对人信息', id=lover_id)
        user = self.request.user
        user.lover = lover
        user.save()
        lover.lover = user
        lover.save()
        redis_conn.srem(f'lover:{user.id}', str(lover_id))  # 从请求者id集合(Set)中移除
        return Response(data='配对成功')

    @action(detail=False, url_path='remove/pairing', methods=['POST'])
    def remove_pairing(self, request):
        """解除配对"""
        if self.request.user.lover_id is None:
            raise ValidationError('解除错误。')
        user = self.request.user
        lover = user.lover
        user.lover = None
        user.save()
        lover.lover = None
        lover.save()
        return Response(data='解除成功')
