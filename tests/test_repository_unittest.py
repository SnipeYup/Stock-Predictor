import unittest

from stock_predictor.db import init_db
from stock_predictor.repository import detail, list_assets, run_prediction, seed


class RepositoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed()

    def test_list_assets(self):
        rows = list_assets('ticker')
        self.assertGreaterEqual(len(rows), 1)

    def test_prediction_and_detail(self):
        p = run_prediction('AAPL', 'days')
        self.assertIsNotNone(p.expected_change_pct)
        d = detail('AAPL', 'days')
        self.assertIn('prediction', d)
        self.assertIn('articles', d)


if __name__ == '__main__':
    unittest.main()
