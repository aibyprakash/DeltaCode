from __future__ import annotations

from dataclasses import asdict
from typing import Iterable

from .analysis import AnalysisResult, analyze_support_resistance
from .capital_client import CapitalApiClient, CapitalCredentials, Candle


class SupportResistanceBot:
    def __init__(self, client: CapitalApiClient | None = None):
        self.client = client or CapitalApiClient(CapitalCredentials.from_env())

    def fetch_candles(
        self,
        epic: str,
        resolution: str = "MINUTE",
        max_points: int = 200,
    ) -> Iterable[Candle]:
        return self.client.get_prices(epic=epic, resolution=resolution, max_points=max_points)

    def analyze(
        self,
        epic: str,
        resolution: str = "MINUTE",
        max_points: int = 200,
    ) -> AnalysisResult:
        candles = self.fetch_candles(epic, resolution=resolution, max_points=max_points)
        return analyze_support_resistance(candles)

    def analyze_payload(
        self,
        epic: str,
        resolution: str = "MINUTE",
        max_points: int = 200,
    ) -> dict:
        result = self.analyze(epic, resolution=resolution, max_points=max_points)
        return {
            "epic": epic,
            "zones": [asdict(zone) for zone in result.zones],
            "breakout": asdict(result.breakout),
            "trend": asdict(result.trend),
        }
