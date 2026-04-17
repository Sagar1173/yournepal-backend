from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .pagination import NewsPagination
from .serializers import FlashNewsSerializer, NewsDetailSerializer, NewsListSerializer
from .services import NewsQueryService


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsQueryService.detail_queryset()
    pagination_class = NewsPagination

    def get_queryset(self):
        if self.action == "flash":
            return NewsQueryService.flash_queryset(limit=5)
        if self.action == "nepal":
            return NewsQueryService.category_queryset("nepal")
        if self.action == "international":
            return NewsQueryService.category_queryset("international")
        return NewsQueryService.detail_queryset()

    def get_serializer_class(self):
        if self.action == "flash":
            return FlashNewsSerializer
        if self.action in {"nepal", "international"}:
            return NewsListSerializer
        return NewsDetailSerializer

    @action(detail=False, methods=["get"], url_path="home", pagination_class=None)
    def home(self, request, *args, **kwargs):
        payload = NewsQueryService.home_payload()
        return Response(
            {
                "flash_news": FlashNewsSerializer(payload["flash_news"], many=True).data,
                "nepal_news": NewsListSerializer(payload["nepal_news"], many=True).data,
                "international_news": NewsListSerializer(payload["international_news"], many=True).data,
            }
        )

    @action(detail=False, methods=["get"], url_path="flash", pagination_class=None)
    def flash(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="nepal")
    def nepal(self, request, *args, **kwargs):
        return self._paginated_category_response()

    @action(detail=False, methods=["get"], url_path="international")
    def international(self, request, *args, **kwargs):
        return self._paginated_category_response()

    def _paginated_category_response(self):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

