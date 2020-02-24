from rest_framework import serializers

from main.models import Bb, Comment, Rubric


class BbSerializer(serializers.ModelSerializer):
    """Сериализатор свединий о каждом объявлении."""
    class Meta:
        model = Bb
        fields = ('id', 'title', 'content', 'price', 'created_at')


class BbDetailSerializer(serializers.ModelSerializer):
    """Сериализатор полных сведений об объявлении."""
    class Meta:
        model = Bb
        fields = ('id', 'title', 'content', 'price', 'created_at',
                  'contacts', 'image')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментариев."""
    class Meta:
        model = Comment
        fields = ('bb', 'author', 'content', 'created_at')


class RubricSerializer(serializers.ModelSerializer):
    """Сериализатор рубрик."""
    class Meta:
        model = Rubric
        fields = ('id', 'order', 'name', 'super_rubric')
