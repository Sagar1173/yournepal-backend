from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="NewsCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(db_index=True, max_length=50, unique=True)),
                ("slug", models.SlugField(db_index=True, max_length=50, unique=True)),
            ],
            options={
                "ordering": ["name"],
                "indexes": [
                    models.Index(fields=["slug"], name="news_newsca_slug_5c0a14_idx"),
                    models.Index(fields=["name"], name="news_newsca_name_f13acd_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="News",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("summary", models.TextField(help_text="Short summary intended to stay around 40-80 words.")),
                ("image", models.URLField(blank=True, max_length=500)),
                ("source_url", models.URLField(blank=True, max_length=500)),
                (
                    "status",
                    models.CharField(
                        choices=[("draft", "Draft"), ("published", "Published")],
                        db_index=True,
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "category",
                    models.ForeignKey(
                        db_index=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="news_items",
                        to="news.newscategory",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at", "-id"],
                "indexes": [
                    models.Index(fields=["category", "status"], name="news_news_categor_caf58c_idx"),
                    models.Index(fields=["status", "created_at"], name="news_news_status_ce57ad_idx"),
                    models.Index(fields=["category", "created_at"], name="news_news_categor_457393_idx"),
                ],
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("status__in", ["draft", "published"])),
                        name="news_status_valid_choice",
                    ),
                    models.CheckConstraint(condition=models.Q(("title", ""), _negated=True), name="news_title_not_blank"),
                    models.CheckConstraint(condition=models.Q(("summary", ""), _negated=True), name="news_summary_not_blank"),
                ],
            },
        ),
    ]
