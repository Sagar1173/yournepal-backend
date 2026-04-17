from django.urls import path

from .views import BrandListView, VehicleCatalogView, VehicleInquiryViewSet, VehicleViewSet

urlpatterns = [
    path("brands/", BrandListView.as_view(), name="vehicle-brand-list"),
    path("catalog/<slug:category>/", VehicleCatalogView.as_view(), name="vehicle-catalog"),
    path("", VehicleViewSet.as_view({"get": "list", "post": "create"}), name="vehicle-list"),
    path("summary/", VehicleViewSet.as_view({"get": "summary"}), name="vehicle-summary"),
    path("<int:pk>/", VehicleViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update"}), name="vehicle-detail"),
    path("<int:pk>/status/", VehicleViewSet.as_view({"patch": "set_status"}), name="vehicle-set-status"),
    path(
        "inquiries/",
        VehicleInquiryViewSet.as_view({"get": "list", "post": "create"}),
        name="vehicle-inquiry-list",
    ),
    path(
        "inquiries/<int:pk>/status/",
        VehicleInquiryViewSet.as_view({"patch": "set_status"}),
        name="vehicle-inquiry-set-status",
    ),
]
