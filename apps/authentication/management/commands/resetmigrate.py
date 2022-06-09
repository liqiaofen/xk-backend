import os
import re
from pathlib import Path

from django.conf import settings
from django.core import management
from django.db import connection


class Command(management.BaseCommand):
    help = '重置迁移文件'

    def __init__(self, *args, **kwargs):
        self.cursor = connection.cursor()
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **options):
        BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent.parent
        for app in settings.LOCAL_APPS:
            migrations_dir = os.path.join(BASE_DIR, f'{app}/migrations')
            if not os.path.exists(migrations_dir):
                continue
            # 删除当前文件中的迁移文件
            for file_name in os.listdir(migrations_dir):
                if re.match('^\d.*\.py$', file_name):
                    os.remove(os.path.join(migrations_dir, file_name))

        management.call_command('makemigrations')
        management.call_command('migrate')
