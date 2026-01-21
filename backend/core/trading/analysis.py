from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable

from .capital_client import Candle


@dataclass(frozen=True)
class SupportResistanceZone:
    level: float
    zone_type: str
    strength: int


@dataclass(frozen=True)
class TrendSignal:
    trend: str
    reversal: bool
    description: str


@dataclass(frozen=True)
class BreakoutSignal:
    breakout: bool
    direction: str | None
    level: float | None


@dataclass(frozen=True)
class AnalysisResult:
    zones: list[SupportResistanceZone]
    breakout: BreakoutSignal
    trend: TrendSignal


def _average_true_range(candles: list[Candle], window: int = 14) -> float:
    if len(candles) < 2:
        return 0.0
    tr_values = []
    for i in range(1, len(candles)):
        high = candles[i].high
        low = candles[i].low
        prev_close = candles[i - 1].close
        tr_values.append(max(high - low, abs(high - prev_close), abs(low - prev_close)))
    if not tr_values:
        return 0.0
    windowed = tr_values[-window:]
    return mean(windowed)


def _pivot_levels(candles: list[Candle], pivot_window: int = 3) -> tuple[list[float], list[float]]:
    highs: list[float] = []
    lows: list[float] = []
    for idx in range(pivot_window, len(candles) - pivot_window):
        window = candles[idx - pivot_window : idx + pivot_window + 1]
        current = candles[idx]
        if current.high == max(candle.high for candle in window):
            highs.append(current.high)
        if current.low == min(candle.low for candle in window):
            lows.append(current.low)
    return highs, lows


def _cluster_levels(levels: Iterable[float], tolerance: float) -> list[float]:
    clusters: list[list[float]] = []
    for level in sorted(levels):
        matched = False
        for cluster in clusters:
            if abs(cluster[0] - level) <= tolerance:
                cluster.append(level)
                matched = True
                break
        if not matched:
            clusters.append([level])
    return [mean(cluster) for cluster in clusters]


def _moving_average(values: list[float], window: int) -> list[float]:
    if window <= 0:
        return []
    averages: list[float] = []
    for idx in range(window - 1, len(values)):
        averages.append(mean(values[idx - window + 1 : idx + 1]))
    return averages


def analyze_support_resistance(
    candles: Iterable[Candle],
    pivot_window: int = 3,
    zone_tolerance_factor: float = 0.6,
    breakout_buffer_factor: float = 0.25,
) -> AnalysisResult:
    candle_list = list(candles)
    if len(candle_list) < 10:
        return AnalysisResult(
            zones=[],
            breakout=BreakoutSignal(breakout=False, direction=None, level=None),
            trend=TrendSignal(trend="neutral", reversal=False, description="Insufficient data."),
        )

    atr = _average_true_range(candle_list)
    tolerance = max(atr * zone_tolerance_factor, 1e-6)
    high_levels, low_levels = _pivot_levels(candle_list, pivot_window=pivot_window)

    resistance_levels = _cluster_levels(high_levels, tolerance)
    support_levels = _cluster_levels(low_levels, tolerance)

    zones: list[SupportResistanceZone] = []
    for level in resistance_levels:
        strength = sum(abs(level - h) <= tolerance for h in high_levels)
        zones.append(SupportResistanceZone(level=level, zone_type="resistance", strength=strength))
    for level in support_levels:
        strength = sum(abs(level - l) <= tolerance for l in low_levels)
        zones.append(SupportResistanceZone(level=level, zone_type="support", strength=strength))

    zones.sort(key=lambda zone: (zone.zone_type, -zone.strength))

    latest = candle_list[-1]
    breakout = BreakoutSignal(breakout=False, direction=None, level=None)
    breakout_buffer = atr * breakout_buffer_factor
    if resistance_levels:
        nearest_resistance = max(resistance_levels)
        if latest.close > nearest_resistance + breakout_buffer:
            breakout = BreakoutSignal(breakout=True, direction="up", level=nearest_resistance)
    if support_levels:
        nearest_support = min(support_levels)
        if latest.close < nearest_support - breakout_buffer:
            breakout = BreakoutSignal(breakout=True, direction="down", level=nearest_support)

    closes = [candle.close for candle in candle_list]
    short_ma = _moving_average(closes, window=5)
    long_ma = _moving_average(closes, window=20)
    trend = "neutral"
    reversal = False
    description = ""
    if short_ma and long_ma:
        short_value = short_ma[-1]
        long_value = long_ma[-1]
        if short_value > long_value:
            trend = "uptrend"
        elif short_value < long_value:
            trend = "downtrend"
        if len(short_ma) > 1 and len(long_ma) > 1:
            prev_short = short_ma[-2]
            prev_long = long_ma[-2]
            if prev_short <= prev_long and short_value > long_value:
                reversal = True
                description = "Bullish moving-average crossover indicates potential reversal."
            elif prev_short >= prev_long and short_value < long_value:
                reversal = True
                description = "Bearish moving-average crossover indicates potential reversal."
    if not description:
        description = f"Trend is {trend}."

    return AnalysisResult(
        zones=zones,
        breakout=breakout,
        trend=TrendSignal(trend=trend, reversal=reversal, description=description),
    )
