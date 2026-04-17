from django.db.models import Count, OuterRef, Prefetch, Subquery

from .models import Brand, Vehicle, VehicleImage, VehicleInquiry, VehicleStatus


class VehicleQueryService:
    list_only_fields = [
        "id",
        "brand_id",
        "brand__id",
        "brand__name",
        "brand__slug",
        "category",
        "status",
        "fuel_type",
        "transmission",
        "name",
        "slug",
        "city",
        "price",
        "year",
        "seating_capacity",
        "is_featured",
        "created_at",
    ]

    detail_only_fields = list_only_fields + [
        "created_by_id",
        "created_by__id",
        "created_by__username",
        "body_type",
        "description",
        "engine_cc",
        "mileage_kmpl",
        "top_speed_kmph",
        "max_power_bhp",
        "fuel_tank_liters",
        "stroke_mm",
        "torque_nm",
        "motor_watts",
        "battery_kwh",
        "is_popular",
        "is_new",
        "is_upcoming",
        "is_ev",
        "available_colors",
        "dimensions",
        "updated_at",
    ]

    @classmethod
    def base_queryset(cls):
        primary_image_subquery = VehicleImage.objects.filter(
            vehicle_id=OuterRef("pk"),
            is_primary=True,
        ).values("image_url")[:1]

        return (
            Vehicle.objects.select_related("brand")
            .annotate(
                primary_image_url=Subquery(primary_image_subquery),
                inquiry_count=Count("inquiries", distinct=True),
            )
        )

    @classmethod
    def list_queryset(cls, params):
        queryset = cls.base_queryset().only(*cls.list_only_fields)
        queryset = cls.apply_filters(queryset, params)
        return queryset.order_by("-created_at", "-id")

    @classmethod
    def detail_queryset(cls):
        image_queryset = VehicleImage.objects.only(
            "id",
            "vehicle_id",
            "image_url",
            "alt_text",
            "sort_order",
            "is_primary",
        ).order_by("sort_order", "id")
        return (
            cls.base_queryset()
            .select_related("created_by")
            .only(*cls.detail_only_fields)
            .prefetch_related(Prefetch("images", queryset=image_queryset))
        )

    @classmethod
    def apply_filters(cls, queryset, params):
        category = params.get("category")
        status_value = params.get("status")
        brand_id = params.get("brand")
        fuel_type = params.get("fuel_type")
        transmission = params.get("transmission")
        city = params.get("city")
        is_featured = params.get("is_featured")
        year = params.get("year")
        slug = params.get("slug")

        if category:
            queryset = queryset.filter(category=category)
        if status_value:
            queryset = queryset.filter(status=status_value)
        else:
            queryset = queryset.filter(status=VehicleStatus.ACTIVE)
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)
        if fuel_type:
            queryset = queryset.filter(fuel_type=fuel_type)
        if transmission:
            queryset = queryset.filter(transmission=transmission)
        if city:
            queryset = queryset.filter(city__iexact=city)
        if is_featured is not None:
            normalized = str(is_featured).lower()
            if normalized in {"true", "1", "yes"}:
                queryset = queryset.filter(is_featured=True)
            elif normalized in {"false", "0", "no"}:
                queryset = queryset.filter(is_featured=False)
        if year:
            queryset = queryset.filter(year=year)
        if slug:
            queryset = queryset.filter(slug=slug)
        return queryset

    @staticmethod
    def summary_queryset(params):
        queryset = Vehicle.objects.all()
        queryset = VehicleQueryService.apply_filters(queryset, params)
        return queryset.values("category", "status").annotate(total=Count("id")).order_by("category", "status")


class VehicleWriteService:
    @staticmethod
    def create_vehicle(validated_data, user=None):
        image_payloads = validated_data.pop("images", [])
        if user and not validated_data.get("created_by"):
            validated_data["created_by"] = user

        vehicle = Vehicle.objects.create(**validated_data)
        VehicleWriteService.sync_images(vehicle, image_payloads)
        return vehicle

    @staticmethod
    def update_vehicle(instance, validated_data):
        image_payloads = validated_data.pop("images", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        if image_payloads is not None:
            instance.images.all().delete()
            VehicleWriteService.sync_images(instance, image_payloads)
        return instance

    @staticmethod
    def sync_images(vehicle, image_payloads):
        images = [VehicleImage(vehicle=vehicle, **payload) for payload in image_payloads]
        if images:
            VehicleImage.objects.bulk_create(images)


class VehicleInquiryService:
    @staticmethod
    def create_inquiry(validated_data):
        return VehicleInquiry.objects.create(**validated_data)

    @staticmethod
    def recent_inquiries(vehicle_id, limit=20):
        return (
            VehicleInquiry.objects.filter(vehicle_id=vehicle_id)
            .only("id", "vehicle_id", "full_name", "email", "phone", "status", "created_at")
            .order_by("-created_at", "-id")[:limit]
        )


class BrandQueryService:
    @staticmethod
    def active_brand_values(category=None):
        queryset = Brand.objects.filter(is_active=True)
        if category:
            queryset = queryset.filter(category=category)
        return queryset.values("id", "name", "slug", "category", "logo_url").order_by("name")


class VehicleCatalogService:
    CATEGORY_SLUG_MAP = {
        "two-wheelers": VehicleStatus.ACTIVE,
        "four-wheelers": VehicleStatus.ACTIVE,
    }

    CATEGORY_MODEL_MAP = {
        "two-wheelers": "two_wheeler",
        "four-wheelers": "four_wheeler",
    }

    @classmethod
    def get_category_value(cls, category_slug):
        return cls.CATEGORY_MODEL_MAP[category_slug]

    @classmethod
    def catalog_queryset(cls, category_slug):
        category_value = cls.get_category_value(category_slug)
        image_queryset = VehicleImage.objects.only(
            "id",
            "vehicle_id",
            "image_url",
            "sort_order",
            "is_primary",
        ).order_by("sort_order", "id")
        return (
            Vehicle.objects.filter(category=category_value, status__in=[VehicleStatus.ACTIVE, VehicleStatus.DRAFT])
            .select_related("brand")
            .only(
                "id",
                "brand_id",
                "brand__name",
                "brand__logo_url",
                "category",
                "name",
                "slug",
                "body_type",
                "price",
                "year",
                "engine_cc",
                "mileage_kmpl",
                "top_speed_kmph",
                "max_power_bhp",
                "fuel_tank_liters",
                "stroke_mm",
                "torque_nm",
                "motor_watts",
                "battery_kwh",
                "is_popular",
                "is_new",
                "is_upcoming",
                "is_ev",
                "available_colors",
                "dimensions",
                "description",
            )
            .prefetch_related(Prefetch("images", queryset=image_queryset))
            .order_by("-is_popular", "-is_new", "-year", "brand__name", "name")
        )

    @classmethod
    def brand_values(cls, category_slug):
        return Brand.objects.filter(
            category=cls.get_category_value(category_slug),
            is_active=True,
        ).values("name", "logo_url").order_by("name")
