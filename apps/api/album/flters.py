from django_filters import rest_framework as filters

from album.models import Picture


class PictureFilter(filters.FilterSet):
    album_name = filters.CharFilter(
        field_name='album__name', lookup_expr='icontains')

    sort = filters.OrderingFilter(
        fields=(
            ('created', 'created'),
        )
    )

    class Meta:
        model = Picture
        fields = ['album_name', 'sort']
