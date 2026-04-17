from django.db import models
from django.db.models import Q
from django.utils.text import slugify


class NewsCategory(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)
    slug = models.SlugField(max_length=50, unique=True, db_index=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"], name="news_newsca_slug_5c0a14_idx"),
            models.Index(fields=["name"], name="news_newsca_name_f13acd_idx"),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class NewsStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"


class News(models.Model):
    category = models.ForeignKey(
        NewsCategory,
        on_delete=models.PROTECT,
        related_name="news_items",
        db_index=True,
    )
    title = models.CharField(max_length=255)
    summary = models.TextField(help_text="Short summary intended to stay around 40-80 words.")
    image = models.URLField(max_length=500, blank=True)
    source_url = models.URLField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20,
        choices=NewsStatus.choices,
        default=NewsStatus.DRAFT,
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(status__in=[NewsStatus.DRAFT, NewsStatus.PUBLISHED]),
                name="news_status_valid_choice",
            ),
            models.CheckConstraint(
                condition=~Q(title=""),
                name="news_title_not_blank",
            ),
            models.CheckConstraint(
                condition=~Q(summary=""),
                name="news_summary_not_blank",
            ),
        ]
        indexes = [
            models.Index(fields=["category", "status"], name="news_news_categor_caf58c_idx"),
            models.Index(fields=["status", "created_at"], name="news_news_status_ce57ad_idx"),
            models.Index(fields=["category", "created_at"], name="news_news_categor_457393_idx"),
        ]

    def __str__(self):
        return self.title
