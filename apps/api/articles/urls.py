from django.urls import path, include
from rest_framework_nested import routers

from api.articles.views import FolderApiViewSet, ArticleApiViewSet

app_name = 'api-articles'

article_router = routers.SimpleRouter()
article_router.register('folders', FolderApiViewSet, basename="article-folder")
article_router.register('', ArticleApiViewSet, basename="article")

urlpatterns = [
    path('', include(article_router.urls)),
]
