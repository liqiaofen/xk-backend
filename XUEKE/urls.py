"""XUEKE URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from XUEKE.views import PersonalView, WriteView, BackendIndexView
from api.authentication.views import RYTDTokenObtainPairView
from articles.views import ArticleFrontListView
from authentication.views import LoginView, SignUpView, BackendLoginView

api_patterns = [
    path('login/', RYTDTokenObtainPairView.as_view(), name='api-login'),
    path('albums/', include('api.album.urls', namespace='api-albums')),
    path('articles/', include('api.articles.urls', namespace='api-articles')),
    path('expenses/', include('api.expense.urls', namespace='api-expense')),
    path('timelines/', include('api.timeline.urls', namespace='api-timeline')),
    path('users/', include('api.authentication.urls', namespace='api-users')),
    path('memos/', include('api.memo.urls', namespace='api-memos')),

]
backend_patterns = [
    path('', BackendIndexView.as_view(), name='backend-index'),
    path('login/', BackendLoginView.as_view(), name='backend-login'),
    path('expenses/', include('expense.urls', namespace='expense')),
    path('albums/', include('album.urls', namespace='album')),
    path('articles/', include('articles.urls.back', namespace='article')),
]

frontend_patterns = [
    path('', ArticleFrontListView.as_view(), name='home'),
    path('articles/', include('articles.urls.front', namespace='front-article')),
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('account/', PersonalView.as_view(), name='personal'),
    path('write/', WriteView.as_view(), name='write'),
    path('write/', WriteView.as_view(), name='write'),
]
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
    path('backend/', include(backend_patterns)),
    path('', include(frontend_patterns)),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
