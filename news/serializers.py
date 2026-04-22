from rest_framework import serializers

from .models import News


class FlashNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["id", "title", "summary", "image", "created_at"]


class NewsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["id", "title", "summary", "created_at"]


class NewsDetailSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.slug", read_only=True)

    class Meta:
        model = News
        fields = ["id", "title", "summary", "image", "created_at", "category", "source_url"]

