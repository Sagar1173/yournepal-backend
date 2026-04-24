from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


class VehicleCategory(models.TextChoices):
    TWO_WHEELER = "two_wheeler", "Two Wheeler"
    FOUR_WHEELER = "four_wheeler", "Four Wheeler"


class VehicleStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    ACTIVE = "active", "Active"
    SOLD = "sold", "Sold"
    ARCHIVED = "archived", "Archived"


class FuelType(models.TextChoices):
    PETROL = "petrol", "Petrol"
    DIESEL = "diesel", "Diesel"
    ELECTRIC = "electric", "Electric"
    HYBRID = "hybrid", "Hybrid"
    CNG = "cng", "CNG"


class TransmissionType(models.TextChoices):
    MANUAL = "manual", "Manual"
    AUTOMATIC = "automatic", "Automatic"


class InquiryStatus(models.TextChoices):
    NEW = "new", "New"
    CONTACTED = "contacted", "Contacted"
    CLOSED = "closed", "Closed"


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    logo = models.ImageField(upload_to="vehicles/brands/", blank=True)
    logo_external_url = models.URLField(max_length=500, blank=True)
    category = models.CharField(
        max_length=20,
        choices=VehicleCategory.choices,
        db_index=True,
        help_text="Limits a brand to either two wheelers or four wheelers.",
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["category", "created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def resolved_logo_url(self):
        if self.logo:
            return self.logo.url
        return self.logo_external_url


class Vehicle(models.Model):
    brand = models.ForeignKey(
        Brand,
        on_delete=models.PROTECT,
        related_name="vehicles",
        db_index=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="vehicles",
        null=True,
        blank=True,
        db_index=True,
    )
    category = models.CharField(max_length=20, choices=VehicleCategory.choices, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=VehicleStatus.choices,
        default=VehicleStatus.DRAFT,
        db_index=True,
    )
    fuel_type = models.CharField(max_length=20, choices=FuelType.choices, db_index=True)
    transmission = models.CharField(
        max_length=20,
        choices=TransmissionType.choices,
        default=TransmissionType.MANUAL,
        db_index=True,
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True)
    city = models.CharField(max_length=100, db_index=True)
    body_type = models.CharField(max_length=50, blank=True, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    year = models.PositiveIntegerField(db_index=True)
    engine_cc = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    mileage_kmpl = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    seating_capacity = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
    )
    top_speed_kmph = models.PositiveIntegerField(null=True, blank=True)
    max_power_bhp = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    fuel_tank_liters = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    stroke_mm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    torque_nm = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    motor_watts = models.PositiveIntegerField(null=True, blank=True)
    battery_kwh = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_popular = models.BooleanField(default=False, db_index=True)
    is_new = models.BooleanField(default=False, db_index=True)
    is_upcoming = models.BooleanField(default=False, db_index=True)
    is_ev = models.BooleanField(default=False, db_index=True)
    available_colors = models.JSONField(default=list, blank=True)
    dimensions = models.JSONField(default=dict, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["brand", "category", "name", "year"],
                name="unique_vehicle_per_brand_category_name_year",
            ),
            models.CheckConstraint(
                condition=Q(price__gte=0),
                name="vehicle_price_non_negative",
            ),
            models.CheckConstraint(
                condition=Q(year__gte=1950),
                name="vehicle_year_at_least_1950",
            ),
            models.CheckConstraint(
                condition=Q(engine_cc__isnull=True) | Q(engine_cc__gt=0),
                name="vehicle_engine_cc_positive_or_null",
            ),
            models.CheckConstraint(
                condition=Q(mileage_kmpl__isnull=True) | Q(mileage_kmpl__gte=0),
                name="vehicle_mileage_non_negative_or_null",
            ),
            models.CheckConstraint(
                condition=Q(seating_capacity__isnull=True) | Q(seating_capacity__gte=1),
                name="vehicle_seating_capacity_positive_or_null",
            ),
        ]
        indexes = [
            models.Index(fields=["category", "status", "-created_at"]),
            models.Index(fields=["brand", "category", "status"]),
            models.Index(fields=["fuel_type", "status", "-created_at"]),
            models.Index(fields=["city", "status", "-created_at"]),
            models.Index(fields=["body_type", "status", "-created_at"]),
            models.Index(fields=["is_featured", "status", "-created_at"]),
            models.Index(fields=["is_popular", "status", "-created_at"]),
            models.Index(fields=["is_upcoming", "status", "-created_at"]),
            models.Index(fields=["is_ev", "status", "-created_at"]),
            models.Index(fields=["created_by", "status", "-created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand_id or 'vehicle'}-{self.name}-{self.year}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class VehicleImage(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="images",
        db_index=True,
    )
    image = models.ImageField(upload_to="vehicles/images/", blank=True)
    image_external_url = models.URLField(max_length=500, blank=True)
    alt_text = models.CharField(max_length=150, blank=True)
    color = models.CharField(max_length=32, blank=True, db_index=True)
    sort_order = models.PositiveSmallIntegerField(default=0, db_index=True)
    is_primary = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle", "sort_order"],
                name="unique_vehicle_image_sort_order",
            ),
            models.UniqueConstraint(
                fields=["vehicle"],
                condition=Q(is_primary=True),
                name="unique_primary_image_per_vehicle",
            ),
        ]
        indexes = [
            models.Index(fields=["vehicle", "is_primary", "sort_order"]),
            models.Index(fields=["vehicle", "color", "sort_order"]),
        ]

    def __str__(self):
        return f"Image {self.id} for {self.vehicle_id}"

    @property
    def resolved_image_url(self):
        if self.image:
            return self.image.url
        return self.image_external_url


class VehicleInquiry(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="inquiries",
        db_index=True,
    )
    full_name = models.CharField(max_length=120)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=25, blank=True, db_index=True)
    city = models.CharField(max_length=100, blank=True, db_index=True)
    dealer_location = models.CharField(max_length=150, blank=True, db_index=True)
    preferred_date = models.DateField(null=True, blank=True, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=InquiryStatus.choices,
        default=InquiryStatus.NEW,
        db_index=True,
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(
                condition=~Q(email=""),
                name="vehicle_inquiry_email_not_blank",
            ),
        ]
        indexes = [
            models.Index(fields=["vehicle", "status", "-created_at"]),
            models.Index(fields=["email", "status", "-created_at"]),
            models.Index(fields=["dealer_location", "status", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.full_name} -> {self.vehicle_id}"


class AuthorizedDealer(models.Model):
    dealer_name = models.CharField(max_length=150, db_index=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=25)
    city = models.CharField(max_length=100, db_index=True)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="authorized_dealers",
        db_index=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["dealer_name", "id"]
        indexes = [
            models.Index(fields=["brand", "city"]),
            models.Index(fields=["brand", "-created_at"]),
            models.Index(fields=["city", "dealer_name"]),
        ]

    def __str__(self):
        return f"{self.dealer_name} ({self.brand.name})"
