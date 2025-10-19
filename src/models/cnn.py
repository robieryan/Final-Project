"""Lightweight 1-D CNN for arrhythmia classification."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


@dataclass
class TrainingConfig:
    batch_size: int = 256
    lr: float = 1e-3
    epochs: int = 20
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class ECGClassifier(nn.Module):
    def __init__(self, input_length: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(1, 16, kernel_size=7, padding=3),
            nn.BatchNorm1d(16),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(16, 32, kernel_size=5, padding=2),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.net(x)
        return self.classifier(x)


def _prepare_loader(X: np.ndarray, y: np.ndarray, batch_size: int, shuffle: bool = True) -> DataLoader:
    tensor_x = torch.from_numpy(X).float().unsqueeze(1)
    label_map = {"normal": 0, "arrhythmia": 1}
    tensor_y = torch.tensor([label_map[label] for label in y], dtype=torch.long)
    dataset = TensorDataset(tensor_x, tensor_y)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


def train_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    config: TrainingConfig,
) -> Tuple[ECGClassifier, dict]:
    device = torch.device(config.device)
    model = ECGClassifier(input_length=X_train.shape[1]).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=config.lr)

    train_loader = _prepare_loader(X_train, y_train, config.batch_size, shuffle=True)
    val_loader = _prepare_loader(X_val, y_val, config.batch_size, shuffle=False)

    history = {"train_loss": [], "val_loss": [], "val_acc": []}

    for epoch in range(config.epochs):
        model.train()
        running_loss = 0.0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * batch_x.size(0)
        epoch_loss = running_loss / len(train_loader.dataset)

        val_loss, val_correct, val_total = 0.0, 0, 0
        model.eval()
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                val_loss += loss.item() * batch_x.size(0)
                preds = outputs.argmax(dim=1)
                val_correct += (preds == batch_y).sum().item()
                val_total += batch_x.size(0)
        history["train_loss"].append(epoch_loss)
        history["val_loss"].append(val_loss / val_total)
        history["val_acc"].append(val_correct / val_total)

    return model, history


def save_model(model: ECGClassifier, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), path)


def load_model(path: Path, input_length: int, device: str | None = None) -> ECGClassifier:
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model = ECGClassifier(input_length=input_length)
    model.load_state_dict(torch.load(path, map_location=device))
    model.eval()
    return model
