from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Vehicle, VehicleInquiry
from .serializers import (
    BrandMinimalSerializer,
    CatalogResponseSerializer,
    InquiryStatusSerializer,
    VehicleDetailSerializer,
    VehicleInquiryCreateSerializer,
    VehicleInquiryListSerializer,
    VehicleListSerializer,
    VehicleStatusSerializer,
    VehicleSummarySerializer,
    VehicleWriteSerializer,
)
from .services import BrandQueryService, VehicleCatalogService, VehicleQueryService


class BrandListView(APIView):
    def get(self, request, *args, **kwargs):
        category = request.query_params.get("category")
        serializer = BrandMinimalSerializer(
            BrandQueryService.active_brand_values(category=category),
            many=True,
            context={"request": request},
        )
        return Response(serializer.data)


class VehicleCatalogView(APIView):
    def get(self, request, category, *args, **kwargs):
        try:
            vehicles = list(VehicleCatalogService.catalog_queryset(category))
            brands = list(VehicleCatalogService.brand_values(category))
        except KeyError as exc:
            raise NotFound("Unknown vehicle category.") from exc

        body_types = sorted({vehicle.body_type for vehicle in vehicles if vehicle.body_type})

        serializer = CatalogResponseSerializer(
            {
                "vehicles": vehicles,
                "brands": brands,
                "bodyTypes": body_types,
            },
            context={"request": request},
        )
        return Response(serializer.data)


class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.none()

    def get_queryset(self):
        if self.action == "retrieve":
            return VehicleQueryService.detail_queryset()
        if self.action in {"list", "summary"}:
            return VehicleQueryService.list_queryset(self.request.query_params)
        return Vehicle.objects.select_related("brand", "created_by").only(
            "id",
            "brand_id",
            "created_by_id",
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
            "created_at",
            "updated_at",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return VehicleListSerializer
        if self.action == "retrieve":
            return VehicleDetailSerializer
        if self.action == "set_status":
            return VehicleStatusSerializer
        if self.action == "summary":
            return VehicleSummarySerializer
        return VehicleWriteSerializer

    @action(detail=False, methods=["get"])
    def summary(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            VehicleQueryService.summary_queryset(request.query_params),
            many=True,
        )
        return Response(serializer.data)

    @action(detail=True, methods=["patch"], url_path="status")
    def set_status(self, request, *args, **kwargs):
        vehicle = self.get_object()
        serializer = self.get_serializer(vehicle, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"id": vehicle.id, "status": serializer.instance.status})


class VehicleInquiryViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = VehicleInquiry.objects.none()

    def get_queryset(self):
        queryset = VehicleInquiry.objects.select_related("vehicle").only(
            "id",
            "vehicle_id",
            "full_name",
            "email",
            "phone",
            "city",
            "dealer_location",
            "preferred_date",
            "status",
            "created_at",
            "vehicle__id",
            "vehicle__name",
        )
        vehicle_id = self.request.query_params.get("vehicle")
        status_value = self.request.query_params.get("status")
        email = self.request.query_params.get("email")

        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)
        if status_value:
            queryset = queryset.filter(status=status_value)
        if email:
            queryset = queryset.filter(email=email)
        return queryset.order_by("-created_at", "-id")

    def get_serializer_class(self):
        if self.action == "create":
            return VehicleInquiryCreateSerializer
        if self.action == "set_status":
            return InquiryStatusSerializer
        return VehicleInquiryListSerializer

    @action(detail=True, methods=["patch"], url_path="status")
    def set_status(self, request, *args, **kwargs):
        inquiry = self.get_object()
        serializer = self.get_serializer(inquiry, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"id": inquiry.id, "status": serializer.instance.status})
