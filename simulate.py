"""Command-line entry point for running virtual acoustic soil simulations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from simulation.config import RootTarget, Sensor, SimulationConfig, Waveform
from simulation.propagation import simulate_run


def _parse_targets(specs: List[str]):
    targets: List[RootTarget] = []
    for spec in specs:
        # Format: label,y,x,radius,velocity_scale,attenuation_scale
        parts = spec.split(",")
        if len(parts) != 6:
            raise ValueError(
                "Targets must be label,y,x,radius_cells,velocity_scale,attenuation_scale"
            )
        label, y, x, radius, vscale, ascale = parts
        targets.append(
            RootTarget(
                center=(int(y), int(x)),
                radius_cells=int(radius),
                velocity_scale=float(vscale),
                attenuation_scale=float(ascale),
                label=label,
            )
        )
    return targets


def build_config(args: argparse.Namespace) -> SimulationConfig:
    waveform = Waveform(
        kind=args.waveform,
        frequency_hz=args.frequency,
        amplitude_v=args.amplitude,
        duration_s=args.duration,
        sample_rate_hz=args.sample_rate,
        chirp_end_hz=args.chirp_end,
        duty_cycle=args.duty_cycle,
    )

    receivers = [Sensor(name=f"rx{i}", position=tuple(map(int, pos.split(",")))) for i, pos in enumerate(args.receivers)]
    targets = _parse_targets(args.target) if args.target else []

    return SimulationConfig(
        waveform=waveform,
        receivers=receivers,
        targets=targets,
        damping=args.damping,
        noise_std=args.noise_std,
        record_interference=not args.skip_interference,
        random_seed=args.seed,
    )


def save_result(result_path: Path, result) -> None:
    result_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "times_s": result.times_s,
        "receivers": result.receiver_signals,
        "metadata": result.metadata,
    }
    if result.interference_map is not None:
        payload["interference_map"] = result.interference_map
    result_path.write_text(json.dumps(payload, indent=2))



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run virtual soil acoustic simulations without hardware.")
    parser.add_argument("--waveform", choices=["sine", "square", "chirp", "triangle"], default="sine")
    parser.add_argument("--frequency", type=float, default=1500.0, help="Base frequency in Hz")
    parser.add_argument("--chirp-end", type=float, default=None, help="End frequency for chirp")
    parser.add_argument("--amplitude", type=float, default=10.0, help="Drive amplitude in volts")
    parser.add_argument("--duration", type=float, default=0.01, help="Duration in seconds")
    parser.add_argument("--sample-rate", type=float, default=48000.0, help="Sample rate in Hz")
    parser.add_argument(
        "--receivers",
        nargs="+",
        default=["56,56"],
        help="Receiver positions as 'y,x' grid indices.",
    )
    parser.add_argument(
        "--target",
        action="append",
        help="Add a target in the form label,y,x,radius_cells,velocity_scale,attenuation_scale",
    )
    parser.add_argument("--damping", type=float, default=0.003, help="Damping factor for the solver")
    parser.add_argument("--noise-std", type=float, default=0.0005, help="Gaussian noise level")
    parser.add_argument("--duty-cycle", type=float, default=0.5, help="Duty cycle for square waveforms")
    parser.add_argument("--skip-interference", action="store_true", help="Skip interference map computation")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for repeatability")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/simulation.json"),
        help="Path to save JSON results",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = build_config(args)
    result = simulate_run(config)
    save_result(args.output, result)
    print(f"Saved simulation to {args.output}")


if __name__ == "__main__":
    main()
