import json
import subprocess
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from vehicles.models import Brand, FuelType, TransmissionType, Vehicle, VehicleCategory, VehicleImage, VehicleStatus


ROOT_DIR = Path(__file__).resolve().parents[4]
FRONTEND_DATA_FILE = ROOT_DIR / "frontend" / "data" / "vehicles.js"


def normalize_category(vehicle_type):
    if vehicle_type == "two-wheeler":
        return VehicleCategory.TWO_WHEELER
    return VehicleCategory.FOUR_WHEELER


def infer_fuel_type(item):
    if item.get("isEV"):
        return FuelType.ELECTRIC
    if item.get("type") == "four-wheeler" and item.get("brand") in {"Toyota", "Mahindra", "Hyundai", "Kia"}:
        return FuelType.DIESEL
    return FuelType.PETROL


def infer_transmission(item):
    if item.get("isEV") or item.get("type") == "four-wheeler":
        return TransmissionType.AUTOMATIC
    return TransmissionType.MANUAL


def infer_image_color(item, index, total_images):
    colors = item.get("availableColors", [])
    if not colors:
        return ""
    if len(colors) == 1:
        return colors[0]
    if len(colors) == total_images:
        return colors[index]
    if total_images % len(colors) == 0:
        chunk_size = total_images // len(colors)
        return colors[min(index // chunk_size, len(colors) - 1)]
    return ""


def run_node_export():
    node_script = f"""
import fs from "node:fs/promises";
const code = await fs.readFile({json.dumps(str(FRONTEND_DATA_FILE))}, "utf8");
const moduleUrl = "data:text/javascript," + encodeURIComponent(code);
const data = await import(moduleUrl);
console.log(JSON.stringify({{
  twoWheelers: data.twoWheelers,
  fourWheelers: data.fourWheelers,
  twoWheelerBrands: data.twoWheelerBrands,
  fourWheelerBrands: data.fourWheelerBrands
}}));
"""
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", node_script],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(completed.stdout)


class Command(BaseCommand):
    help = "Import the frontend vehicle catalog into the Django database."

    @transaction.atomic
    def handle(self, *args, **options):
        payload = run_node_export()

        brand_logos = {
            VehicleCategory.TWO_WHEELER: {item["name"]: item.get("logo", "") for item in payload["twoWheelerBrands"]},
            VehicleCategory.FOUR_WHEELER: {item["name"]: item.get("logo", "") for item in payload["fourWheelerBrands"]},
        }

        imported_count = 0

        for item in payload["twoWheelers"] + payload["fourWheelers"]:
            category = normalize_category(item["type"])
            brand, _ = Brand.objects.update_or_create(
                slug=slugify(item["brand"]),
                defaults={
                    "name": item["brand"],
                    "category": category,
                    "logo_external_url": brand_logos[category].get(item["brand"], ""),
                    "is_active": True,
                },
            )

            defaults = {
                "brand": brand,
                "category": category,
                "status": VehicleStatus.ACTIVE if not item.get("isUpcoming") else VehicleStatus.DRAFT,
                "fuel_type": infer_fuel_type(item),
                "transmission": infer_transmission(item),
                "name": item["model"],
                "city": "Kathmandu",
                "body_type": item.get("bodyType", ""),
                "price": Decimal(str(item["price"])),
                "year": item.get("modelYear") or 2025,
                "engine_cc": int(round(item["engineSize"])) if item.get("engineSize") is not None else None,
                "mileage_kmpl": Decimal(str(item["mileage"])) if item.get("mileage") is not None else None,
                "top_speed_kmph": item.get("topSpeed"),
                "max_power_bhp": Decimal(str(item["maxPower"])) if item.get("maxPower") is not None else None,
                "fuel_tank_liters": Decimal(str(item["fuelTank"])) if item.get("fuelTank") is not None else None,
                "stroke_mm": Decimal(str(item["stroke"])) if item.get("stroke") is not None else None,
                "torque_nm": Decimal(str(item["torque"])) if item.get("torque") is not None else None,
                "motor_watts": item.get("motor"),
                "battery_kwh": Decimal(str(item["battery"])) if item.get("battery") is not None else None,
                "is_featured": bool(item.get("isPopular") or item.get("isNew")),
                "is_popular": bool(item.get("isPopular")),
                "is_new": bool(item.get("isNew")),
                "is_upcoming": bool(item.get("isUpcoming")),
                "is_ev": bool(item.get("isEV")),
                "available_colors": item.get("availableColors", []),
                "dimensions": item.get("dimensions", {}),
                "description": item.get("description", ""),
            }

            vehicle, _ = Vehicle.objects.update_or_create(
                slug=item["id"],
                defaults=defaults,
            )

            VehicleImage.objects.filter(vehicle=vehicle).delete()
            VehicleImage.objects.bulk_create(
                [
                    VehicleImage(
                        vehicle=vehicle,
                        image_external_url=image_url,
                        alt_text=item["model"],
                        color=infer_image_color(item, index, len(item.get("images", []))),
                        sort_order=index,
                        is_primary=index == 0,
                    )
                    for index, image_url in enumerate(item.get("images", []))
                ]
            )
            imported_count += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {imported_count} vehicles into the database."))
