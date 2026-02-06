import unittest

from stock_predictor.prediction import predict


class PredictionTests(unittest.TestCase):
    def test_not_enough_data(self):
        result = predict(['single'], 'days')
        self.assertEqual(result.confidence_pct, 0.0)
        self.assertEqual(result.reason, '0% certainty – not enough data')

    def test_positive_signal(self):
        result = predict([
            'Company beats earnings with growth and profit',
            'Analysts note expansion and partnership approval',
        ], 'days')
        self.assertGreater(result.expected_change_pct, 0)
        self.assertGreater(result.confidence_pct, 0)


if __name__ == '__main__':
    unittest.main()
