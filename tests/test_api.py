import unittest
from urllib.request import urlopen
import json
import threading
import time

from stock_predictor.server import run


class ApiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.thread = threading.Thread(target=run, kwargs={'host': '127.0.0.1', 'port': 8010}, daemon=True)
        cls.thread.start()
        time.sleep(0.5)

    def test_stocks_endpoint(self):
        data = json.loads(urlopen('http://127.0.0.1:8010/stocks').read().decode('utf-8'))
        self.assertIsInstance(data, list)


if __name__ == '__main__':
    unittest.main()
