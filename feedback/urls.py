from django.urls import path

from .views import SuggestionCreateView


urlpatterns = [
    path("suggestions/", SuggestionCreateView.as_view(), name="suggestion-create"),
]

