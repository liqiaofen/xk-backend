from django.db.models.query import QuerySet
from core.caches.cache_base import CacheBase


class ModelCacheBase(CacheBase):
    serializer_class = None

    def __init__(self) -> None:
        super(ModelCacheBase, self).__init__()

    def get_from_db(self, key, *args, **kwargs):
        raise NotImplementedError('get_from_db is not implemented.')

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer(self, data):
        serializer_class = self.get_serializer_class()
        if serializer_class is None:
            raise TypeError(
                f"{self.__class__.__name__} should either include a 'serializer_class' attribute, or override the 'get_serializer_class()' method."
            )
        if isinstance(data, QuerySet) or isinstance(data, list):
            return serializer_class(data, many=True)
        return serializer_class(data)

    def serialize(self, data):
        ser = self.get_serializer(data)
        return ser.data

    def to_cache_representation(self, obj):
        return obj

    def get(self, key, force_db=False, *args, **kwargs):
        if force_db:
            data = None
        else:
            data = self.cache_get(key)

        if data is None:
            data = self.get_from_db(key, *args, **kwargs)
            if data is None:
                return None
            data = self.serialize(data)
            self.cache_set(key, data)
        return self.to_cache_representation(data)
