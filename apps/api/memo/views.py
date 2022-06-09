from rest_framework.viewsets import ModelViewSet

from api.memo.flters import MemoFilter
from api.memo.serializers import MemoCreateSerializer, MemoSerializer
from memo.models import Memo


class MemoApiViewSet(ModelViewSet):
    queryset = Memo.objects.filter()
    filterset_class = MemoFilter

    def get_serializer_class(self):
        if self.action in ['create']:
            return MemoCreateSerializer
        return MemoSerializer
