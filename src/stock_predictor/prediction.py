from __future__ import annotations

from dataclasses import dataclass

POSITIVE = {
    'beats': 1.8,
    'growth': 1.2,
    'approval': 1.5,
    'expansion': 1.1,
    'profit': 1.3,
    'partnership': 1.0,
}

NEGATIVE = {
    'lawsuit': -1.7,
    'investigation': -1.6,
    'downgrade': -1.4,
    'loss': -1.2,
    'recall': -1.5,
    'regulatory': -1.0,
}


@dataclass
class Prediction:
    expected_change_pct: float
    confidence_pct: float
    rise_gt_7: float
    rise_3_7: float
    fall: float
    reason: str


def _score(text: str) -> float:
    lower = text.lower()
    score = 0.0
    for key, value in POSITIVE.items():
        if key in lower:
            score += value
    for key, value in NEGATIVE.items():
        if key in lower:
            score += value
    return score


def predict(titles: list[str], timeframe: str) -> Prediction:
    if len(titles) < 2:
        return Prediction(0.0, 0.0, 0.0, 0.0, 0.0, '0% certainty – not enough data')

    score = sum(_score(t) for t in titles)
    multiplier = {'hours': 0.4, 'days': 1.0, 'weeks': 1.2, 'months': 1.35, 'years': 1.5}.get(timeframe, 1.0)
    expected = round(max(min(score * 0.85 * multiplier, 15), -15), 2)
    confidence = round(min(30 + len(titles) * 9 + abs(score) * 4, 95), 2)

    rise_gt_7 = max(min(20 + max(expected, 0) * 2.1, 85), 0)
    rise_3_7 = max(min(30 + max(expected, 0) * 1.2, 90 - rise_gt_7), 0)
    fall = round(max(100 - rise_gt_7 - rise_3_7, 1), 2)

    return Prediction(
        expected_change_pct=expected,
        confidence_pct=confidence,
        rise_gt_7=round(rise_gt_7, 2),
        rise_3_7=round(rise_3_7, 2),
        fall=fall,
        reason=f'Analyzed {len(titles)} linked articles. Weighted sentiment score: {score:.2f}.',
    )
