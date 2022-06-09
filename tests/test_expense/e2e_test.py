import os
from pathlib import Path

from rest_framework import status

BASE_DIR = Path(__file__).resolve(strict=True).parent  # os.path.abspath(os.path.dirname(__file__))  # 获取当前路径
ROOT_DIR = BASE_DIR.parent.parent


class TestExpenseApiViewSet:

    def setup_class(self):
        self.url = '/api/expenses'

    def test_bill_import(self, admin_client):
        """测试账单导入"""
        file_path = os.path.join(ROOT_DIR, 'const/alipay_bill.csv')
        with open(file_path, 'rb') as fp:
            res = admin_client.post(self.url + '/bill/', {'method': 'alipay', 'file': fp})
        assert res.status_code == status.HTTP_200_OK, res.json()
