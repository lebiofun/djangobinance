from django.test import TestCase
from unittest.mock import patch, MagicMock
from crypto.management.commands.start_binance_ws import on_message
from crypto.models import PriceUpdate

class BinanceWebSocketTest(TestCase):
    @patch("crypto.management.commands.start_binance_ws.logger")
    @patch("crypto.management.commands.start_binance_ws.get_channel_layer")
    def test_on_message_valid_data(self, mock_get_channel_layer, mock_logger):
        mock_layer = MagicMock()
        mock_get_channel_layer.return_value = mock_layer

        test_message = '{"stream": "btcusdt@trade", "data": {"s": "BTCUSDT", "p": "50000.00"}}'

        on_message(None, test_message)

        self.assertTrue(PriceUpdate.objects.filter(symbol="BTCUSDT", price="50000.00").exists())
        mock_logger.info.assert_called_with("получены данные: BTCUSDT - 50000.00")
        mock_layer.group_send.assert_called_once()

    @patch("crypto.management.commands.start_binance_ws.logger")
    def test_on_message_invalid_data(self, mock_logger):
        test_message = '{"stream": "btcusdt@trade", "data": {}}'

        on_message(None, test_message)

        self.assertFalse(PriceUpdate.objects.exists())
        mock_logger.warning.assert_called_with(
            "некорректный ответ от Binance: {'stream': 'btcusdt@trade', 'data': {}}")

    @patch("crypto.management.commands.start_binance_ws.logger")
    def test_on_message_exception_handling(self, mock_logger):
        test_message = 'invalid json'

        on_message(None, test_message)

        mock_logger.error.assert_called()
