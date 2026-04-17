from django.urls import path

from .views import NewsViewSet

urlpatterns = [
    path("home/", NewsViewSet.as_view({"get": "home"}), name="news-home"),
    path("flash/", NewsViewSet.as_view({"get": "flash"}), name="news-flash"),
    path("nepal/", NewsViewSet.as_view({"get": "nepal"}), name="news-nepal"),
    path("international/", NewsViewSet.as_view({"get": "international"}), name="news-international"),
    path("<int:pk>/", NewsViewSet.as_view({"get": "retrieve"}), name="news-detail"),
]

