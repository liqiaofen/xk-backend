# class RecursiveField(serpy)
#
#
# class FolderListSerializer(serpy.Serializer):
#     name = serpy.StrField()
#     children = serpy.MethodField()
#
#     def get_children(self, obj):
#         return FolderListSerializer(obj.get_children(), many=True).data
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from articles.models import Folder, Article, ArticleImage, Tag
# https://stackoverflow.com/questions/27073115/django-mptt-efficiently-serializing-relational-data-with-drf
# https://stackoverflow.com/questions/26593312/optimizing-database-queries-in-django-rest-framework/26598897#26598897
from core.mixin.serializers import QuerySerializerMixin
from core.utils import get_object_or_error


class RecursiveField(serializers.Serializer):

    def to_native(self, value):
        return FolderListSerializer(value, context={"parent": self.parent.object, "parent_serializer": self.parent})


class FolderListSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Folder
        fields = ('id', 'name', 'children')

    # group_count = serializers.Field(source='get_group_count')
    def get_children(self, obj):
        return FolderListSerializer(obj.get_children(), many=True).data


class FolderCreateSerializer(serializers.ModelSerializer):
    parent = serializers.CharField(required=False, write_only=True)
    name = serializers.CharField(max_length=10, write_only=True)

    class Meta:
        model = Folder
        fields = ('parent', 'name', 'id', 'path')
        read_only_fields = ['path', 'id']

    def validate_name(self, value):
        obj = Folder.objects.filter(name=value, path=f'{self.initial_data["parent"]}/{value}').exists()
        print(obj)
        if obj:
            raise ValidationError(f'当前路径下已经存在{value}文件夹')
        return value

    def validate_parent(self, value):
        if value is None:
            return None
        obj = Folder.objects.filter(path=value).first()
        if obj is None:
            raise ValidationError('不存在的路径')
        return obj


class ArticleListSerializer(QuerySerializerMixin, serializers.ModelSerializer):
    PREFETCH_FIELDS = ['tags']
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Article
        fields = ('title', 'id', 'abstract', 'cover_url', 'tags')


class ArticleDetailSerializer(QuerySerializerMixin, serializers.ModelSerializer):
    PREFETCH_FIELDS = ['tags']
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = Article
        fields = ('title', 'id', 'abstract', 'cover_url', 'tags', 'content', 'modified')


class ArticleCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    folder = serializers.CharField()

    class Meta:
        model = Article
        fields = ('title', 'id', 'created_by', 'folder')

    def validate_folder(self, value):
        obj = get_object_or_error(Folder, err_msg='不存在的路径', path=value)
        return obj


class ArticleUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(required=False)

    class Meta:
        model = Article
        fields = ('id', 'title', 'abstract', 'content', 'tags', 'cover')
        extra_kwargs = {'cover': {'required': False}}

    def validate_cover(self, value):
        if self.instance.cover:  # 存在就删除
            self.instance.cover.delete()
        return value

    def validate_tags(self, value):
        tags = value.strip().split(' ')
        exist = Tag.objects.filter(name__in=tags).in_bulk(field_name='name')
        not_exist = set(tags) - set(exist.keys())
        objs = Tag.objects.bulk_create([Tag(name=tag) for tag in not_exist], batch_size=100)
        return [*objs, *exist.values()]


class ArticleImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleImage
        fields = ('id', 'file')
