from PIL import Image, ImageDraw, ImageFont
import io
import base64
from django.core.files.base import ContentFile


class RenderService:
    @staticmethod
    def render_template(template_data, user_inputs):
        """
        Render template with user inputs
        template_data: dict with background and elements
        user_inputs: dict with placeholders and values
        """
        # Load background image
        background_path = template_data.get('background')
        if background_path.startswith('/'):
            # Assume static files
            from django.contrib.staticfiles.storage import staticfiles_storage
            background = Image.open(staticfiles_storage.path(background_path[1:]))
        else:
            background = Image.open(background_path)

        # Create drawing context
        draw = ImageDraw.Draw(background)

        # Process elements
        for element in template_data.get('elements', []):
            if element['type'] == 'text':
                text = user_inputs.get(element.get('placeholder'), element.get('value', ''))
                font_size = element.get('fontSize', 24)
                x, y = element.get('x', 0), element.get('y', 0)
                # Use default font
                font = ImageFont.load_default()
                draw.text((x, y), text, fill='black', font=font)
            elif element['type'] == 'image':
                # For photo placeholder
                photo_data = user_inputs.get(element.get('placeholder'))
                if photo_data:
                    # Assume base64 encoded image
                    image_data = base64.b64decode(photo_data.split(',')[1])
                    photo = Image.open(io.BytesIO(image_data))
                    # Resize and position
                    width, height = element.get('width', 100), element.get('height', 100)
                    photo = photo.resize((width, height))
                    x, y = element.get('x', 0), element.get('y', 0)
                    background.paste(photo, (x, y))

        # Save to bytes
        output = io.BytesIO()
        background.save(output, format='PNG')
        output.seek(0)
        return output.getvalue()