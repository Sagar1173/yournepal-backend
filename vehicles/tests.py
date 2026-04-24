from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Brand,
    FuelType,
    TransmissionType,
    Vehicle,
    VehicleCategory,
    VehicleImage,
    VehicleInquiry,
    VehicleStatus,
)


class VehicleApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="manager",
            email="manager@example.com",
            password="pass1234",
        )
        self.brand = Brand.objects.create(
            name="Honda",
            slug="honda",
            category=VehicleCategory.TWO_WHEELER,
        )
        self.car_brand = Brand.objects.create(
            name="Hyundai",
            slug="hyundai",
            category=VehicleCategory.FOUR_WHEELER,
        )
        self.vehicle = Vehicle.objects.create(
            brand=self.brand,
            created_by=self.user,
            category=VehicleCategory.TWO_WHEELER,
            status=VehicleStatus.ACTIVE,
            fuel_type=FuelType.PETROL,
            transmission=TransmissionType.MANUAL,
            name="Shine",
            slug="shine-2024",
            city="Kathmandu",
            price=Decimal("320000.00"),
            year=2024,
            engine_cc=125,
            mileage_kmpl=Decimal("55.00"),
            is_featured=True,
            description="Reliable commuter bike.",
        )
        VehicleImage.objects.create(
            vehicle=self.vehicle,
            image_external_url="https://example.com/shine-primary.jpg",
            alt_text="Front view",
            sort_order=0,
            is_primary=True,
        )

    def test_vehicle_list_is_paginated_and_filtered(self):
        Vehicle.objects.create(
            brand=self.brand,
            category=VehicleCategory.TWO_WHEELER,
            status=VehicleStatus.ARCHIVED,
            fuel_type=FuelType.PETROL,
            transmission=TransmissionType.MANUAL,
            name="Old Shine",
            slug="old-shine-2022",
            city="Pokhara",
            price=Decimal("200000.00"),
            year=2022,
        )

        response = self.client.get(
            reverse("vehicle-list"),
            {"category": VehicleCategory.TWO_WHEELER, "status": VehicleStatus.ACTIVE},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["slug"], self.vehicle.slug)

    def test_vehicle_detail_returns_minimal_nested_data(self):
        response = self.client.get(reverse("vehicle-detail", args=[self.vehicle.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["brand"]["slug"], "honda")
        self.assertEqual(len(response.data["images"]), 1)
        self.assertNotIn("inquiries", response.data)

    def test_vehicle_create_accepts_image_payloads(self):
        payload = {
            "brand": self.car_brand.id,
            "category": VehicleCategory.FOUR_WHEELER,
            "status": VehicleStatus.ACTIVE,
            "fuel_type": FuelType.DIESEL,
            "transmission": TransmissionType.AUTOMATIC,
            "name": "Creta",
            "slug": "creta-2025",
            "city": "Lalitpur",
            "price": "5400000.00",
            "year": 2025,
            "engine_cc": 1493,
            "seating_capacity": 5,
            "description": "Compact SUV",
            "images": [
                {
                    "image_external_url": "https://example.com/creta.jpg",
                    "alt_text": "Creta",
                    "sort_order": 0,
                    "is_primary": True,
                }
            ],
        }

        response = self.client.post(reverse("vehicle-list"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_vehicle = Vehicle.objects.get(slug="creta-2025")
        self.assertEqual(created_vehicle.images.count(), 1)

    def test_summary_uses_aggregated_counts(self):
        response = self.client.get(reverse("vehicle-summary"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["total"], 1)

    def test_catalog_endpoint_returns_frontend_shape(self):
        response = self.client.get(reverse("vehicle-catalog", args=["two-wheelers"]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("vehicles", response.data)
        self.assertIn("brands", response.data)
        self.assertEqual(response.data["vehicles"][0]["id"], self.vehicle.slug)
        self.assertEqual(response.data["vehicles"][0]["brand"], "Honda")
        self.assertIsInstance(response.data["vehicles"][0]["images"], list)

    def test_inquiry_create_and_list(self):
        create_response = self.client.post(
            reverse("vehicle-inquiry-list"),
            {
                "vehicle": self.vehicle.id,
                "full_name": "Alice",
                "email": "alice@example.com",
                "phone": "9800000000",
                "city": "Kathmandu",
                "dealer_location": "Naxal, Kathmandu",
                "preferred_date": "2026-04-25",
                "message": "Need a test ride",
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        list_response = self.client.get(
            reverse("vehicle-inquiry-list"),
            {"vehicle": self.vehicle.id, "email": "alice@example.com"},
        )

        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data["count"], 1)
        self.assertEqual(list_response.data["results"][0]["full_name"], "Alice")
