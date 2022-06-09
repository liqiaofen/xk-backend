# Generated by Django 3.2 on 2022-05-27 22:39

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PayCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('icon', models.CharField(max_length=20, verbose_name='图标')),
                ('name', models.CharField(max_length=6, verbose_name='名称')),
                ('color', models.CharField(default='#333333', max_length=20, verbose_name='颜色')),
                ('sort', models.PositiveSmallIntegerField(verbose_name='排序')),
                ('pay_type', models.PositiveSmallIntegerField(choices=[(0, '支出'), (1, '收入'), (2, '其他')], default=0, verbose_name='类型')),
            ],
            options={
                'verbose_name': '消费类别',
                'verbose_name_plural': '消费类别',
                'ordering': ['pay_type', 'sort'],
                'unique_together': {('name', 'pay_type')},
            },
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('note', models.CharField(blank=True, max_length=200, verbose_name='备注')),
                ('addr', django.contrib.postgres.fields.jsonb.JSONField(verbose_name='消费地址')),
                ('pay_way', models.PositiveSmallIntegerField(choices=[(0, '微信'), (1, '花呗'), (2, '银行卡'), (3, '现金'), (4, '其他')], default=3, verbose_name='支付方式')),
                ('pay_type', models.PositiveSmallIntegerField(choices=[(0, '支出'), (1, '收入'), (2, '其他')], default=0, verbose_name='类型')),
                ('pay_date', models.DateField(verbose_name='支付日期')),
                ('pay_time', models.TimeField(verbose_name='支付时间')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=6, verbose_name='支付金额')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='expense.paycategory', verbose_name='交易分类')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '费用',
                'verbose_name_plural': '费用',
                'ordering': ['-pay_date'],
            },
        ),
    ]