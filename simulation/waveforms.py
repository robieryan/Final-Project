"""Waveform synthesis utilities for acoustic simulations."""
from __future__ import annotations

import math
from typing import List

from .config import Waveform


def synthesize_waveform(config: Waveform) -> List[float]:
    """Create a waveform list based on the configuration.

    Supports sine, square, linear chirp, and triangle waveforms. Returns a
    normalized waveform (peak amplitude in volts) sampled at the requested rate.
    """

    step = 1.0 / config.sample_rate_hz
    t_values = [i * step for i in range(int(config.duration_s * config.sample_rate_hz))]
    omega = 2 * math.pi * config.frequency_hz
    signal: List[float] = []

    if config.kind == "sine":
        signal = [math.sin(omega * t) for t in t_values]
    elif config.kind == "square":
        duty = min(max(config.duty_cycle, 0.05), 0.95)
        period = 1 / config.frequency_hz
        signal = [1.0 if (t % period) < duty * period else -1.0 for t in t_values]
    elif config.kind == "chirp":
        f1 = config.frequency_hz
        f2 = config.chirp_end_hz or config.frequency_hz * 2
        k = (f2 - f1) / max(config.duration_s, 1e-6)
        signal = [math.sin(2 * math.pi * (f1 * t + 0.5 * k * t * t)) for t in t_values]
    elif config.kind == "triangle":
        period = 1 / config.frequency_hz
        signal = [((t / period) % 1) for t in t_values]
        signal = [2 * abs(s - 0.5) * 2 - 1 for s in signal]
    else:
        raise ValueError(f"Unsupported waveform: {config.kind}")

    return [config.amplitude_v * s for s in signal]
