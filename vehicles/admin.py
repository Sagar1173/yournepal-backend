from django.contrib import admin

from .models import Brand, Vehicle, VehicleImage, VehicleInquiry


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 0


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("name", "slug")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "category", "status", "fuel_type", "city", "price", "created_at")
    list_filter = ("category", "status", "fuel_type", "transmission", "is_featured", "city")
    search_fields = ("name", "slug")
    inlines = [VehicleImageInline]


@admin.register(VehicleInquiry)
class VehicleInquiryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "vehicle", "email", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "phone")
