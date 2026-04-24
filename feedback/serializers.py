from rest_framework import serializers

from .models import Suggestion


class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = ["id", "suggestion_text", "created_at"]
        read_only_fields = ["id", "created_at"]

