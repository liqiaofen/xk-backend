from django.conf import settings
from django.db import models
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from django_lifecycle import LifecycleModelMixin, hook, AFTER_UPDATE, BEFORE_UPDATE
from mptt.models import MPTTModel
from rest_framework.exceptions import ValidationError

from core.mixin.models import TimeStampedModel, BaseQuerySet
# 参考：https://django-mptt.readthedocs.io/en/latest/tutorial.html
from utils.uploads import FilePathAndRename


class Folder(MPTTModel, TimeStampedModel):
    name = models.CharField(max_length=10, )
    path = models.CharField(verbose_name='路径', max_length=100, blank=True, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['lft']

    def save(self, *args, **kwargs):
        if not self.path:
            if self.parent:
                parent_path = '/'.join(
                    self.parent.get_ancestors(ascending=False, include_self=True).values_list('name', flat=True))
                self.path = f'{parent_path}/{self.name}'
            else:
                self.path = self.name
        super(Folder, self).save(**kwargs)


class ArticleImage(TimeStampedModel):
    file = models.ImageField(upload_to=FilePathAndRename('article'))

    class Meta:
        verbose_name = _("文章图片")
        verbose_name_plural = verbose_name
        ordering = ['-created']


class Tag(TimeStampedModel):
    name = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = "标签"
        verbose_name_plural = verbose_name
        ordering = ['-created']

    @staticmethod
    def get_tags_cloud(font_size=1.2):
        """计算标签云"""
        tags = Tag.objects.filter().annotate(article_count=Count('article')).filter(article_count__gt=0).order_by(
            '-article_count').values('name', 'article_count')
        ratio = font_size / tags[0]['article_count']
        for tag in tags:
            tag['size'] = tag['article_count'] * ratio
        return tags


class ArticleQuerySet(BaseQuerySet):

    def publish(self):
        return self.filter(status__in=[Article.Status.PUBLISHED, Article.Status.SHARED])

    def draft(self):
        return self.filter(status=Article.Status.DRAFT)


class ArticleManager(models.Manager):

    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)


class Article(LifecycleModelMixin, TimeStampedModel):
    class Status(models.IntegerChoices):
        DRAFT = 0, '草稿'
        PUBLISHED = 1, '已发布'
        SHARED = 2, '共享'

    # slug = models.SlugField(db_index=True, max_length=255, unique=True)
    title = models.CharField(db_index=True, max_length=50)
    abstract = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey('authentication.User', on_delete=models.CASCADE, related_name='articles')
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=Status.choices, default=Status.DRAFT)
    folder = models.ForeignKey(Folder, verbose_name='目录', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)
    cover = models.ImageField(upload_to=FilePathAndRename('article'))
    objects = ArticleManager()

    @hook(BEFORE_UPDATE, when='contents', has_changed=True)
    def on_content_change(self):
        print('on_content_change')
        # do something

    @hook(AFTER_UPDATE, when="status", was="draft", is_now="published")
    def on_publish(self):
        print('on_publish')
        # send_email(self.editor.email, "An article has published!")

    @property
    def cover_url(self):
        if self.cover:
            if self.cover.url.startswith('http'):
                return self.cover.url
            return settings.BASE_URL + self.cover.url
        return ''

    def tag_names(self):
        return self.tags.all().values_list('name', flat=True)

    def tags_name_str(self):
        return ' '.join(self.tag_names())

    def get_related_articles(self):
        return Article.objects.filter(tags__in=self.tags.all()
                                      ).exclude(id=self.id).order_by('created',
                                                                     'title').distinct('created', 'title')[:3]

    def change_status(self, status):
        """更改状态"""
        if status is None or int(status) not in Article.Status.values:
            raise ValidationError('错误的状态')
        self.status = status
        self.save(update_fields=['status'])

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        ordering = ['-created']


class Comment(TimeStampedModel):
    body = models.TextField()
    article = models.ForeignKey('articles.Article', related_name='comments', on_delete=models.CASCADE)
    created_by = models.ForeignKey('authentication.User', related_name='comments', on_delete=models.CASCADE)
