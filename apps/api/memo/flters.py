from django_filters import rest_framework as filters

from memo.models import Memo


class MemoFilter(filters.FilterSet):
    class Meta:
        model = Memo
        fields = ['type']
