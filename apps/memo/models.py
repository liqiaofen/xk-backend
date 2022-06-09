from django.db import models

from core.mixin.models import TimeStampedModel


class MemoType(TimeStampedModel):
    icon = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=20)
    name = models.CharField(max_length=10)
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "备忘录类型"
        verbose_name_plural = verbose_name
        ordering = ['-created']


class Memo(TimeStampedModel):
    title = models.CharField(verbose_name='', max_length=100, blank=True)
    content = models.TextField()
    type = models.ForeignKey(MemoType, on_delete=models.CASCADE)
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE)

    # TODO 这里可以使用非规范化的包，如果类型删除，将对应备忘录类型修改默认类型

    class Meta:
        verbose_name = "备忘录"
        verbose_name_plural = verbose_name
        ordering = ['-created']
