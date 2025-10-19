"""Streamlit dashboard for ECG arrhythmia classification."""
from __future__ import annotations

from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import wfdb

from inference import predict_record
from src.data_pipeline import BEAT_LABEL_MAP, preprocess_record
from src.utils.signal import BandpassConfig

st.set_page_config(page_title="ECG Arrhythmia Classifier", layout="wide")


def list_records(data_dir: Path) -> List[str]:
    return sorted({path.stem for path in data_dir.glob("*.hea")})


def main() -> None:
    st.title("ECG Arrhythmia Classifier")
    st.sidebar.header("Dataset & Model")

    data_dir = Path(st.sidebar.text_input("MIT-BIH data directory", "data"))
    model_path = Path(st.sidebar.text_input("Model path", "artifacts/ecg_cnn.pt"))
    window = st.sidebar.slider("Window (s)", min_value=0.4, max_value=1.0, value=0.66, step=0.02)
    use_lead = st.sidebar.selectbox("Lead", options=[0, 1], index=0)

    if not data_dir.exists():
        st.warning("Data directory not found. Place MIT-BIH records in the specified folder.")
        return
    if not model_path.exists():
        st.warning("Model checkpoint not found. Train the model first using train.py.")
        return

    records = list_records(data_dir)
    if not records:
        st.warning("No records found in the data directory.")
        return

    record = st.selectbox("Select record", options=records)
    if st.button("Run prediction"):
        with st.spinner("Processing record..."):
            results = predict_record(
                record,
                data_dir=data_dir,
                model_path=model_path,
                window_seconds=window,
                use_lead=use_lead,
            )
        beats = results["beats"]
        true_labels = results["true_labels"]
        predicted_labels = results["predicted_labels"]
        probs = results["probabilities"]

        st.subheader("Prediction Summary")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Arrhythmia prevalence (predicted)",
                f"{(predicted_labels == 'arrhythmia').mean() * 100:.1f}%",
            )
        with col2:
            st.metric(
                "Normal prevalence (predicted)",
                f"{(predicted_labels == 'normal').mean() * 100:.1f}%",
            )

        st.subheader("Beat Explorer")
        beat_idx = st.slider("Beat index", min_value=0, max_value=len(beats) - 1, value=0)
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(beats[beat_idx], label="Normalized beat")
        ax.set_title(
            f"Predicted: {predicted_labels[beat_idx]} | True: {true_labels[beat_idx]}\n"
            f"Prob arrhythmia: {probs[beat_idx, 1]:.2f}"
        )
        ax.set_xlabel("Sample")
        ax.set_ylabel("Amplitude (normalized)")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

        st.subheader("Predictions Table")
        st.dataframe(
            {
                "beat_index": np.arange(len(beats)),
                "predicted": predicted_labels,
                "true": true_labels,
                "prob_normal": probs[:, 0],
                "prob_arrhythmia": probs[:, 1],
            }
        )


if __name__ == "__main__":
    main()
