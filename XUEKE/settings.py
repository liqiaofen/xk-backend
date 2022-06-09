"""
Django settings for XUEKE project.

Generated by 'django-admin startproject' using Django 4.0.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
import os
import sys
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

DEBUG = False

# Auth配置
AUTH_USER_MODEL = 'authentication.User'

LOCAL_APPS = [
    'album',
    'articles',
    'authentication',
    'expense',
    'memo',
    # 'practice',  # 测试，无意义
    'system',
    'timeline'
]

INSTALLED_APPS = [
                     # 'django.contrib.admin',
                     'django.contrib.auth',
                     'django.contrib.contenttypes',
                     'django.contrib.sessions',
                     'django.contrib.messages',
                     'django.contrib.staticfiles',
                     'corsheaders',
                     'rest_framework',
                     'django_filters',
                     'gunicorn',
                     'django_extensions',
                     # 'mdeditor',
                     'denorm',  # 非规范化数据库字段
                     'nplusone.ext.django',
                     # 'storages',
                     'mptt'
                 ] + LOCAL_APPS

MIDDLEWARE = [
    'core.custom_nplusone.middleware.CustomerNPlusOneMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'denorm.middleware.DenormMiddleware'
    'core.drf.middleware.BackendRbacMiddleware'
]

VALID_URL_LIST = ['/backend/login/']  # 后端地址白名单

ROOT_URLCONF = 'XUEKE.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'XUEKE.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # 身份信息认证
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',  # 启用这个后，可以浏览器登录，上线后可考虑关闭
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # 需要用户登录
        'core.drf.permissions.RbacPermission'  # 权限认证
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',  # django_filters
    ),
    'DEFAULT_RENDERER_CLASSES': [
        # 'rest_framework.renderers.JSONRenderer',  # 返回json格式
        'core.drf.renderers.FitJSONRenderer',  # 这个自定义渲染器，为回文增加了code和msg
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    # 自定义异常
    'EXCEPTION_HANDLER': 'core.drf.exception_handler.custom_exception_handler',
    'DEFAULT_PAGINATION_CLASS': 'core.drf.renderers.CommonPagination',
    'PAGE_SIZE': 10
}

# SimpleJWT配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    # 'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
}
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# django-pure-pagination 后端分页设置
PAGINATION_SETTINGS = {
    'PAGE_RANGE_DISPLAYED': 2,  # 分页条当前页前后应该显示的总页数（两边均匀分布，因此要设置为偶数），
    'MARGIN_PAGES_DISPLAYED': 3,  # 分页条开头和结尾显示的页数
    'SHOW_FIRST_PAGE_WHEN_INVALID': True,  # 当请求了不存在页，显示第一页
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "@format redis://{this.REDIS_HOST}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                'max_connections': 1000,
                'encoding': 'utf-8'
            }
        }
    }
}

# https://www.cnblogs.com/chenxuming/articles/9529128.html
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'nplusone': {  # n+1 问题
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/nplusone.log',
            'maxBytes': 1024 * 1024 * 10,  # 日志大小 10M
            'backupCount': 2,  # 备份数为 2
            'formatter': 'simple'
        },
        'request_err': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/request_err.log',
            'maxBytes': 1024 * 1024 * 10,  # 日志大小 10M
            'backupCount': 2,  # 备份数为 2
            'formatter': 'simple',
            'encoding': 'utf-8',
        }
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'level': 'ERROR',
            'propagate': False,
        },
        'nplusone': {
            'handlers': ['nplusone'],
            'level': 'DEBUG',
        },
        'request_err': {
            'handlers': ['request_err'],
            'level': 'ERROR',
        }
    }
}

import dynaconf  # noqa

settings = dynaconf.DjangoDynaconf(__name__)  # noqa