from django.contrib import admin
from django.utils.html import format_html
from .models import News, NewsCategory, NewsStatus


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "news_count"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["name"]

    def news_count(self, obj):
        return obj.news_items.count()
    news_count.short_description = "Total News"


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = [
        "title", "category", "status", "image_preview",
        "has_source_url", "created_at", "updated_at"
    ]
    list_filter = ["status", "category", "created_at"]
    search_fields = ["title", "summary", "category__name"]
    list_editable = ["status"]
    readonly_fields = ["created_at", "updated_at", "image_preview"]
    date_hierarchy = "created_at"
    list_per_page = 25
    ordering = ["-created_at"]

    fieldsets = (
        ("Content", {
            "fields": ("category", "title", "summary")
        }),
        ("Media & Links", {
            "fields": ("image", "image_preview", "source_url")
        }),
        ("Publishing", {
            "fields": ("status",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    actions = ["mark_as_published", "mark_as_draft"]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:60px; border-radius:4px;" />', obj.image)
        return "No image"
    image_preview.short_description = "Preview"

    def has_source_url(self, obj):
        return bool(obj.source_url)
    has_source_url.boolean = True
    has_source_url.short_description = "Source URL"

    @admin.action(description="Mark selected news as Published")
    def mark_as_published(self, request, queryset):
        updated = queryset.update(status=NewsStatus.PUBLISHED)
        self.message_user(request, f"{updated} news item(s) marked as Published.")

    @admin.action(description="Mark selected news as Draft")
    def mark_as_draft(self, request, queryset):
        updated = queryset.update(status=NewsStatus.DRAFT)
        self.message_user(request, f"{updated} news item(s) marked as Draft.")