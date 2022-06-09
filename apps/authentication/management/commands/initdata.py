import os
import random
from pathlib import Path

from django.core import management
from django.db import transaction
from faker import Faker
from model_bakery import baker

from album.models import Album
from articles.models import Folder, Article, Tag
from authentication.models import User
from core.file_import.import_factory import ImportFactory
from timeline.models import LifeRecord, LifeRecordImage

fake = Faker(['zh_CN'])
BASE_DIR = Path(__file__).resolve(strict=True).parent  # os.path.abspath(os.path.dirname(__file__))  # 获取当前路径
ROOT_DIR = BASE_DIR.parent.parent.parent.parent


class Command(management.BaseCommand):
    help = '清空数据库后，初始化数据'

    def add_arguments(self, parser):
        parser.add_argument('--init', '-i', action='append', default=[], help='初始化的功能列表')
        parser.add_argument('-pro', action='store_true', help='初始化环境是否为生产环境')
        parser.add_argument('-all', action='store_true', help='执行所有的初始化方法')

    def handle(self, *args, **kwargs):

        with transaction.atomic():
            # DELETE FROM pg_trigger WHERE tgname like 'denorm_after_row_%';    触发器已经存在
            management.call_command('flush', verbosity=0, interactive=False)

            admin = User.objects.create_superuser(username='2385512991@qq.com', password='admin', nickname='Qiaofinn')
            zhangsan = User.objects.create_user(username='zhangsan', password='zhangsan', nickname='张三')
            kwargs['admin'] = admin
            kwargs['zhangsan'] = zhangsan

            init = self.all_init_methods() if kwargs['all'] else kwargs['init']
            with transaction.atomic():
                for fun_name in init:
                    fun = getattr(self, fun_name)
                    fun(**kwargs)

            text = '生产环境数据初始化成功' if kwargs['pro'] else '开发环境数据初始化成功'
            self.stdout.write(self.style.SUCCESS(text))

    def all_init_methods(self):
        # 获取所有的初始化方法
        return list(filter(lambda m: m.startswith("init_") and callable(getattr(self, m)), dir(self)))

    def init_expense(self, **kwargs):
        # 消费, 开发环境才会执行
        if kwargs['pro']:
            return

        class Request:
            user = kwargs['admin']

        request = Request()

        factory = ImportFactory()
        alipay_bill = os.path.join(ROOT_DIR, 'const/alipay_bill.csv')
        factory.get_import('AliPayBill', alipay_bill).save(request=request)
        wechat_bill = os.path.join(ROOT_DIR, 'const/wechat_bill.csv')
        factory.get_import('WeChatBill', wechat_bill).save(request=request)

    def init_timeline(self, **kwargs):
        class Request:
            user = kwargs['admin']

        request = Request()
        factory = ImportFactory()
        alipay_bill = os.path.join(ROOT_DIR, 'const/timeline.xlsx')
        factory.get_import('TimeLine', alipay_bill).save(request=request)

        for i in range(50):
            images = []
            for j in range(random.choice([0, 2, 0, 5, 9])):
                images.append(LifeRecordImage(image=f'https://picsum.photos/seed/{i * j}/160/320'))
            images = LifeRecordImage.objects.bulk_create(images)
            obj = LifeRecord.objects.create(content=fake.paragraph(),
                                            created_by=random.choice([kwargs['admin'], kwargs['zhangsan']]))
            obj.images.add(*images)

    def init_album(self, **kwargs):
        # 相册
        for i in range(8):
            album = Album.objects.create(name=f'album-{i}', created_by=kwargs['admin'])
            num = 40 if i == 0 else 2
            for j in range(0, num):
                baker.make('album.Picture', image=f'album/{i}-{j}.jpg', album=album)

    def init_folder(self, **kwargs):
        folder = Folder.objects.create(name=f'一级目录')  # 根节点
        Folder.objects.create(name=f'二级目录-1', parent=folder)
        folder2 = Folder.objects.create(name=f'二级目录-2', parent=folder)  # 子节点
        Folder.objects.create(name=f'三级目录-2-1', parent=folder2)  # 子节点、叶子节点
        folder3 = Folder.objects.create(name=f'二级目录-3', parent=folder)

        tags = Tag.objects.bulk_create([Tag(name=name) for name in ['Django', 'Python', '设计模式', '数据结构']])

        for i in range(50):
            article = Article.objects.create(title=fake.sentence(), abstract=fake.paragraph(),
                                             content=fake.text(),
                                             created_by=random.choice([kwargs['admin'], kwargs['zhangsan']]),
                                             folder=folder3,
                                             cover=f'article/0-{i}.jpg',
                                             status=Article.Status.PUBLISHED)

            article.tags.add(*random.sample(tags, 2))
