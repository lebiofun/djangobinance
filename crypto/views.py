from rest_framework import generics
from .models import PriceUpdate
from .serializers import PriceUpdateSerializer
from django.shortcuts import render


class PriceUpdateListAPIView(generics.ListAPIView):
    serializer_class = PriceUpdateSerializer

    def get_queryset(self):
        queryset = PriceUpdate.objects.all().order_by("-timestamp")
        symbol = self.request.query_params.get("symbol")
        if symbol:
            queryset = queryset.filter(symbol=symbol)
        return queryset

class PriceUpdateListAPIView(generics.ListAPIView):
    queryset = PriceUpdate.objects.all().order_by("-timestamp")
    serializer_class = PriceUpdateSerializer

def home(request):
    return render(request, 'home.html')