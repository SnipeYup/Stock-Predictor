import unittest

from stock_predictor.data_split import time_series_train_validation_split


class TimeSeriesSplitTests(unittest.TestCase):
    def test_preserves_order_and_uses_tail_for_validation(self):
        rows = ["d1", "d2", "d3", "d4", "d5"]
        split = time_series_train_validation_split(rows, validation_ratio=0.4)

        self.assertEqual(split.train, ["d1", "d2", "d3"])
        self.assertEqual(split.validation, ["d4", "d5"])

    def test_requires_enough_data(self):
        with self.assertRaises(ValueError):
            time_series_train_validation_split(["only-one"])

    def test_rejects_invalid_ratio(self):
        with self.assertRaises(ValueError):
            time_series_train_validation_split([1, 2, 3], validation_ratio=0)


if __name__ == "__main__":
    unittest.main()
