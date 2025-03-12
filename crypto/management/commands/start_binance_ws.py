import json
import threading
from django.core.management.base import BaseCommand
from websocket import WebSocketApp
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from crypto.models import PriceUpdate

BINANCE_WS_URL = "wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@trade"


def on_message(ws, message):
    import json
    data = json.loads(message)

    # Для мультистрима Binance приходит {"stream": "btcusdt@trade", "data": {...}}
    stream = data.get("stream")       # "btcusdt@trade" или "ethusdt@trade"
    inner_data = data.get("data", {}) # внутри "data" уже лежит сделка

    symbol = inner_data.get("s")  # "BTCUSDT" или "ETHUSDT"
    price = inner_data.get("p")
    # Сохраняем в БД
    PriceUpdate.objects.create(symbol=symbol, price=price)
    # Рассылаем в группу
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "prices",
        {
            "type": "send_price_update",
            "data": {"symbol": symbol, "price": price},
        }
    )


def on_error(ws, error):
    print("WebSocket error:", error)

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    print("WebSocket connection opened")

class Command(BaseCommand):
    help = "Starts Binance WebSocket client."

    def handle(self, *args, **options):
        ws = WebSocketApp(
            BINANCE_WS_URL,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        wst = threading.Thread(target=ws.run_forever)
        wst.daemon = True
        wst.start()

        self.stdout.write(self.style.SUCCESS("Binance WebSocket client started. Press Ctrl+C to stop."))

        try:
            while True:
                pass
        except KeyboardInterrupt:
            ws.close()
            self.stdout.write(self.style.WARNING("Binance WebSocket client stopped."))
