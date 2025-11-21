# In-situ Plant Root and Rhizosphere Detection and Characterization

This repository captures the simulation design for an acoustic sensing system that characterizes plant roots and the surrounding rhizosphere without disturbing the soil. It builds on the Team S.O.I.L. architecture and incorporates remote sensing, waveform analysis, and spectral reconstruction to resolve roots, fungal tendrils, and other low-mass structures in mixed media.

- **Primary objective:** Define and run simulations that inform a deployable prototype for in-soil acoustic interrogation, with emphasis on interference pattern capture and spectral analysis.
- **Key sensors:**
  - Piezo Bending Element RPE-2.200-4106-NS1 (excitation and/or contact sensing)
  - Same Sky CUSA-TR80-18-2400-TH ultrasonic transmitter/receiver pair
  - LSM6DSO 3D accelerometer/gyro carrier (vibration monitoring)
- **Deliverable:** A simulation campaign (outlined in `docs/simulation-plan.md`) that spans parametric frequency/power sweeps, waveform variants, interference detection, and reconstruction methods (FFT-based spectral analysis and SIRT-informed tomography).

See `docs/simulation-plan.md` for the detailed workflow and parameter sets.

## Running virtual simulations
The repository now includes a lightweight Python simulator to explore waveform options, soil conditions, and synthetic root layouts entirely in software.

1. No external dependencies are required beyond the Python standard library.

2. Run a single simulation (sine, 1.5 kHz, 10 Vpp, default soil and receiver at `56,56`).
   ```bash
   python simulate.py --waveform sine --frequency 1500 --amplitude 10 --duration 0.01 --output outputs/sim_sine.json
   ```

3. Add a synthetic target and switch to a square wave for harmonic analysis.
   ```bash
   python simulate.py \
     --waveform square --frequency 5000 --amplitude 20 --duration 0.004 \
     --target root,32,32,4,0.9,1.3 --output outputs/sim_square_root.json
   ```

Results are saved as JSON containing the timebase, receiver traces, optional interference map, and metadata. Adjust `--target`, `--receivers`, `--chirp-end`, or `--noise-std` to sweep the matrix described in `docs/simulation-plan.md`.

## Beginner quickstart
If you are new to Python or command-line tools, follow the step-by-step walkthrough in [`docs/beginner-guide.md`](docs/beginner-guide.md). It covers:

- Checking your Python installation
- Running the simulator with copy-paste commands
- Inspecting the JSON output
- Troubleshooting the most common errors (missing Python, path issues, and permission errors)
