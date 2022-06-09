from rest_framework import serializers

from core import serpy
from core.mixin.serializers import QuerySerializerMixin
from memo.models import Memo


class MemoType(serpy.Serializer):
    icon = serpy.StrField()
    color = serpy.StrField()
    name = serpy.StrField()


class MemoSerializer(QuerySerializerMixin, serpy.Serializer):
    id = serpy.IntField()
    title = serpy.StrField()
    content = serpy.StrField()
    type = serpy.MethodField()
    created_by = serpy.StrField()

    def get_type(self, obj):
        return MemoType(obj.type).data


class MemoCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Memo
        fields = ['title', 'content', 'type', 'created_by']
