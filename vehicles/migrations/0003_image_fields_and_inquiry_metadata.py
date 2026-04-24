from django.db import migrations, models


def migrate_legacy_image_urls(apps, schema_editor):
    Brand = apps.get_model("vehicles", "Brand")
    VehicleImage = apps.get_model("vehicles", "VehicleImage")

    for brand in Brand.objects.exclude(logo_url="").iterator():
        brand.logo_external_url = brand.logo_url
        brand.save(update_fields=["logo_external_url"])

    for vehicle_image in VehicleImage.objects.exclude(image_url="").iterator():
        vehicle_image.image_external_url = vehicle_image.image_url
        vehicle_image.save(update_fields=["image_external_url"])


class Migration(migrations.Migration):

    dependencies = [
        ("vehicles", "0002_brand_logo_url_vehicle_available_colors_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="brand",
            name="logo",
            field=models.ImageField(blank=True, upload_to="vehicles/brands/"),
        ),
        migrations.AddField(
            model_name="brand",
            name="logo_external_url",
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="vehicleimage",
            name="image",
            field=models.ImageField(blank=True, upload_to="vehicles/images/"),
        ),
        migrations.AddField(
            model_name="vehicleimage",
            name="image_external_url",
            field=models.URLField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="vehicleinquiry",
            name="city",
            field=models.CharField(blank=True, db_index=True, max_length=100),
        ),
        migrations.AddField(
            model_name="vehicleinquiry",
            name="dealer_location",
            field=models.CharField(blank=True, db_index=True, max_length=150),
        ),
        migrations.AddField(
            model_name="vehicleinquiry",
            name="preferred_date",
            field=models.DateField(blank=True, db_index=True, null=True),
        ),
        migrations.RunPython(migrate_legacy_image_urls, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="brand",
            name="logo_url",
        ),
        migrations.RemoveField(
            model_name="vehicleimage",
            name="image_url",
        ),
        migrations.AddIndex(
            model_name="vehicleinquiry",
            index=models.Index(fields=["dealer_location", "status", "-created_at"], name="vehicles_ve_dealer__2b5056_idx"),
        ),
    ]
