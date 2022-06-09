from django.urls import path, include
from rest_framework import routers

from api.authentication.views import UserViewSet

app_name = 'api-users'
router = routers.SimpleRouter()
router.register('', UserViewSet, basename='users')
urlpatterns = [
    path('', include(router.urls)),
]
