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
