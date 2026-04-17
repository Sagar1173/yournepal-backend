from django.db import migrations


def seed_categories(apps, schema_editor):
    NewsCategory = apps.get_model("news", "NewsCategory")
    categories = [
        ("Flash", "flash"),
        ("Nepal", "nepal"),
        ("International", "international"),
    ]

    for name, slug in categories:
        NewsCategory.objects.update_or_create(slug=slug, defaults={"name": name})


def unseed_categories(apps, schema_editor):
    NewsCategory = apps.get_model("news", "NewsCategory")
    NewsCategory.objects.filter(slug__in=["flash", "nepal", "international"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("news", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]

