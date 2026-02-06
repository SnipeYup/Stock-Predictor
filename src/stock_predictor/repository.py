from __future__ import annotations

from datetime import datetime, timezone

from stock_predictor.db import connect
from stock_predictor.prediction import Prediction, predict

SEED_ASSETS = [
    ('AAPL', 'Apple Inc.', 'Technology', 'US'),
    ('MSFT', 'Microsoft', 'Technology', 'US'),
    ('NVDA', 'NVIDIA', 'Technology', 'US'),
    ('TSLA', 'Tesla', 'Automotive', 'US'),
    ('SHEL', 'Shell plc', 'Energy', 'UK'),
    ('TM', 'Toyota', 'Automotive', 'JP'),
]

SEED_NEWS = {
    'AAPL': [
        ('Apple beats earnings with growth in services', 'https://example.com/aapl-1', 'Reuters'),
        ('Analysts cite expansion and partnership momentum at Apple', 'https://example.com/aapl-2', 'Bloomberg'),
    ],
    'TSLA': [
        ('Tesla faces regulatory investigation in driver-assist probe', 'https://example.com/tsla-1', 'WSJ'),
        ('Tesla announces factory expansion in India', 'https://example.com/tsla-2', 'CNBC'),
    ],
}


def seed() -> None:
    with connect() as conn:
        exists = conn.execute('SELECT COUNT(*) AS c FROM assets').fetchone()['c']
        if exists > 0:
            return

        conn.executemany('INSERT INTO assets(ticker,name,sector,country) VALUES(?,?,?,?)', SEED_ASSETS)
        rows = []
        now = datetime.now(timezone.utc).isoformat()
        for ticker, articles in SEED_NEWS.items():
            for title, url, source in articles:
                rows.append((ticker, title, url, source, now))
        conn.executemany(
            'INSERT INTO news_articles(ticker,title,url,source,published_at) VALUES(?,?,?,?,?)',
            rows,
        )
        conn.commit()


def list_assets(sort_by: str = 'ticker') -> list[dict]:
    with connect() as conn:
        assets = conn.execute('SELECT ticker,name,sector,country FROM assets').fetchall()
        out = []
        for a in assets:
            pred = conn.execute(
                'SELECT expected_change_pct,confidence_pct,updated_at FROM predictions WHERE ticker=? AND timeframe=? ORDER BY id DESC LIMIT 1',
                (a['ticker'], 'days'),
            ).fetchone()
            out.append(
                {
                    'ticker': a['ticker'],
                    'name': a['name'],
                    'sector': a['sector'],
                    'country': a['country'],
                    'predicted': pred['expected_change_pct'] if pred else 0.0,
                    'confidence': pred['confidence_pct'] if pred else 0.0,
                    'updated_at': pred['updated_at'] if pred else None,
                }
            )

    if sort_by == 'predicted':
        out.sort(key=lambda x: x['predicted'], reverse=True)
    elif sort_by == 'confidence':
        out.sort(key=lambda x: x['confidence'], reverse=True)
    else:
        out.sort(key=lambda x: x['ticker'])
    return out


def get_or_add_asset(query: str) -> dict:
    token = query.strip().upper()
    with connect() as conn:
        row = conn.execute(
            'SELECT ticker,name FROM assets WHERE upper(ticker) LIKE ? OR upper(name) LIKE ? LIMIT 1',
            (f'%{token}%', f'%{token}%'),
        ).fetchone()
        if row:
            return {'ticker': row['ticker'], 'name': row['name'], 'added': False}

        ticker = token[:8]
        if not ticker:
            return {'ticker': '', 'name': '', 'added': False}

        conn.execute(
            'INSERT INTO assets(ticker,name,sector,country) VALUES(?,?,?,?)',
            (ticker, f'{ticker} (On-demand)', 'Unknown', 'Unknown'),
        )
        conn.execute(
            'INSERT INTO news_articles(ticker,title,url,source,published_at) VALUES(?,?,?,?,?)',
            (ticker, f'Insufficient coverage yet for {ticker}', 'https://example.com/on-demand', 'System', datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return {'ticker': ticker, 'name': f'{ticker} (On-demand)', 'added': True}


def run_prediction(ticker: str, timeframe: str) -> Prediction:
    with connect() as conn:
        titles = [
            r['title']
            for r in conn.execute('SELECT title FROM news_articles WHERE ticker=?', (ticker.upper(),)).fetchall()
        ]
        pred = predict(titles, timeframe)
        conn.execute(
            '''INSERT INTO predictions(
                ticker,timeframe,expected_change_pct,confidence_pct,rise_gt_7,rise_3_7,fall,reason,updated_at
            ) VALUES(?,?,?,?,?,?,?,?,?)''',
            (
                ticker.upper(),
                timeframe,
                pred.expected_change_pct,
                pred.confidence_pct,
                pred.rise_gt_7,
                pred.rise_3_7,
                pred.fall,
                pred.reason,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
    return pred


def detail(ticker: str, timeframe: str) -> dict:
    t = ticker.upper()
    with connect() as conn:
        asset = conn.execute('SELECT ticker,name,sector,country FROM assets WHERE ticker=?', (t,)).fetchone()
        if not asset:
            raise KeyError('Ticker not tracked')

        latest = conn.execute(
            'SELECT expected_change_pct,confidence_pct,rise_gt_7,rise_3_7,fall,reason,updated_at FROM predictions WHERE ticker=? AND timeframe=? ORDER BY id DESC LIMIT 1',
            (t, timeframe),
        ).fetchone()
        if not latest:
            run_prediction(t, timeframe)
            latest = conn.execute(
                'SELECT expected_change_pct,confidence_pct,rise_gt_7,rise_3_7,fall,reason,updated_at FROM predictions WHERE ticker=? AND timeframe=? ORDER BY id DESC LIMIT 1',
                (t, timeframe),
            ).fetchone()

        articles = conn.execute(
            'SELECT title,url,source,published_at FROM news_articles WHERE ticker=? ORDER BY id DESC',
            (t,),
        ).fetchall()

    return {
        'asset': dict(asset),
        'prediction': {
            'expected_change_pct': latest['expected_change_pct'],
            'confidence_pct': latest['confidence_pct'],
            'timeframe': timeframe,
            'distribution': {
                'rise_gt_7': latest['rise_gt_7'],
                'rise_3_7': latest['rise_3_7'],
                'fall': latest['fall'],
            },
            'reason': latest['reason'],
            'updated_at': latest['updated_at'],
        },
        'articles': [dict(x) for x in articles],
    }
