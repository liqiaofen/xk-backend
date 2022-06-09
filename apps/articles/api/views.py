from rest_framework import mixins, viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from articles.models import Article
from articles.renderers import ArticleJSONRenderer
from articles.serializers import ArticleSerializer


class ArticleViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    lookup_field = 'slug'
    queryset = Article.objects.select_related('created_by', 'created_by__user')
    renderer_classes = (ArticleJSONRenderer,)
    serializer_class = ArticleSerializer

    def create(self, request, *args, **kwargs):
        serializer_context = {
            'created_by': request.user.profile,
            'request': request
        }
        serializer_data = request.data.get('article', {})

        serializer = self.serializer_class(
            data=serializer_data, context=serializer_context
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        serializer_context = {'request': request}
        page = self.paginate_queryset(self.get_queryset())

        serializer = self.serializer_class(
            page,
            context=serializer_context,
            many=True
        )

        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer_context = {'request': request}

        try:
            serializer_instance = self.queryset.get(slug=kwargs['slug'])
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        serializer = self.serializer_class(
            serializer_instance,
            context=serializer_context
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, slug):
        serializer_context = {'request': request}

        try:
            serializer_instance = self.queryset.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound('An article with this slug does not exist.')

        serializer_data = request.data.get('article', {})

        serializer = self.serializer_class(
            serializer_instance,
            context=serializer_context,
            data=serializer_data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
