from django.urls import path, include
from rest_framework import routers

app_name = 'users'
router = routers.SimpleRouter()
# router.register('', UserViewSet, basename="users")
urlpatterns = [
    path('', include(router.urls)),
]
