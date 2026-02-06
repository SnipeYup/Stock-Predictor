from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / 'stock_predictor.sqlite3'


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            '''
            CREATE TABLE IF NOT EXISTS assets (
                ticker TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                sector TEXT NOT NULL,
                country TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                published_at TEXT NOT NULL,
                FOREIGN KEY (ticker) REFERENCES assets(ticker)
            );

            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                expected_change_pct REAL NOT NULL,
                confidence_pct REAL NOT NULL,
                rise_gt_7 REAL NOT NULL,
                rise_3_7 REAL NOT NULL,
                fall REAL NOT NULL,
                reason TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (ticker) REFERENCES assets(ticker)
            );
            '''
        )
        conn.commit()
