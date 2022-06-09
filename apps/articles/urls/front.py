from django.urls import path

from articles.views import ArticleFrontDetailView

app_name = 'front-articles'

urlpatterns = [
    # path('', ArticleListView.as_view(), name='article'),
    path('<pk>/', ArticleFrontDetailView.as_view(), name='article-detail'),
]
