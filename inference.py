"""Utilities for running inference with a trained ECG classifier."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import joblib
import numpy as np
import torch

from src.data_pipeline import BEAT_LABEL_MAP, preprocess_record
from src.models.cnn import ECGClassifier, load_model
from src.utils.signal import BandpassConfig, normalize_segments

LABEL_MAP_INV = {0: "normal", 1: "arrhythmia"}


def load_history(path: Path) -> Dict[str, list]:
    return joblib.load(path)


def predict_record(
    record: str,
    data_dir: Path,
    model_path: Path,
    window_seconds: float = 0.66,
    use_lead: int = 0,
) -> Dict[str, np.ndarray]:
    beats, labels = preprocess_record(
        record,
        data_dir=data_dir,
        window_seconds=window_seconds,
        bandpass=BandpassConfig(),
        use_lead=use_lead,
    )
    input_length = beats.shape[1]
    model = load_model(model_path, input_length=input_length)

    with torch.no_grad():
        tensor = torch.from_numpy(beats).float().unsqueeze(1)
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1).numpy()
        preds = probs.argmax(axis=1)

    predicted_labels = np.vectorize(LABEL_MAP_INV.get)(preds)
    return {
        "beats": beats,
        "true_labels": labels,
        "predicted_labels": predicted_labels,
        "probabilities": probs,
    }
