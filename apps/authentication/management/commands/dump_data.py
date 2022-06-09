import os
from pathlib import Path

from django.core import management
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = '导出指定数据库数据'

    def handle(self, *args, **options):
        BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
        dump_path = os.path.join(BASE_DIR, 'media/dump.json')
        management.call_command('dumpdata', natural_foreign=True, output=dump_path)
