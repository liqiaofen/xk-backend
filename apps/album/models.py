from denorm import CountField
from django.conf import settings
from django.db import models

from core.mixin.models import TimeStampedModel


class Album(TimeStampedModel):
    name = models.CharField(max_length=15, unique=True)
    index = models.PositiveSmallIntegerField(verbose_name='排序', default=0)
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE)
    picture_count = CountField('picture_set')

    class Meta:
        verbose_name = "相册"
        verbose_name_plural = verbose_name
        ordering = ['index', '-created']


class Picture(models.Model):
    # album_name = models.CharField(verbose_name='相册名称', max_length=15)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='album')
    created = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(
        'authentication.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.image.url

    class Meta:
        verbose_name = "图片"
        verbose_name_plural = verbose_name
        ordering = ['-created']

    def delete(self, using=None, keep_parents=False):
        self.image.delete()
        super(Picture, self).delete(using=using, keep_parents=keep_parents)

    @property
    def image_url(self):
        if self.image.url.startswith('http'):
            return self.image.url
        return settings.BASE_URL + self.image.url
