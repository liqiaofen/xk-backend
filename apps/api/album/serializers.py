from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from album.models import Album, Picture
from core import serpy
from core.utils import get_object_or_error


class AlbumCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    name = serializers.CharField(validators=[UniqueValidator(queryset=Album.objects.all(), message='此名称已被使用')])

    class Meta:
        model = Album
        fields = ['name', 'created_by', 'id', 'picture_count']
        read_only_fields = ['picture_count']
        # extra_kwargs = {"name": {"error_messages": {"unique": "Give yourself a username"}}}
        # error_messages = {
        #     "name": {"required": "For some reason this is a custom error message overriding the model's default"}
        # }


class AlbumBaseSerializer(serpy.Serializer):
    id = serpy.StrField()
    name = serpy.StrField()
    picture_count = serpy.IntField()


class AlbumListSerializer(AlbumBaseSerializer):
    cover = serpy.StrField(attr='newest')


class PictureCreateSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    album = serializers.CharField(write_only=True)

    class Meta:
        model = Picture
        fields = ['image', 'created_by', 'album', 'id']

    # @staticmethod
    def validate_album(self, value):
        return get_object_or_error(Album, name=value)


class PictureListSerializer(serpy.Serializer):
    id = serpy.StrField()
    # file = serpy.StrField(attr='file.url')
    image = serpy.StrField(attr='image_url')
    created_by = serpy.StrField()
