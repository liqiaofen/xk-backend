from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import (
    BaseUserManager, PermissionsMixin, AbstractUser
)
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.const.choices import GenderChoice
from core.mixin.models import TimeStampedModel


class UserManager(BaseUserManager):

    def create_user(self, username, password=None, **kwargs):
        if username is None:
            raise TypeError('Users must have a username.')

        # if email is None:
        #     raise TypeError('Users must have an email address.')

        user = self.model(username=username, **kwargs)  # , email=self.normalize_email(email)

        password = password if password else self.make_random_password()
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, password, **kwargs):
        if password is None:
            raise TypeError('Superusers must have a password.')

        user = self.create_user(username, password=password, **kwargs)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractUser, TimeStampedModel):
    nickname = models.CharField(max_length=10)
    gender = models.CharField(verbose_name='性别', choices=GenderChoice.choices, max_length=2,
                              default=GenderChoice.GENDER_MALE)
    avatar = models.ImageField(upload_to="avatars", default="avatars/default.png",
                               max_length=100, null=True, blank=True)

    lover = models.ForeignKey('self', verbose_name='爱人', on_delete=models.CASCADE, null=True, blank=True)

    # @hook(AFTER_UPDATE, when='avatar', has_changed=True)
    # def on_avatar_change(self):
    #     # 头像信息更改后，清除缓存
    #     print('# 头像信息更改后，清除缓存')
    #     UserProfileCache().delete(self.id)

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created']

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        token = RefreshToken.for_user(self)
        return str(token.access_token)

    @staticmethod
    def validate_username(username):
        return User.objects.filter(username=username).exists()

    @property
    def avatar_url(self):
        if self.avatar.url.startswith('http'):
            return self.avatar.url
        return settings.BASE_URL + self.avatar.url
