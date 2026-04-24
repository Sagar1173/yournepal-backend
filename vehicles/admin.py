from django.contrib import admin
from django.utils.html import format_html

from .models import AuthorizedDealer, Brand, Vehicle, VehicleImage, VehicleInquiry


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 0
    fields = ("preview", "image", "image_external_url", "alt_text", "color", "sort_order", "is_primary")
    readonly_fields = ("preview",)

    @admin.display(description="Preview")
    def preview(self, obj):
        if not obj.pk or not obj.resolved_image_url:
            return "No image"
        return format_html(
            '<img src="{}" alt="{}" style="height: 64px; width: 96px; object-fit: cover; border-radius: 6px;" />',
            obj.resolved_image_url,
            obj.alt_text or "Vehicle image",
        )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("logo_preview", "name", "category", "is_active", "created_at")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("name", "slug")
    ordering = ("name",)
    readonly_fields = ("logo_preview", "created_at")
    fieldsets = (
        ("Brand", {"fields": ("name", "slug", "category", "is_active")}),
        ("Branding", {"fields": ("logo_preview", "logo", "logo_external_url")}),
        ("Metadata", {"fields": ("created_at",)}),
    )

    @admin.display(description="Logo")
    def logo_preview(self, obj):
        if not obj.pk or not obj.resolved_logo_url:
            return "No logo"
        return format_html(
            '<img src="{}" alt="{}" style="height: 48px; width: 48px; object-fit: contain; border-radius: 6px;" />',
            obj.resolved_logo_url,
            obj.name,
        )


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "primary_image_preview",
        "name",
        "brand",
        "category",
        "status",
        "fuel_type",
        "city",
        "price",
        "year",
        "created_at",
    )
    list_filter = (
        "category",
        "brand",
        "status",
        "fuel_type",
        "transmission",
        "is_featured",
        "is_popular",
        "is_upcoming",
        "created_at",
    )
    search_fields = ("name", "slug", "brand__name", "city", "body_type")
    ordering = ("-created_at", "-id")
    readonly_fields = ("primary_image_preview", "created_at", "updated_at")
    fieldsets = (
        ("Vehicle", {"fields": ("primary_image_preview", "name", "slug", "brand", "category", "status")}),
        (
            "Pricing & Positioning",
            {"fields": ("price", "year", "city", "body_type", "description")},
        ),
        (
            "Powertrain",
            {
                "fields": (
                    "fuel_type",
                    "transmission",
                    "engine_cc",
                    "mileage_kmpl",
                    "max_power_bhp",
                    "torque_nm",
                    "top_speed_kmph",
                    "fuel_tank_liters",
                    "stroke_mm",
                    "motor_watts",
                    "battery_kwh",
                    "seating_capacity",
                )
            },
        ),
        (
            "Flags",
            {"fields": ("is_featured", "is_popular", "is_new", "is_upcoming", "is_ev", "available_colors", "dimensions")},
        ),
        ("Audit", {"fields": ("created_by", "created_at", "updated_at")}),
    )
    inlines = [VehicleImageInline]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("brand", "created_by").prefetch_related("images")

    @admin.display(description="Image")
    def primary_image_preview(self, obj):
        images = list(obj.images.all())
        primary_image = next((image for image in images if image.is_primary), images[0] if images else None)
        if not primary_image or not primary_image.resolved_image_url:
            return "No image"
        return format_html(
            '<img src="{}" alt="{}" style="height: 64px; width: 96px; object-fit: cover; border-radius: 6px;" />',
            primary_image.resolved_image_url,
            obj.name,
        )


@admin.register(VehicleInquiry)
class VehicleInquiryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "vehicle", "email", "phone", "dealer_location", "status", "created_at")
    list_filter = ("status", "vehicle__brand", "vehicle__category", "dealer_location", "created_at", "preferred_date")
    search_fields = ("full_name", "email", "phone", "dealer_location", "vehicle__name", "vehicle__brand__name")
    ordering = ("-created_at", "-id")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Contact", {"fields": ("vehicle", "full_name", "email", "phone", "city")}),
        ("Visit Details", {"fields": ("dealer_location", "preferred_date", "message", "status")}),
        ("Metadata", {"fields": ("created_at",)}),
    )


@admin.register(AuthorizedDealer)
class AuthorizedDealerAdmin(admin.ModelAdmin):
    list_display = ("dealer_name", "brand", "city", "phone", "created_at")
    list_filter = ("brand", "city", "created_at")
    search_fields = ("dealer_name", "address", "city", "phone", "brand__name")
    ordering = ("dealer_name", "id")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Dealer", {"fields": ("dealer_name", "brand", "phone")}),
        ("Location", {"fields": ("city", "address")}),
        ("Metadata", {"fields": ("created_at",)}),
    )
