from django.db import models
from django.db.models import Func, F, Value, CharField


class BaseQuerySet(models.QuerySet):

    def annotate_fmt_datetime(self, field, fmt='YYYY-MM'):
        # 格式化时间，便于日期、时间分组统计
        return self.annotate(
            year_month=Func(F(field), Value(fmt), function='to_char',
                            output_field=CharField()))


class TimeStampedModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        重写保存方法，以确保修改的字段将被更新，即使它没有被给出更新字段参数的参数。
        """
        update_fields = kwargs.get('update_fields', None)
        if update_fields:
            kwargs['update_fields'] = set(update_fields).union({'modified'})
        super(TimeStampedModel, self).save(*args, **kwargs)
