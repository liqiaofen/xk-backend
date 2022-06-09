# Generated by Django 3.2 on 2022-05-30 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(0, '草稿'), (1, '已发布'), (2, '共享')], default=0, verbose_name='状态'),
        ),
    ]
