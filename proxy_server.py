#!/usr/bin/env python3
"""Cantus local dev server with Claude proxy endpoint.

Serves static files like `python -m http.server` and proxies:
POST /api/claude/messages -> https://api.anthropic.com/v1/messages

The browser sends API key via `x-cantus-api-key` (from app Settings), or you can
set ANTHROPIC_API_KEY in the shell to avoid browser key entry.
"""

from __future__ import annotations

import argparse
import json
import os
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


class CantusHandler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, anthropic-version, x-cantus-api-key")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        if self.path != "/api/claude/messages":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
            return
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, anthropic-version, x-cantus-api-key")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Max-Age", "600")
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/claude/messages":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": {"message": "Not found"}})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": {"message": "Invalid Content-Length"}})
            return

        raw_body = self.rfile.read(length)
        if not raw_body:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": {"message": "Missing request body"}})
            return

        api_key = self.headers.get("x-cantus-api-key", "").strip() or os.getenv("ANTHROPIC_API_KEY", "").strip()
        if not api_key:
            self._send_json(
                HTTPStatus.UNAUTHORIZED,
                {"error": {"message": "Missing API key. Set it in Cantus Settings or ANTHROPIC_API_KEY env var."}},
            )
            return

        anthropic_version = self.headers.get("anthropic-version", "2023-06-01")
        out_headers = {
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": anthropic_version,
        }

        req = Request(ANTHROPIC_URL, data=raw_body, headers=out_headers, method="POST")

        try:
            with urlopen(req, timeout=90) as resp:
                resp_body = resp.read()
                status = resp.status
                content_type = resp.headers.get("Content-Type", "application/json; charset=utf-8")
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(resp_body)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(resp_body)
        except HTTPError as e:
            err_body = e.read() or b""
            self.send_response(e.code)
            self.send_header("Content-Type", e.headers.get("Content-Type", "application/json; charset=utf-8"))
            self.send_header("Content-Length", str(len(err_body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            if err_body:
                self.wfile.write(err_body)
            else:
                self.wfile.write(json.dumps({"error": {"message": f"Upstream HTTP {e.code}"}}).encode("utf-8"))
        except URLError as e:
            self._send_json(HTTPStatus.BAD_GATEWAY, {"error": {"message": f"Upstream network error: {e.reason}"}})


def main() -> None:
    parser = argparse.ArgumentParser(description="Cantus dev server with Claude proxy")
    parser.add_argument("port", nargs="?", default=8080, type=int)
    parser.add_argument("--bind", default="0.0.0.0")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.bind, args.port), CantusHandler)
    print(f"Cantus proxy server running on http://{args.bind}:{args.port}")
    print("Proxy endpoint: /api/claude/messages")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
