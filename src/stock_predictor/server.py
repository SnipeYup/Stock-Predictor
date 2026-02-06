from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from stock_predictor.db import init_db
from stock_predictor.repository import detail, get_or_add_asset, list_assets, run_prediction, seed

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / 'web'


class Handler(BaseHTTPRequestHandler):
    def _json(self, payload: dict | list, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status.value)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _html(self, html: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = html.encode('utf-8')
        self.send_response(status.value)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == '/':
            return self._html((WEB / 'index.html').read_text())

        if parsed.path == '/stocks':
            sort_by = params.get('sort_by', ['ticker'])[0]
            return self._json(list_assets(sort_by=sort_by))

        if parsed.path.startswith('/stocks/'):
            ticker = parsed.path.split('/')[-1]
            timeframe = params.get('timeframe', ['days'])[0]
            try:
                return self._json(detail(ticker, timeframe))
            except KeyError:
                return self._json({'error': 'Ticker not tracked'}, HTTPStatus.NOT_FOUND)

        if parsed.path == '/search':
            query = params.get('query', [''])[0]
            result = get_or_add_asset(query)
            return self._json({'matches': [{'ticker': result['ticker'], 'name': result['name']}], 'added': result['added']})

        return self._json({'error': 'Not found'}, HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path.startswith('/predict/'):
            ticker = parsed.path.split('/')[-1]
            timeframe = params.get('timeframe', ['days'])[0]
            pred = run_prediction(ticker, timeframe)
            return self._json(
                {
                    'ticker': ticker.upper(),
                    'timeframe': timeframe,
                    'expected_change_pct': pred.expected_change_pct,
                    'confidence_pct': pred.confidence_pct,
                    'distribution': {
                        'rise_gt_7': pred.rise_gt_7,
                        'rise_3_7': pred.rise_3_7,
                        'fall': pred.fall,
                    },
                    'reason': pred.reason,
                }
            )

        return self._json({'error': 'Not found'}, HTTPStatus.NOT_FOUND)


def run(host: str = '0.0.0.0', port: int = 8000) -> None:
    init_db()
    seed()
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f'Server running on http://{host}:{port}')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
