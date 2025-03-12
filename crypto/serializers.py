from rest_framework import serializers
from .models import PriceUpdate

class PriceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceUpdate
        fields = "__all__"
