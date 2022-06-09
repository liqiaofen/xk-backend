from django.urls import path, include
from rest_framework_nested import routers

from api.album.views import PictureApiViewSet, AlbumApiViewSet

app_name = 'api-albums'

albums_router = routers.SimpleRouter()
albums_router.register('pictures', PictureApiViewSet, basename="album-picture")
albums_router.register('', AlbumApiViewSet, basename="album")

urlpatterns = [
    path('', include(albums_router.urls)),
]
