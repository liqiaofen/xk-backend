from abc import ABC

import pandas as pd

from api.expense.serializers import ExpenseImportSerializer
from api.timeline.serializers import TimeLineImportSerializer
from expense.choices import PayType
from expense.models import PayCategory


class CsvImport(ABC):
    COLUMN_MAP = {}

    def __init__(self, file, **kwargs):
        self.file = file
        self.kwargs = kwargs
        self.columns = {}
        self.dtype = {}
        self.__format_columns(self.COLUMN_MAP)
        self.df = self.read_file(file)
        self._rename_columns(self.df)

    def read_file(self, file):
        """默认读取excel文件"""
        df = pd.read_excel(file)
        return df

    def _rename_columns(self, df):
        df.columns = df.columns.str.strip()  # 去除columns前后空格
        df.rename(columns=self.columns, inplace=True)  # 索引重命名

    def __format_columns(self, column_map):
        """定义上传字段类型"""
        for k, v in column_map.items():
            if isinstance(v, tuple):
                self.columns[k] = v[0]
                self.dtype[k] = v[1]
            else:
                self.columns[k] = v

    def save(self, **kwargs):
        pass


class TimeLine(CsvImport):
    COLUMN_MAP = {
        '具体日期': 'exact_date',
        '内容': 'content',
        '心情': 'color',
        '图标': 'icon',
        '地点': 'addr'
    }

    def data_treating(self):
        df = self.df
        df['exact_date'] = pd.to_datetime(df['exact_date']).dt.date
        return df

    def save(self, **kwargs):
        df = self.data_treating()
        ser = TimeLineImportSerializer(data=df.to_dict('records'), many=True)
        ser.is_valid(raise_exception=True)
        ser.save(created_by=kwargs['request'].user)


class BillCsvImport(CsvImport):

    def data_treating(self):
        """数据处理"""
        df = self.df
        # 删除包含nan的列，all全为nan才删除，any包含一个才删除， 大可不必， 直接通过指定列获取了
        df = df.dropna(axis=1, how='all')
        # 删除和修改数据
        self.drop_update_data(df)
        # 除前后空格
        # df.replace('\s+', '', regex=True, inplace=True)  # 对整个表去除空格, 不太好，去除了字符串之间的空格
        df = df.loc[:, self.columns.values()]  # 获取指定列数据,
        for column in df.columns:
            if df[column].dtype == 'object':  # 只对字符串执行
                # df[column].str.strip()
                df[column] = df[column].str.strip()

        # 替换pay_type，inplace=True 直接修改表中数据
        df['pay_type'].replace(regex={'支出': PayType.SPENDING, '收入': PayType.INCOME, r'^[^支收]': PayType.OTHER},
                               inplace=True)

        return df

    def drop_update_data(self, df):
        pass

    def save(self, **kwargs):
        bill_df = self.data_treating()
        for pay_type in PayType.values:
            df_label = bill_df[bill_df['pay_type'] == pay_type]
            data_list = df_label.to_dict('list')
            # 获取所有的分类
            categories = PayCategory.objects.not_exist_to_create(data_list['category_id'], pay_type=pay_type)
            # print(df_label.to_dict('records'))

            expense_ser = ExpenseImportSerializer(data=df_label.to_dict('records'), many=True,
                                                  context={'categories': dict(categories)})
            expense_ser.is_valid(raise_exception=True)
            expense_ser.save(created_by=kwargs['request'].user)


class AliPayBill(BillCsvImport):
    COLUMN_MAP = {
        '收/支': ('pay_type', str),
        '交易对方': 'addr',
        '商品说明': 'note',
        '收/付款方式': 'pay_way',
        '金额': ('amount', float),
        '交易分类': 'category_id',
        '交易时间': 'pay_date'
    }

    def read_file(self, file):
        df = pd.read_csv(file, header=1
                         # , encoding='gbk'
                         )  # header=1 指定表头
        return df

    def drop_update_data(self, df):
        super(AliPayBill, self).drop_update_data(df)
        df.dropna(subset=['商家订单号'], inplace=True)  # 删除商家订单号为空的数据
        # 去除交易关闭的行
        df.drop(df[(df['交易状态'] == '关闭交易') | (df['交易状态'] == '退款成功')].index, inplace=True)


class WeChatBill(BillCsvImport):
    COLUMN_MAP = {
        '收/支': 'pay_type',
        '交易对方': 'addr',
        '商品': 'note',
        '支付方式': 'pay_way',
        '金额(元)': 'amount',
        '交易类型': 'category_id',
        '交易时间': 'pay_date'
    }

    def read_file(self, file):
        df = pd.read_csv(file, header=16)
        return df

    def drop_update_data(self, df):
        super(WeChatBill, self).drop_update_data(df)
        df.dropna(subset=['商户单号'], inplace=True)  # 删除商家订单号为空的数据
        df['amount'] = df['amount'].replace(regex={r'[￥¥]': ''})  # ¥0.10
        # 分类设置 扫码付款、商户消费-> 生活消费；微信红包->红包
        df['category_id'].replace(regex={'商户消费': '生活消费', '扫二维码付款': '生活消费', r'.*红包.*': '红包'},
                                  inplace=True)
