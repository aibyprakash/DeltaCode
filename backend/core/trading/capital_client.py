from __future__ import annotations

import datetime as dt
import json
import os
from dataclasses import dataclass
from typing import Iterable
from urllib import parse, request


@dataclass(frozen=True)
class CapitalCredentials:
    api_key: str
    identifier: str
    password: str
    base_url: str = "https://api-capital.backend-capital.com"

    @classmethod
    def from_env(cls) -> "CapitalCredentials":
        return cls(
            api_key=os.environ["CAPITAL_API_KEY"],
            identifier=os.environ["CAPITAL_IDENTIFIER"],
            password=os.environ["CAPITAL_PASSWORD"],
            base_url=os.environ.get("CAPITAL_API_URL", cls.base_url),
        )


@dataclass
class CapitalSession:
    cst: str
    security_token: str
    expires_at: dt.datetime

    def is_expired(self) -> bool:
        return dt.datetime.now(dt.timezone.utc) >= self.expires_at


@dataclass(frozen=True)
class Candle:
    timestamp: dt.datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None


class CapitalApiClient:
    def __init__(self, credentials: CapitalCredentials):
        self.credentials = credentials
        self.session: CapitalSession | None = None

    def authenticate(self) -> CapitalSession:
        endpoint = f"{self.credentials.base_url}/api/v1/session"
        body = {
            "identifier": self.credentials.identifier,
            "password": self.credentials.password,
        }
        data = parse.urlencode(body).encode("utf-8")
        headers = {
            "X-CAP-API-KEY": self.credentials.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        req = request.Request(endpoint, data=data, headers=headers, method="POST")
        with request.urlopen(req) as response:
            cst = response.headers.get("CST")
            security_token = response.headers.get("X-SECURITY-TOKEN")

        if not cst or not security_token:
            raise RuntimeError("Capital.com authentication failed: missing session tokens.")

        expires_at = dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=6)
        self.session = CapitalSession(cst=cst, security_token=security_token, expires_at=expires_at)
        return self.session

    def _ensure_session(self) -> CapitalSession:
        if self.session is None or self.session.is_expired():
            return self.authenticate()
        return self.session

    def get_prices(
        self,
        epic: str,
        resolution: str = "MINUTE",
        max_points: int = 200,
    ) -> Iterable[Candle]:
        session = self._ensure_session()
        query = parse.urlencode({"resolution": resolution, "max": max_points})
        endpoint = f"{self.credentials.base_url}/api/v1/prices/{epic}?{query}"
        headers = {
            "X-CAP-API-KEY": self.credentials.api_key,
            "CST": session.cst,
            "X-SECURITY-TOKEN": session.security_token,
        }
        req = request.Request(endpoint, headers=headers, method="GET")
        with request.urlopen(req) as response:
            payload = response.read().decode("utf-8")

        data = json.loads(payload)
        prices = data.get("prices", [])
        candles: list[Candle] = []
        for price in prices:
            open_price = price["openPrice"]["bid"]
            close_price = price["closePrice"]["bid"]
            high_price = price["highPrice"]["bid"]
            low_price = price["lowPrice"]["bid"]
            snapshot_time = price.get("snapshotTimeUTC") or price.get("snapshotTime")
            if not snapshot_time:
                raise RuntimeError("Capital.com price payload missing snapshot time.")
            normalized_time = snapshot_time.replace("Z", "+00:00")
            timestamp = dt.datetime.fromisoformat(normalized_time)
            volume_value = price.get("lastTradedVolume")
            candles.append(
                Candle(
                    timestamp=timestamp,
                    open=float(open_price),
                    high=float(high_price),
                    low=float(low_price),
                    close=float(close_price),
                    volume=float(volume_value) if volume_value is not None else None,
                )
            )
        return candles
