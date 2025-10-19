"""Data loading and preprocessing pipeline for the MIT-BIH Arrhythmia dataset."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd
import wfdb

from src.utils.signal import (
    BandpassConfig,
    bandpass_filter,
    normalize_segments,
    segment_beats,
)

# Mapping of MIT-BIH beat annotations to high-level categories.
BEAT_LABEL_MAP: Dict[str, str] = {
    "N": "normal",
    "L": "normal",
    "R": "normal",
    "e": "normal",
    "j": "normal",
    "A": "arrhythmia",
    "a": "arrhythmia",
    "J": "arrhythmia",
    "S": "arrhythmia",
    "V": "arrhythmia",
    "E": "arrhythmia",
    "F": "arrhythmia",
    "/": "arrhythmia",
    "f": "arrhythmia",
    "Q": "arrhythmia",
    "?": "arrhythmia",
}


class DatasetNotFoundError(FileNotFoundError):
    """Raised when a requested MIT-BIH record is not available locally."""


def _load_annotations(record: str, data_dir: Path) -> Tuple[np.ndarray, List[str]]:
    annotation = wfdb.rdann(str(data_dir / record), "atr")
    return annotation.sample, annotation.symbol


def _map_labels(symbols: Iterable[str]) -> np.ndarray:
    mapped = [BEAT_LABEL_MAP.get(sym, "arrhythmia") for sym in symbols]
    return np.array(mapped)


def load_record(record: str, data_dir: Path) -> Tuple[np.ndarray, int]:
    """Load a single MIT-BIH record and return the signal and sampling rate."""

    record_path = data_dir / record
    if not (record_path.with_suffix(".dat").exists() and record_path.with_suffix(".hea").exists()):
        raise DatasetNotFoundError(
            f"Missing files for record {record}. Ensure .dat, .hea, and .atr are downloaded."
        )

    wfdb_record = wfdb.rdrecord(str(record_path))
    signal = wfdb_record.p_signal.T  # leads x samples
    fs = wfdb_record.fs
    return signal, int(fs)


def preprocess_record(
    record: str,
    data_dir: Path,
    window_seconds: float = 0.66,
    bandpass: BandpassConfig | None = None,
    use_lead: int = 0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Preprocess a record into beat segments and labels."""

    signal, fs = load_record(record, data_dir)
    ann_samples, ann_symbols = _load_annotations(record, data_dir)

    if bandpass is None:
        bandpass = BandpassConfig(fs=fs)

    filtered = bandpass_filter(signal[use_lead], bandpass)
    window_size = int(window_seconds * fs)
    if window_size % 2 == 1:
        window_size += 1
    beats = segment_beats(filtered, ann_samples, window_size)
    beats = normalize_segments(beats)
    labels = _map_labels(ann_symbols[: len(beats)])
    return beats, labels


def build_dataset(
    records: Iterable[str],
    data_dir: Path,
    window_seconds: float = 0.66,
    bandpass: BandpassConfig | None = None,
    use_lead: int = 0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Aggregate beats from multiple records into a single dataset."""

    all_beats: List[np.ndarray] = []
    all_labels: List[np.ndarray] = []
    for record in records:
        beats, labels = preprocess_record(
            record,
            data_dir=data_dir,
            window_seconds=window_seconds,
            bandpass=bandpass,
            use_lead=use_lead,
        )
        all_beats.append(beats)
        all_labels.append(labels)
    if not all_beats:
        raise ValueError("No beats were extracted. Check the record list.")
    X = np.vstack(all_beats)
    y = np.concatenate(all_labels)
    return X, y


def export_dataset_csv(
    X: np.ndarray,
    y: np.ndarray,
    output_path: Path,
) -> None:
    """Export the processed dataset as a CSV file for downstream tasks."""

    df = pd.DataFrame(X)
    df.insert(0, "label", y)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def summarize_dataset(X: np.ndarray, y: np.ndarray) -> Dict[str, int]:
    """Return class counts for inspection and reporting."""

    unique, counts = np.unique(y, return_counts=True)
    return dict(zip(unique, counts))


def save_summary(summary: Dict[str, int], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
