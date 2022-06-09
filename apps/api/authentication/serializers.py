import re

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from authentication.models import User
from core import serpy


class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': '账号或密码错误'
    }

    def validate(self, attrs):
        REGEX_EMAIL = "^\\w+([-+.]\\w+)*@\\w+([-.]\\w+)*\\.\\w+([-.]\\w+)*$"
        if re.match(REGEX_EMAIL, attrs['username']):
            # 邮箱方式登录
            user = User.objects.filter(email=attrs['username']).values('username').first()
            if user:
                attrs['username'] = user['username']
        data = super().validate(attrs)
        data['access'] = self.user.token
        del data['refresh']
        data['userinfo'] = UserInfoSerializer(self.user).data
        return data


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_staff', 'is_active']


class LoverInfoSerializer(serpy.Serializer):
    nickname = serpy.StrField()
    id = serpy.StrField()
    avatar_url = serpy.StrField()


class UserInfoSerializer(LoverInfoSerializer):
    lover = serpy.MethodField()

    def get_lover(self, obj):
        if obj.lover is None:
            return None
        return LoverInfoSerializer(instance=obj.lover).data
