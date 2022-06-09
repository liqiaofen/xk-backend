from django.urls import path, include
from rest_framework_nested import routers

from api.timeline.views import TimeLineApiViewSet, LifeRecordApiView

app_name = 'api-timeline'

router = routers.SimpleRouter()
router.register('liferecords', LifeRecordApiView, basename="liferecord")
router.register('', TimeLineApiViewSet, basename="timeline")

urlpatterns = [
    path('', include(router.urls)),
]
