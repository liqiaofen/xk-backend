from django.core.cache import cache, caches

DEFAULT_CACHE_ALIAS = 'default'


def _get_cache(cache_alias):
    if cache_alias == DEFAULT_CACHE_ALIAS:
        return cache
    return caches[cache_alias]


class CacheBase:
    cache_alias = DEFAULT_CACHE_ALIAS
    key_prefix = ''
    single_key = False
    expire_duration = 60 * 60 * 24

    @classmethod
    def _set_default_key_prefix(cls):
        if cls.key_prefix == '':
            cls.key_prefix = cls.__name__

    def __init__(self) -> None:
        self.cache = _get_cache(self.cache_alias)
        self._set_default_key_prefix()

    def _format_key(self, key):
        if self.single_key:
            return self.key_prefix
        elif isinstance(key, tuple) or isinstance(key, list):
            return f'{self.key_prefix}:{"-".join(str(k) for k in key)}'
        else:
            return f'{self.key_prefix}:{key}'

    def cache_get(self, key):
        key = self._format_key(key)
        data = self.cache.get(key)
        return data

    def cache_set(self, key, data, expire_duration=None):
        key = self._format_key(key)
        if data is None:
            self.delete(key)
        else:
            self.cache.set(key, data, expire_duration or self.expire_duration)

    def delete(self, key):
        key = self._format_key(key)
        self.cache.delete(key)

    def delete_many(self, *args):
        key_list = self._args_format_key_list(*args)
        self.cache.delete_many(key_list)

    def _args_format_key_list(self, *args):
        return [self._format_key(key) for key in args]

    def cache_get_many(self, *args):
        if self.single_key:
            return self.get(*args)
        else:
            key_list = self._args_format_key_list(*args)
            result = self.cache.get_many(key_list)
            missing = [key for key in args if self._format_key(
                key) not in result]
            return result, missing

    def add(self, key, value):
        # key = self._format_key(key)  # TODO 我觉得这个应该放在下面
        if not self.get(key):
            key = self._format_key(key)
            self.set(key, value)

    def delete_pattern(self, pattern):
        self.cache.delete_pattern(pattern)

    def delete_all(self):
        pattern = self._format_key('*')
        return self.delete_pattern(pattern)

    def incr(self, key, delta):
        key = self._format_key(key)
        self.cache.incr(key, delta)

    def decr(self, key, delta):
        key = self._format_key(key)
        self.cache.incr(key, delta)


class SimpleGetCache(CacheBase):
    def get(self, key=None, force_db=False, *args, **kwargs):
        data = None
        if force_db:
            data = None
        else:
            data = self.cache_get(key)
        return data
