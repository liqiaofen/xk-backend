# 独立使用django的model
import os
import sys

# 获取当前文件的路径
# os.path.realpath(__file__) 获取当前执行脚本的绝对路径。
# os.path.dirname() 获取当前脚本所在的文件夹名称


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 找到项目文件
sys.path.extend([BASE_DIR, ])

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "XUEKE.settings")

import django

django.setup()
from api.expense.excel import AliPayBill
from api.expense.const.maps import ALIPAY_RECORD_MAP
from expense.models import PayType, PayCategory
from api.expense.serializers import ExpenseImportSerializer

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # 获取当前路径
xlsx_path = os.path.join(BASE_DIR, 'wechat.csv')  # 必须得用BASE_DIR，否则运行init_data的时候会报错

wb = AliPayBill(xlsx_path, ALIPAY_RECORD_MAP)

print(wb.df.to_dict('records'))
# 筛选 支出
for value, label in PayType.choices:
    df = wb.df[wb.df['pay_type'] == label]
    data = df.to_dict('list')
    category_names = set(data['category_id'])
    exist = set(PayCategory.objects.filter(name__in=category_names, pay_type=value).values_list('name', flat=True))
    not_exist = category_names - exist
    # 批量创建不存在的分类
    if not_exist:
        PayCategory.objects.bulk_create(
            [PayCategory(name=name, icon='', sort=1, pay_type=value) for name in not_exist])

    # 获取所有的分类
    categories = PayCategory.objects.filter(name__in=category_names, pay_type=value).values_list('name', 'id')

    ser = ExpenseImportSerializer(data=df.to_dict('records'), many=True, context={'categories': dict(categories)})
    ser.is_valid(raise_exception=True)
    # objs = ser.save(created_by_id=1)
    # print(objs)
    # Expense.objects.bulk_create(ser)
