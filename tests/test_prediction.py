from stock_predictor.prediction import predict


def test_prediction_not_enough_data():
    result = predict(['one'], 'days')
    assert result.reason == '0% certainty – not enough data'
