from django.db import models


class Suggestion(models.Model):
    suggestion_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.suggestion_text[:60]

