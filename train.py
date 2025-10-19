"""End-to-end training pipeline for arrhythmia classification."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np

from src.data_pipeline import build_dataset, export_dataset_csv, save_summary, summarize_dataset
from src.models.cnn import TrainingConfig, save_model, train_model
from src.utils.signal import train_test_split


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train arrhythmia classifier from MIT-BIH dataset")
    parser.add_argument("--data-dir", type=Path, required=True, help="Directory with MIT-BIH records")
    parser.add_argument(
        "--records",
        nargs="*",
        default=["100", "101", "103", "105", "106", "108", "109", "112", "114", "115"],
        help="List of record numbers to use",
    )
    parser.add_argument("--window", type=float, default=0.66, help="Beat window size in seconds")
    parser.add_argument("--use-lead", type=int, default=0, help="Lead index to use from the record")
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts"), help="Directory to save artifacts")
    parser.add_argument("--epochs", type=int, default=20, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=256, help="Training batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument(
        "--test-size",
        type=float,
        default=0.2,
        help="Fraction of data reserved for validation",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed for dataset split")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    X, y = build_dataset(args.records, args.data_dir, window_seconds=args.window, use_lead=args.use_lead)
    summary = summarize_dataset(X, y)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    export_dataset_csv(X, y, output_dir / "dataset.csv")
    save_summary(summary, output_dir / "summary.json")

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=args.test_size, seed=args.seed)

    config = TrainingConfig(batch_size=args.batch_size, lr=args.lr, epochs=args.epochs)
    model, history = train_model(X_train, y_train, X_val, y_val, config)

    save_model(model, output_dir / "ecg_cnn.pt")
    joblib.dump(history, output_dir / "history.joblib")

    metrics = {
        "val_accuracy": history["val_acc"][-1],
        "val_loss": history["val_loss"][-1],
        "train_loss": history["train_loss"][-1],
        "class_distribution": summary,
    }
    with (output_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


if __name__ == "__main__":
    main()
