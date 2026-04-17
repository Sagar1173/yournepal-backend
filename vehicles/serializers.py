from rest_framework import serializers

from .models import (
    Brand,
    FuelType,
    InquiryStatus,
    TransmissionType,
    Vehicle,
    VehicleCategory,
    VehicleImage,
    VehicleInquiry,
    VehicleStatus,
)
from .services import VehicleInquiryService, VehicleWriteService


class BrandMinimalSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    category = serializers.CharField()
    logo_url = serializers.URLField(allow_blank=True, required=False)


class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ["id", "image_url", "alt_text", "sort_order", "is_primary"]
        read_only_fields = ["id"]


class VehicleListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    brand = BrandMinimalSerializer(read_only=True)
    category = serializers.ChoiceField(choices=VehicleCategory.choices)
    status = serializers.ChoiceField(choices=VehicleStatus.choices)
    fuel_type = serializers.ChoiceField(choices=FuelType.choices)
    transmission = serializers.ChoiceField(choices=TransmissionType.choices)
    name = serializers.CharField()
    slug = serializers.CharField()
    city = serializers.CharField()
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    year = serializers.IntegerField()
    seating_capacity = serializers.IntegerField(allow_null=True)
    is_featured = serializers.BooleanField()
    primary_image_url = serializers.URLField(allow_null=True)
    inquiry_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class VehicleDetailSerializer(VehicleListSerializer):
    description = serializers.CharField()
    engine_cc = serializers.IntegerField(allow_null=True)
    mileage_kmpl = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    updated_at = serializers.DateTimeField()
    created_by = serializers.SerializerMethodField()
    images = VehicleImageSerializer(many=True, read_only=True)

    def get_created_by(self, obj):
        if not obj.created_by_id:
            return None
        return {"id": obj.created_by_id, "username": obj.created_by.username}


class VehicleImageWriteSerializer(serializers.Serializer):
    image_url = serializers.URLField(max_length=500)
    alt_text = serializers.CharField(max_length=150, allow_blank=True, required=False)
    sort_order = serializers.IntegerField(min_value=0, required=False, default=0)
    is_primary = serializers.BooleanField(required=False, default=False)


class VehicleWriteSerializer(serializers.ModelSerializer):
    images = VehicleImageWriteSerializer(many=True, required=False)

    class Meta:
        model = Vehicle
        fields = [
            "id",
            "brand",
            "category",
            "status",
            "fuel_type",
            "transmission",
            "name",
            "slug",
            "city",
            "price",
            "year",
            "engine_cc",
            "mileage_kmpl",
            "seating_capacity",
            "is_featured",
            "description",
            "images",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        brand = attrs.get("brand") or getattr(self.instance, "brand", None)
        category = attrs.get("category") or getattr(self.instance, "category", None)

        if brand and category and brand.category != category:
            raise serializers.ValidationError(
                {"brand": "Selected brand category does not match the vehicle category."}
            )

        images = attrs.get("images")
        if images:
            primary_count = sum(1 for image in images if image.get("is_primary"))
            if primary_count > 1:
                raise serializers.ValidationError({"images": "Only one primary image is allowed."})
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None
        return VehicleWriteService.create_vehicle(validated_data, user=user)

    def update(self, instance, validated_data):
        return VehicleWriteService.update_vehicle(instance, validated_data)


class VehicleStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ["status"]


class VehicleSummarySerializer(serializers.Serializer):
    category = serializers.CharField()
    status = serializers.CharField()
    total = serializers.IntegerField()


class VehicleInquiryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleInquiry
        fields = ["id", "vehicle", "full_name", "email", "phone", "message"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        return VehicleInquiryService.create_inquiry(validated_data)


class VehicleInquiryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleInquiry
        fields = ["id", "vehicle", "full_name", "email", "phone", "status", "created_at"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ["id", "name", "slug", "category", "logo_url"]


class InquiryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleInquiry
        fields = ["status"]


class CatalogBrandSerializer(serializers.Serializer):
    name = serializers.CharField()
    logo = serializers.CharField(source="logo_url", allow_blank=True)


class CatalogVehicleSerializer(serializers.Serializer):
    id = serializers.CharField(source="slug")
    type = serializers.SerializerMethodField()
    brand = serializers.CharField(source="brand.name")
    model = serializers.CharField(source="name")
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    isPopular = serializers.BooleanField(source="is_popular")
    isNew = serializers.BooleanField(source="is_new")
    isUpcoming = serializers.BooleanField(source="is_upcoming")
    isEV = serializers.BooleanField(source="is_ev")
    images = serializers.SerializerMethodField()
    availableColors = serializers.ListField(source="available_colors", child=serializers.CharField(), allow_empty=True)
    description = serializers.CharField()
    bodyType = serializers.CharField(source="body_type")
    displacement = serializers.SerializerMethodField()
    evRange = serializers.SerializerMethodField()
    motor = serializers.IntegerField(source="motor_watts", allow_null=True)
    battery = serializers.DecimalField(source="battery_kwh", max_digits=8, decimal_places=2, allow_null=True)
    engineSize = serializers.SerializerMethodField()
    mileage = serializers.SerializerMethodField()
    maxPower = serializers.DecimalField(source="max_power_bhp", max_digits=8, decimal_places=2, allow_null=True)
    topSpeed = serializers.IntegerField(source="top_speed_kmph", allow_null=True)
    modelYear = serializers.IntegerField(source="year")
    fuelTank = serializers.DecimalField(source="fuel_tank_liters", max_digits=6, decimal_places=2, allow_null=True)
    stroke = serializers.DecimalField(source="stroke_mm", max_digits=8, decimal_places=2, allow_null=True)
    torque = serializers.DecimalField(source="torque_nm", max_digits=8, decimal_places=2, allow_null=True)
    dimensions = serializers.JSONField()

    def get_type(self, obj):
        return "two-wheeler" if obj.category == VehicleCategory.TWO_WHEELER else "four-wheeler"

    def get_images(self, obj):
        images = getattr(obj, "_prefetched_objects_cache", {}).get("images")
        if images is None:
            images = obj.images.all()
        return [image.image_url for image in images]

    def get_displacement(self, obj):
        return obj.engine_cc

    def get_evRange(self, obj):
        if obj.is_ev:
            return float(obj.mileage_kmpl) if obj.mileage_kmpl is not None else None
        return None

    def get_engineSize(self, obj):
        return obj.engine_cc

    def get_mileage(self, obj):
        return float(obj.mileage_kmpl) if obj.mileage_kmpl is not None else None


class CatalogResponseSerializer(serializers.Serializer):
    vehicles = CatalogVehicleSerializer(many=True)
    brands = CatalogBrandSerializer(many=True)
    bodyTypes = serializers.ListField(child=serializers.CharField())
