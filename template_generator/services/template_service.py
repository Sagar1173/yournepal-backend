import json
import os
from django.conf import settings
from ..models import Template


class TemplateService:
    @staticmethod
    def load_default_templates():
        """Load templates from default_templates.json"""
        template_file = os.path.join(settings.BASE_DIR, 'template_generator', 'templates_data', 'default_templates.json')
        with open(template_file, 'r') as f:
            templates_data = json.load(f)
        return templates_data

    @staticmethod
    def get_templates_by_category(category=None):
        """Get templates, optionally filtered by category"""
        templates = Template.objects.all()
        if category:
            templates = templates.filter(category=category)
        return templates

    @staticmethod
    def get_template_by_id(template_id):
        """Get a specific template by ID"""
        try:
            return Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            return None