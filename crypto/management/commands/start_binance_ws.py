import threading
import json
import logging
import time
from django.core.management.base import BaseCommand
from websocket import WebSocketApp
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from crypto.models import PriceUpdate

logger = logging.getLogger("binance_logger")

BINANCE_WS_URL = "wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@trade"

def on_message(ws, message):
    try:
        data = json.loads(message)
        stream = data.get("stream")
        inner_data = data.get("data", {})

        symbol = inner_data.get("s")
        price = inner_data.get("p")

        if symbol and price:
            logger.info(f"Стрим: {stream} | Получены данные: {symbol} - {price}")

            PriceUpdate.objects.create(symbol=symbol, price=price)

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "prices",
                {
                    "type": "send_price_update",
                    "data": {"symbol": symbol, "price": price},
                }
            )
        else:
            logger.warning(f"Стрим: {stream} | Некорректный ответ от Binance: {data}")

    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)

def on_error(ws, error):
    logger.error(f"WebSocket ошибка: {error}", exc_info=True)

def on_close(ws, close_status_code, close_msg):
    logger.warning(f"WebSocket закрыт. Код: {close_status_code}, Причина: {close_msg}")

def on_open(ws):
    logger.info("WebSocket соединение открыто.")

class Command(BaseCommand):
    help = "Starts Binance WebSocket client."

    def handle(self, *args, **options):
        logger.info("Запуск Binance WebSocket клиента...")

        ws = WebSocketApp(
            BINANCE_WS_URL,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )

        wst = threading.Thread(target=ws.run_forever, daemon=True)
        wst.start()

        self.stdout.write(self.style.SUCCESS("Binance WebSocket клиент запущен. Нажмите Ctrl+C для остановки."))

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.warning("Остановка WebSocket клиента...")
            ws.close()
            self.stdout.write(self.style.WARNING("Binance WebSocket клиент остановлен."))
