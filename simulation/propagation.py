"""Lightweight 2D finite-difference acoustic simulator for soil.

The implementation avoids external dependencies so it can run in constrained
environments. It is intended for comparative studies of waveforms and soil
conditions rather than high-fidelity full-wave modeling.
"""
from __future__ import annotations

import math
import random
from typing import Dict, List, Tuple

from .config import RootTarget, Sensor, SimulationConfig, SimulationResult
from .waveforms import synthesize_waveform


Field = List[List[float]]


def _zeros(shape: Tuple[int, int], value: float = 0.0) -> Field:
    y, x = shape
    return [[float(value) for _ in range(x)] for _ in range(y)]


def _apply_targets(base: Field, targets: List[RootTarget], multiplier: str) -> Field:
    updated = [row[:] for row in base]
    for target in targets:
        ty, tx = target.center
        for y, row in enumerate(updated):
            for x, _ in enumerate(row):
                if (y - ty) ** 2 + (x - tx) ** 2 <= target.radius_cells ** 2:
                    scale = (
                        target.velocity_scale
                        if multiplier == "velocity"
                        else target.attenuation_scale
                    )
                    updated[y][x] *= scale
    return updated


def _laplacian(field: Field, dx: float) -> Field:
    y_max = len(field)
    x_max = len(field[0])
    lap = _zeros((y_max, x_max))
    for y in range(y_max):
        up = (y - 1) % y_max
        down = (y + 1) % y_max
        for x in range(x_max):
            left = (x - 1) % x_max
            right = (x + 1) % x_max
            lap[y][x] = (
                -4 * field[y][x]
                + field[up][x]
                + field[down][x]
                + field[y][left]
                + field[y][right]
            ) / (dx * dx)
    return lap


def _mul_fields(a: Field, scalar: float) -> Field:
    return [[val * scalar for val in row] for row in a]


def _add_fields(a: Field, b: Field) -> Field:
    return [[va + vb for va, vb in zip(row_a, row_b)] for row_a, row_b in zip(a, b)]


def _max_fields(a: Field, b: Field) -> Field:
    return [[max(va, vb) for va, vb in zip(row_a, row_b)] for row_a, row_b in zip(a, b)]


def simulate_run(config: SimulationConfig) -> SimulationResult:
    if config.random_seed is not None:
        random.seed(config.random_seed)

    waveform = synthesize_waveform(config.waveform)
    grid_y, grid_x = config.grid.size
    dx = config.grid.spacing_m
    dt = 1.0 / config.waveform.sample_rate_hz
    n_steps = len(waveform)

    velocity = _zeros((grid_y, grid_x), config.soil.velocity_m_per_s)
    attenuation = _zeros((grid_y, grid_x), config.soil.attenuation_np_per_m)
    velocity = _apply_targets(velocity, config.targets, multiplier="velocity")
    attenuation = _apply_targets(attenuation, config.targets, multiplier="attenuation")

    p_prev = _zeros((grid_y, grid_x))
    p_curr = _zeros((grid_y, grid_x))
    p_next = _zeros((grid_y, grid_x))

    receiver_traces: Dict[str, List[float]] = {rx.name: [0.0] * n_steps for rx in config.receivers}
    interference = _zeros((grid_y, grid_x)) if config.record_interference else None

    tx_y, tx_x = config.transmitter.position
    receiver_positions: List[Tuple[int, int]] = [rx.position for rx in config.receivers]

    c_dt_dx2 = _zeros((grid_y, grid_x))
    for y in range(grid_y):
        for x in range(grid_x):
            c_dt_dx2[y][x] = (velocity[y][x] * dt / dx) ** 2

    damping = config.damping

    for step in range(n_steps):
        lap = _laplacian(p_curr, dx)
        for y in range(grid_y):
            for x in range(grid_x):
                p_next[y][x] = (
                    (2 - damping) * p_curr[y][x]
                    - (1 - damping) * p_prev[y][x]
                    + c_dt_dx2[y][x] * lap[y][x]
                )
        p_next[tx_y][tx_x] += waveform[step]

        if interference is not None:
            for y in range(grid_y):
                for x in range(grid_x):
                    interference[y][x] = max(interference[y][x], abs(p_next[y][x]))

        for idx, (ry, rx) in enumerate(receiver_positions):
            name = config.receivers[idx].name
            receiver_traces[name][step] = p_next[ry][rx]

        p_prev, p_curr, p_next = p_curr, p_next, p_prev

    # Apply attenuation and sensor noise after propagation
    attenuation_factor: List[float] = []
    for ry, rx in receiver_positions:
        distance = math.hypot(ry - tx_y, rx - tx_x) * dx
        attenuation_factor.append(math.exp(-attenuation[tx_y][tx_x] * distance))

    for idx, name in enumerate(receiver_traces):
        trace = receiver_traces[name]
        receiver_traces[name] = [val * attenuation_factor[idx] + random.gauss(0.0, config.noise_std) for val in trace]

    times = [i * dt for i in range(n_steps)]
    metadata = {
        "dt_s": dt,
        "dx_m": dx,
        "waveform": config.waveform.kind,
        "frequency_hz": config.waveform.frequency_hz,
        "amplitude_v": config.waveform.amplitude_v,
        "moisture_fraction": config.soil.moisture_fraction,
        "damping": config.damping,
    }

    return SimulationResult(
        times_s=times,
        receiver_signals=receiver_traces,
        interference_map=interference,
        metadata=metadata,
    )
