from django.db import models


class Template(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    category = models.CharField(max_length=50)
    data = models.JSONField()  # Store the template JSON structure
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.id}"