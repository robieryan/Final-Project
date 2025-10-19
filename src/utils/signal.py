"""Signal processing utilities for ECG preprocessing."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

import numpy as np
from scipy.signal import butter, filtfilt


@dataclass
class BandpassConfig:
    """Configuration for band-pass filtering.

    Attributes
    ----------
    lowcut: float
        Low cutoff frequency in Hz.
    highcut: float
        High cutoff frequency in Hz.
    order: int
        Order of the Butterworth filter.
    fs: float
        Sampling frequency of the signal in Hz.
    """

    lowcut: float = 0.5
    highcut: float = 40.0
    order: int = 4
    fs: float = 360.0


def bandpass_filter(signal: np.ndarray, config: BandpassConfig) -> np.ndarray:
    """Apply a Butterworth band-pass filter to the ECG signal.

    Parameters
    ----------
    signal:
        Raw ECG waveform with shape ``(n_samples,)`` or ``(n_leads, n_samples)``.
    config:
        Filter configuration with cutoff frequencies and sampling rate.

    Returns
    -------
    np.ndarray
        Filtered signal with the same shape as the input.
    """

    nyquist = 0.5 * config.fs
    low = config.lowcut / nyquist
    high = config.highcut / nyquist
    b, a = butter(config.order, [low, high], btype="band")

    if signal.ndim == 1:
        return filtfilt(b, a, signal)

    return np.vstack([filtfilt(b, a, lead) for lead in signal])


def segment_beats(
    signal: np.ndarray,
    annotations: Iterable[int],
    window_size: int,
) -> np.ndarray:
    """Segment ECG beats around provided annotations.

    Parameters
    ----------
    signal:
        The ECG signal (single lead) as a 1-D numpy array.
    annotations:
        Iterable of sample indices representing beat peaks.
    window_size:
        Number of samples to include in each segment. The window will span
        ``window_size`` samples centered at each annotation.

    Returns
    -------
    np.ndarray
        Array of shape ``(n_beats, window_size)`` containing segmented beats.
    """

    half_window = window_size // 2
    padded_signal = np.pad(signal, (half_window, half_window), mode="constant")
    segments = []
    for idx in annotations:
        start = idx
        end = idx + window_size
        segment = padded_signal[start : end]
        if len(segment) == window_size:
            segments.append(segment)
    if not segments:
        return np.empty((0, window_size))
    return np.stack(segments)


def normalize_segments(segments: np.ndarray) -> np.ndarray:
    """Standardize ECG segments per beat to zero mean and unit variance."""

    if segments.size == 0:
        return segments
    mean = segments.mean(axis=1, keepdims=True)
    std = segments.std(axis=1, keepdims=True) + 1e-8
    return (segments - mean) / std


def train_test_split(
    X: np.ndarray,
    y: np.ndarray,
    test_size: float = 0.2,
    seed: int | None = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Simple deterministic train/test split to avoid sklearn dependency."""

    rng = np.random.default_rng(seed)
    indices = np.arange(len(X))
    rng.shuffle(indices)
    split_idx = int(len(indices) * (1 - test_size))
    train_idx, test_idx = indices[:split_idx], indices[split_idx:]
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]
