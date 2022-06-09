import smtplib

import pytest
from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APIClient

from authentication.management.common_initdata import init_user
from authentication.models import User


@pytest.fixture(scope='session', autouse=True)
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        # 清空redis缓存
        cache.clear()
        init_user()


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass  # 就不用写 @pytest.mark.django_db


@pytest.fixture(scope='session')
def user_admin(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        return User.objects.get(username='admin')


@pytest.fixture(scope='session')
def admin_token(django_db_blocker):
    with django_db_blocker.unblock():
        client = APIClient()
        res = client.post('/api/login/', data={'username': '2385512991@qq.com', 'password': 'admin'}, format='json')
        assert res.status_code == status.HTTP_200_OK, res.json()
        return res.json()['data']['access']


@pytest.fixture(scope='session')
def admin_client(admin_token):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    return client


# 官方例子
@pytest.fixture(scope="module")
def smtp_connection():
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=5) as smtp_connection:
        yield smtp_connection  # provide the fixture value


def test_users(admin_client):
    res = admin_client.get('/api/users/info/')
    print(res.json())
