# store/urls.py

from django.urls import path

from .views import (
    StoreAPIView,
    ProductDetailAPIView
)
urlpatterns = [

    path(
        "",
        StoreAPIView.as_view(),
        name="store"
    ),

    path(
        "category/<slug:category_slug>/",
        StoreAPIView.as_view(),
        name="category_products"
    ),

    path(
        "product/<slug:category_slug>/<slug:product_slug>/",
        ProductDetailAPIView.as_view(),
        name="product_detail"
    ),

]