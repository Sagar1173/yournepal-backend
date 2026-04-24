from django.contrib import admin

from .models import Suggestion


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "created_at")
    search_fields = ("suggestion_text",)
    ordering = ("-created_at", "-id")
    readonly_fields = ("created_at",)

    @admin.display(description="Suggestion")
    def short_text(self, obj):
        text = obj.suggestion_text.strip()
        return text[:80] + ("..." if len(text) > 80 else "")

