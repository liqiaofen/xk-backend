from django.urls import path

from album.views import AlbumView, PictureView

app_name = 'album'

urlpatterns = [
    path('', AlbumView.as_view(), name='album'),
    path('pictures/', PictureView.as_view(), name='album-picture'),
]
