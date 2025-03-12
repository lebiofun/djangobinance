from django.db import models

class PriceUpdate(models.Model):
    symbol = models.CharField(max_length=20)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} - {self.price} at {self.timestamp}"
