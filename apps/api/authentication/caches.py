from api.authentication.serializers import UserInfoSerializer
from core.caches.model_cache import ModelCacheBase


class UserProfileCache(ModelCacheBase):
    serializer_class = UserInfoSerializer
    key_prefix = 'user'
