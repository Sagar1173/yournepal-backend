from django.shortcuts import get_object_or_404

from .models import News, NewsStatus


class NewsQueryService:
    base_only_fields = [
        "id",
        "title",
        "summary",
        "image",
        "source_url",
        "status",
        "created_at",
        "updated_at",
        "category_id",
        "category__id",
        "category__name",
        "category__slug",
    ]

    @classmethod
    def published_queryset(cls):
        return (
            News.objects.select_related("category")
            .only(*cls.base_only_fields)
            .filter(status=NewsStatus.PUBLISHED)
            .order_by("-created_at", "-id")
        )

    @classmethod
    def category_queryset(cls, category_slug):
        return cls.published_queryset().filter(category__slug=category_slug)

    @classmethod
    def flash_queryset(cls, limit=5):
        return cls.category_queryset("flash")[:limit]

    @classmethod
    def home_payload(cls):
        return {
            "flash_news": cls.flash_queryset(limit=5),
            "nepal_news": cls.category_queryset("nepal")[:6],
            "international_news": cls.category_queryset("international")[:6],
        }

    @classmethod
    def detail_queryset(cls):
        return cls.published_queryset()

    @classmethod
    def get_published_news(cls, news_id):
        return get_object_or_404(cls.detail_queryset(), pk=news_id)

