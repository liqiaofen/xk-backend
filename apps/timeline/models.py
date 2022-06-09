import random

from django.db import models

from core.mixin.models import TimeStampedModel, BaseQuerySet
from utils.uploads import FilePathAndRename


class TimeLineManager(models.Manager):
    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db)


class TimeLine(TimeStampedModel):
    content = models.TextField()
    exact_date = models.DateField(verbose_name='具体日期')
    icon = models.CharField(max_length=20, blank=True)
    color = models.CharField(max_length=20, blank=True)
    addr = models.JSONField(verbose_name='消费地址')
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='created_by')
    objects = TimeLineManager()

    class Meta:
        verbose_name = "时间轴"
        verbose_name_plural = verbose_name
        ordering = ['-created']


class LifeRecordImage(TimeStampedModel):
    image = models.ImageField(upload_to=FilePathAndRename('liferecord'))

    class Meta:
        verbose_name = "生活记录图片"
        verbose_name_plural = verbose_name
        ordering = ['-created']

    @property
    def image_url(self):
        if self.image.url.startswith('/media'):
            return f'https://picsum.photos/seed/{random.randint(0, 99)}/160/320'
        return self.image.url

    def delete(self, using=None, keep_parents=False):
        self.image.delete()
        super(LifeRecordImage, self).delete(using=using, keep_parents=keep_parents)


class LifeRecord(TimeStampedModel):
    content = models.CharField(max_length=500, blank=True)
    images = models.ManyToManyField(LifeRecordImage, blank=True)
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE)

    class Meta:
        verbose_name = "生活记录"
        verbose_name_plural = verbose_name
        ordering = ['-created']
