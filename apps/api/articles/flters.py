from django_filters import rest_framework as filters

from album.models import Picture
from articles.models import Article, Tag


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


class ArticleFilter(filters.FilterSet):
    path = filters.CharFilter(field_name='folder__path')
    tag = filters.ModelMultipleChoiceFilter(field_name='tags__name',
                                            to_field_name='name',
                                            queryset=Tag.objects.all())

    class Meta:
        model = Article
        fields = ['path']
