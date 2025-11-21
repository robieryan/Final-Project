"""Configuration dataclasses for acoustic soil simulations.

These classes capture sensor placement, soil properties, waveform settings,
information about roots/hyphae, and numerical grid parameters.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class SoilProfile:
    """Bulk properties of the soil medium."""

    velocity_m_per_s: float = 320.0
    density_kg_per_m3: float = 1700.0
    attenuation_np_per_m: float = 1.2
    moisture_fraction: float = 0.12


@dataclass
class RootTarget:
    """Simple cylindrical or filament-like targets to perturb the field."""

    center: Tuple[int, int]
    radius_cells: int
    velocity_scale: float = 0.9
    attenuation_scale: float = 1.3
    label: str = "root"


@dataclass
class Sensor:
    """Represents a transmitter or receiver on the grid."""

    name: str
    position: Tuple[int, int]


@dataclass
class Waveform:
    """Defines excitation waveform parameters."""

    kind: str = "sine"  # sine, square, chirp, triangle
    frequency_hz: float = 1500.0
    amplitude_v: float = 10.0
    duration_s: float = 0.01
    sample_rate_hz: float = 48000.0
    chirp_end_hz: float | None = None
    duty_cycle: float = 0.5


@dataclass
class SimulationGrid:
    """Spatial discretization parameters."""

    size: Tuple[int, int] = (64, 64)
    spacing_m: float = 0.01


@dataclass
class SimulationConfig:
    """Aggregated configuration for an acoustic run."""

    soil: SoilProfile = field(default_factory=SoilProfile)
    grid: SimulationGrid = field(default_factory=SimulationGrid)
    waveform: Waveform = field(default_factory=Waveform)
    transmitter: Sensor = field(default_factory=lambda: Sensor("tx", (8, 8)))
    receivers: List[Sensor] = field(
        default_factory=lambda: [Sensor("rx0", (56, 56))]
    )
    targets: List[RootTarget] = field(default_factory=list)
    damping: float = 0.003
    noise_std: float = 0.0005
    random_seed: int | None = None
    record_interference: bool = True
    store_full_field: bool = False


@dataclass
class SimulationResult:
    """Outputs from a single simulation run."""

    times_s: List[float]
    receiver_signals: Dict[str, List[float]]
    interference_map: List[List[float]] | None
    metadata: Dict[str, float | str]

