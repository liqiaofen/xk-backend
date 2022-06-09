from django.core.management import BaseCommand

from django.utils import timezone
from django.utils.crypto import get_random_string

from authentication.models import User


class Command(BaseCommand):
    help = '创建随机用户'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int, help='表示要创建的用户数量')
        parser.add_argument('-p', '--predix', type=str, help='用户名前缀')
        parser.add_argument('-a', '--admin', action='store_true', help='创建admin用户')

    def handle(self, *args, **kwargs):
        total = kwargs['total']
        predix = kwargs['predix']
        admin = kwargs['admin']
        for i in range(total):
            if predix:
                username = f'{predix}_{get_random_string(length=5)}'
            else:
                username = get_random_string(length=5)

            if admin:
                User.objects.create_superuser(username=username, password='123')
            else:
                User.objects.create_user(username=username, password='123')
