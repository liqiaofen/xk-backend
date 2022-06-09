import string
import random
from datetime import datetime, timedelta

from django.shortcuts import _get_queryset
from rest_framework.exceptions import ValidationError


def get_object_or_error(klass, err_msg=None, *args, **kwargs):
    queryset = _get_queryset(klass)
    if not hasattr(queryset, 'get'):
        klass__name = klass.__name__ if isinstance(
            klass, type) else klass.__class__.__name__
        raise ValueError(
            "First argument to get_object_or_404() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        err_msg = err_msg if err_msg else 'No %s matches the given query.' % queryset.model._meta.object_name
        raise ValidationError(err_msg)


def get_date_range(start, end, fmt='%Y-%m-%d'):
    # 获取时间范围
    if not isinstance(start, datetime):
        start = datetime.strptime(start, fmt)

    if not isinstance(end, datetime):
        end = datetime.strptime(end, fmt)

    for n in range(int((end - start).days)):
        yield (start + timedelta(n)).strftime(fmt)


"""
 def to_representation(self, obj):
        representation = super().to_representation(obj)
        user_representation = representation.pop("user")
        for key in user_representation:
            representation[key] = user_representation[key]

        representation = convert_empty_string_to_none(representation)
        return representation
"""


def convert_empty_string_to_none(representation: dict) -> dict:
    """转换空字符串为None"""

    def converter(i):
        if isinstance(i, str):
            return i or None
        return i

    for key, value in representation.items():
        representation[key] = converter(value)

    return representation


def create_random_string(max_length, letters=string.ascii_letters):
    """创建随机长度的字符串"""
    return ''.join(random.choice(letters) for i in range(random.randint(1, max_length)))
