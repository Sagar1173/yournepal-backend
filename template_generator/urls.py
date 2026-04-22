from django.urls import path
from . import views

urlpatterns = [
    path('templates/', views.TemplateListView.as_view(), name='template-list'),
    path('templates/<str:template_id>/', views.TemplateDetailView.as_view(), name='template-detail'),
    path('render/', views.RenderTemplateView.as_view(), name='render-template'),
]