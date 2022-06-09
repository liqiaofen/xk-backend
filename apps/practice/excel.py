import os

import pandas as pd

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # 获取当前路径
xlsx_path = os.path.join(BASE_DIR, 'wechat.csv')  # 必须得用BASE_DIR，否则运行init_data的时候会报错

WECHAT_RECORD_MAP = {
    '收/支': 'pay_type',
    '交易对方': 'addr',
    '商品': 'note',
    '支付方式': 'pay_way',
    '金额(元)': 'amount',
    '交易类型': 'category_id',
    '交易时间': 'pay_date'
}

ALIPAY_RECORD_MAP = {
    '收/支': 'pay_type',
    '交易对方': 'addr',
    '商品说明': 'note',
    '收/付款方式': 'pay_way',
    '金额': 'amount',
    '交易分类': 'category_id',
    '交易时间': 'pay_date'
}

df = pd.read_csv(xlsx_path, header=16)  # header=1 指定表头

df.columns = df.columns.str.strip()  # 去除columns前后空格
# df = df.dropna(subset=['商家订单号'])

RECORD_MAP = WECHAT_RECORD_MAP
df = df.rename(columns=RECORD_MAP)

#

for column in df.columns:
    if df[column].dtype == 'object':
        df[column] = df[column].str.strip()

# df.drop(df[df['交易状态'] == '关闭交易'].index, inplace=True)
df = df.loc[:, RECORD_MAP.values()]  # 获取指定列数据

# df['pay_type'] = df['pay_type'].mask(df['pay_type'] == '收入', 0)
# df['pay_type'] = df['pay_type'].mask(df['pay_type'] == '支出', 1)
# df['pay_type'] = df['pay_type'].mask((df['pay_type'] != 0) & (df['pay_type'] != 1), 2)

# df['pay_type'].replace(['支出', '收入', '[]'], ['PayType.SPENDING', 'PayType.INCOME'], inplace=True)
df['pay_type'].replace(regex={'支出': '0', '收入': 1, r'^[^支收]': 2}, inplace=True)

# data为DataFrame格式
# df.replace('\s+', '', regex=True, inplace=True)  # 对真个表去除空格
# df = df[df['pay_type'] != nan]  # 筛选
# 或者
# a.replace('\s+','',regex=True,inplace=True) 对真个表去除空格
# print(df)

# mask = df['pay_type'] in '---------------------------------------------'
# pos = np.flatnonzero(mask)
print(df.category_id)
df['category_id'].replace(regex={'商户消费': '生活消费', '扫二维码付款': '生活消费', r'.*红包.*': '红包'},
                          inplace=True)
print(df.category_id)
# print(df.to_dict('records'))
