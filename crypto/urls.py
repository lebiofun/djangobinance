from django.urls import path
from .views import PriceUpdateListAPIView

urlpatterns = [
    path('binance/', PriceUpdateListAPIView.as_view(), name='price-list'),
]
