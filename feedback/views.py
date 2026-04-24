from rest_framework import generics

from .models import Suggestion
from .serializers import SuggestionSerializer


class SuggestionCreateView(generics.CreateAPIView):
    queryset = Suggestion.objects.only("id", "suggestion_text", "created_at")
    serializer_class = SuggestionSerializer

