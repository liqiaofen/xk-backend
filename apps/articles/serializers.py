from rest_framework import serializers

from articles.models import Article


class ArticleSerializer(serializers.ModelSerializer):
    # author = ProfileSerializer(read_only=True)
    description = serializers.CharField(required=False)
    slug = serializers.SlugField(required=False)

    favorited = serializers.SerializerMethodField()
    favoritesCount = serializers.SerializerMethodField(method_name='get_favorites_count')

    # tagList = TagRelatedField(many=True, required=False, source='tags')
    createdAt = serializers.SerializerMethodField(method_name='get_created_at')
    updatedAt = serializers.SerializerMethodField(method_name='get_updated_at')

    class Meta:
        model = Article
        fields = (
            'author',
            'body',
            'createdAt',
            'description',
            'favorited',
            'favoritesCount',
            'slug',
            'tagList',
            'title',
            'updatedAt',
        )

    def create(self, validated_data):
        author = self.context.get('created_by', None)

        tags = validated_data.pop('tags', [])

        article = Article.objects.create(created_by=author, **validated_data)

        for tag in tags:
            article.tags.add(tag)

        return article

    def get_created_at(self, instance):
        return instance.created_at.isoformat()

    def get_updated_at(self, instance):
        return instance.updated_at.isoformat()

    def get_favorited(self, instance):
        request = self.context.get('request', None)

        if request is None:
            return False

        if not request.user.is_authenticated():
            return False

        return request.user.profile.has_favorited(instance)

    def get_favorites_count(self, instance):
        return instance.favorited_by.count()
