from django.urls import path, include
from rest_framework_nested import routers

from api.memo.views import MemoApiViewSet

app_name = 'api-memos'

router = routers.SimpleRouter()

router.register('', MemoApiViewSet, basename="memo")

urlpatterns = [
    path('', include(router.urls)),
]
