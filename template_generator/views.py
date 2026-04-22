from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from .services.template_service import TemplateService
from .services.render_service import RenderService
import json
from django.conf import settings
import os


class TemplateListView(APIView):
    def get(self, request):
        category = request.query_params.get('category')
        # Load from JSON for now
        template_file = os.path.join(settings.BASE_DIR, 'template_generator', 'templates_data', 'default_templates.json')
        with open(template_file, 'r') as f:
            templates = json.load(f)
        if category and category != 'all':
            templates = [t for t in templates if t['category'] == category]
        return Response(templates)


class TemplateDetailView(APIView):
    def get(self, request, template_id):
        template_file = os.path.join(settings.BASE_DIR, 'template_generator', 'templates_data', 'default_templates.json')
        with open(template_file, 'r') as f:
            templates = json.load(f)
        template = next((t for t in templates if t['id'] == template_id), None)
        if not template:
            return Response({'error': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(template)


class RenderTemplateView(APIView):
    def post(self, request):
        template_id = request.data.get('template_id')
        user_inputs = request.data.get('user_inputs', {})

        # Get template from JSON
        template_file = os.path.join(settings.BASE_DIR, 'template_generator', 'templates_data', 'default_templates.json')
        with open(template_file, 'r') as f:
            templates = json.load(f)
        template = next((t for t in templates if t['id'] == template_id), None)
        if not template:
            return Response({'error': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)

        # Render the image
        image_data = RenderService.render_template(template, user_inputs)

        # Return as HTTP response with image
        return HttpResponse(image_data, content_type='image/png')