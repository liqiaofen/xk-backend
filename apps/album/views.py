from typing import Any, Dict

from django.views.generic import ListView

from album.models import Album, Picture
from utils.paginator import PaginationMixin


class AlbumView(PaginationMixin, ListView):
    model = Album
    context_object_name = "albums"
    template_name = "backend/album/album.html"


class PictureView(PaginationMixin, ListView):
    model = Picture
    context_object_name = "pictures"
    template_name = "backend/album/picture.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        print(context)
        return context
