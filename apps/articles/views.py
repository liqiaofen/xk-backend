from datetime import timedelta

from django.db.models import When, Case, BooleanField
from django.utils import timezone
from django.views.generic import DetailView
from django_filters.views import FilterView

from api.articles.flters import ArticleFilter
from articles.models import Article, Folder, Tag
from utils.paginator import PaginationMixin, LoverViewMixin


class ArticleListView(PaginationMixin, LoverViewMixin, FilterView):
    model = Article
    context_object_name = "articles"
    template_name = "backend/article/index.html"
    filterset_class = ArticleFilter

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['current_path'] = self.request.GET.get('path', None)
        # 当前路径
        kwargs['nodes'] = Folder.objects.all().annotate(
            current_path=Case(When(path=kwargs['current_path'], then=True), default=False,
                              output_field=BooleanField()))
        return super(ArticleListView, self).get_context_data(object_list=None, **kwargs)


class ArticleDetailView(DetailView):
    model = Article
    context_object_name = "article"
    template_name = "backend/article/detail.html"


class ArticleSideContextData:
    def get_context_data(self, **kwargs):
        kwargs['tags'] = Tag.get_tags_cloud()
        kwargs['recents'] = Article.objects.filter(created__date__gte=(timezone.now() - timedelta(days=7)))[:5]
        return super(ArticleSideContextData, self).get_context_data(**kwargs)

    def get_queryset(self):
        """已发布的文章"""
        queryset = super(ArticleSideContextData, self).get_queryset()
        return queryset.publish()


class ArticleFrontListView(ArticleSideContextData, PaginationMixin, FilterView):
    model = Article
    context_object_name = "articles"
    template_name = "frontend/article/index.html"
    filterset_class = ArticleFilter


class ArticleFrontDetailView(ArticleSideContextData, DetailView):
    model = Article
    context_object_name = "article"
    template_name = "frontend/article/detail.html"
