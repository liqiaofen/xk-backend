# xk-backend

#### 初始化数据

```shell
# 数据初始化
python manage.py initdata
```

- -i init_expense # 指定某项初始化的数据
- -all # 执行全部的初始化数据
- -pro # 是否为生产

#### 1、重写serpy,提高 DRF中的序列化性能

> https://mp.weixin.qq.com/s/38RvBJLWoUgpME75fiuTyw

#### 2、Dynaconf 动态配置环境

> https://mp.weixin.qq.com/s/t_XmdCyPOGcdJenb571hdQ

```shell
poetry add dynaconf
```

#### 3、n+1 查询问题日志记录

> https://mp.weixin.qq.com/s/J9apIL6K1WRfwdXT5SlbUQ

```shell
poetry add nplusone
```

#### 4、S3储存

> https://mp.weixin.qq.com/s/T6u9c1TfnivZ9_HOsk3hYg

```shell
poetry add boto3 
poetry add django-storages
```

#### 5、非规范化数据库设计

> https://mp.weixin.qq.com/s/0mbNcN8EVykxXg9Rlf_JGw

```shell
poetry add django-denorm-iplweb
```

```python
from denorm import CountField
from django.db import models


class Album(models.Model):
    picture_count = CountField('picture_set')
```

执行`python manage.py flush`命令时会出现`触发器已经存在`错误。可能是同时导入`django-denorm-iplweb`和`django-denorm`
导致的，我们只需要使用`django-denorm-iplweb`

> 解决方法: DELETE FROM pg_trigger WHERE tgname like 'denorm_after_row_%';

#### 6、导入支付宝、微信账单

使用工厂方法优化账单导入
> https://mp.weixin.qq.com/s/zDTYyye9XE1HSQ-qx9Mspw

```shell
import bill_import

from inspect import getmembers, isclass, isabstract

def _create_class_map():
    class_list = []

    concrete_classes = getmembers(bill_import, lambda m: isclass(m)
                                                         and not isabstract(m)
                                                         and issubclass(m, bill_import.BillCsvImport))

    for class_name, concrete_class in concrete_classes:
        class_list.append(dict(class_name=class_name, concrete_class=concrete_class))

    return class_list
```

#### 7、付宝、微信账单导入时批量创建

> https://mp.weixin.qq.com/s/4uYmg1FAT-n3ptrvGXJH9Q

```python
class BulkCreateListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = super(BulkCreateListSerializer, self).create(validated_data)
        try:
            self.child.Meta.model.objects.bulk_create(result)
        except IntegrityError as e:
            raise ValidationError(e)
        # 批量创建后的操作
        return result


class ExpenseImportSerializer(serializers.ModelSerializer):
    ...

    def create(self, validated_data):
        instance = Expense(**validated_data)
        if isinstance(self._kwargs['data'], dict):  # 字典为单个创建， 批量创建为list
            instance.save()
        return instance

    class Meta:
        ...
        list_serializer_class = BulkCreateListSerializer
```

#### 8、Pytest

```shell
poetry add pytest
poetry add pytest-django
```

#### 9、文件夹列表： 在数据库中存储层级结构

```shell
poetry add django-mptt
```

> https://www.sitepoint.com/author/gijs-van-tulder/

#### 10、测试

```python

import cProfile

print(cProfile.run('for i in range(8000): MemoRestSerializer(objs)', sort='tottime'))
print(cProfile.run('for i in range(8000): MemoSerializer(objs)', sort='tottime'))

```

#### 11、django-lifecycle

```python
from django_lifecycle import hook, AFTER_UPDATE


@hook(AFTER_UPDATE, when='avatar', has_changed=True)
def on_avatar_change(self):
    # 头像信息等更改后，清除缓存
    UserProfileCache().delete(self.id)
```

#### 12、Docker

```shell

docker-compose up -d --build
docker-compose logs -f
docker-compose exec service_name python manage.py migrate --noinput # 运行迁移
docker-compose -f docker-compose-staging.yaml restart nginx-proxy
docker-compose -f docker-compose-staging.yaml logs -f nginx-proxy

```

查看数据库表

```shell
docker-compose exec db psql --username=postgres --dbname=xueke
# 查看数据库
xueke=# \l  
# 查看连接
xueke=# \c 
You are now connected to database "xueke" as user "postgres".
# 查看所有的数据表
xueke=# \dt
# 退出数据库
xueke=# \q
```

检查数据卷是否创建

```shell
docker volume ls

docker volume inspect xk-backend_postgres_data

```

#### entrypoint.sh 脚本

```shell
需要提前在本地更新文件权限
chmod +x app/entrypoint.sh

```


