# Simulation Plan for Root and Rhizosphere Acoustic Sensing

## Goals
1. Demonstrate that a low-mass acoustic perturbation can be detected via interference patterns in soil.
2. Quantify resolution limits for root detection under realistic soil heterogeneity and moisture conditions.
3. Produce spectral signatures that can be reconstructed with FFT and Simultaneous Iterative Reconstruction Technique (SIRT).
4. De-risk a fieldable prototype that pairs soil probes with onboard inertial sensing and data acquisition.

## Sensors and Digital Twins
- **Piezo Bending Element RPE-2.200-4106-NS1**: Model as a broadband bender actuator and contact microphone. Include electromechanical coupling, plate bending stiffness, and soil contact impedance.
- **Same Sky CUSA-TR80-18-2400-TH ultrasonic Tx/Rx**: Model as matched 24 kHz resonant transducers with narrowband response; include beam directivity and insertion loss through soil.
- **LSM6DSO 3D accelerometer/gyro**: Model as a vibration monitor mounted near the actuator; capture soil/rod coupling and noise floor.
- **Headers and fixtures**: Represent probe spacing, mounting rods, and coupling media (e.g., gel or water injection) as boundary conditions affecting transmission loss.

## Simulation Environment
- Use a hybrid stack:
  - **k-Wave (MATLAB/Python)** or **FEniCS/FiPy** for time-domain wave propagation in heterogeneous soil volumes (include variable moisture, density, and grain size).
  - **Pyroomacoustics** for faster 2D parametric sweeps and interference pattern visualization.
  - **scikit-dsp-comm / SciPy** for waveform synthesis, FFT/STFT analysis, and matched filtering.
  - **Custom SIRT implementation** (NumPy) to reconstruct attenuation maps from multi-angle transmissions.

## Geometry and Media
- **Volume**: 0.6 m × 0.6 m × 0.6 m soil block with optional cylindrical boundary to mimic lysimeter.
- **Root models**: Parametric cylinders/tendrils (1–10 mm diameter) at variable depths (5–40 cm) with acoustic impedance 5–20% different from bulk soil.
- **Fungal hyphae**: Sub-mm filaments represented as line scatterers with very low acoustic contrast.
- **Soil heterogeneity**: Layered profiles and random inclusions (stones, voids) to challenge reconstruction.

## Excitation Waveforms
- **Base tones**: 1 kHz and 1.5 kHz (legacy) plus sweeps up to 24 kHz to align with ultrasonic Tx/Rx resonance.
- **Square waves**: 10–50% duty cycle to study harmonic content and soil attenuation of higher modes.
- **Linear chirps**: 500 Hz–24 kHz (1–10 ms) for matched-filter gain and interference richness.
- **Triangular pulses**: For controlled spectral roll-off when minimizing high-frequency attenuation.
- **Power levels**: 5–40 Vpp at the bender element; include amplifier clipping and soil heating checks.

## Simulation Matrix
- **Frequency × Power sweep**: (0.5, 1, 1.5, 5, 10, 15, 24 kHz) × (5, 10, 20, 30, 40 Vpp).
- **Waveform types**: sine, square, chirp, triangular.
- **Soil states**: dry (1–3% moisture), moist (8–15%), saturated (25–35%).
- **Root scenarios**: none (control), single root, branching root, root + hyphae, root near stone.
- **Sensor layouts**: two-probe linear (Tx/Rx), three-probe triangular for phase triangulation, ring of four around target.

## Data Products and Metrics
- **Interference maps**: Spatial pressure fields showing constructive/destructive regions; evaluate visibility of roots.
- **Spectral signatures**: FFT/STFT of received waveforms to capture notch/peak patterns caused by roots and hyphae.
- **Time-of-flight & group delay**: Estimate apparent velocity changes vs. soil-only baseline.
- **Attenuation profiles**: dB loss vs. path; map into SIRT to infer localized anomalies.
- **Reconstruction quality**: Structural similarity index (SSIM) and localization error (cm) between ground truth and SIRT output.

## Analysis Methods
- **Fourier analysis**: Extract harmonic content from square waves; identify spectral notches vs. frequency for root presence.
- **Matched filtering**: Use chirps to boost SNR; assess peak sharpness with and without roots.
- **Interference detection**: Simulate multi-probe phase differences; detect fringe spacing changes induced by roots or hyphae.
- **SIRT**: Ingest multi-angle attenuation and phase data; iterate until residual <5% or 200 iterations.
- **Noise modeling**: Add Gaussian electronic noise, coupling jitter, and soil movement artifacts sensed by the LSM6DSO.

## Validation Steps
1. **Baseline soil calibration**: Simulate empty soil block across all waveforms; record reference spectra and velocity.
2. **Single-root detection**: Introduce a 5 mm root at 20 cm depth; compare interference fringes and spectral notches.
3. **Hyphae sensitivity**: Add sub-mm scatterers; quantify detection limit vs. frequency and waveform.
4. **Layout comparison**: Run linear vs. triangular vs. ring probe configurations; select geometry with highest SSIM.
5. **Robustness**: Vary moisture and density; confirm that chirps + SIRT maintain detection under worst-case conditions.
6. **Prototype envelope**: Evaluate drive voltage and thermal load to ensure field hardware (amplifier + probes) can sustain repeated sweeps.

## Field Prototype Recommendations
- **Probe assembly**: Mount the RPE bender on a narrow stainless rod for soil insertion; pair with one or more CUSA-TR80 transducers at fixed spacing (10–20 cm). Use coupling gel from the ACL Staticide syringe to improve contact.
- **Sensing stack**: Log Tx drive, Rx voltage, and LSM6DSO vibrations on a microcontroller/SoC (e.g., Teensy or STM32) with synchronized timestamps.
- **Test script**: Cycle through waveform set (sine, square, chirp) and power levels; capture raw I/Q or time-series data per shot.
- **In-situ validation**: Deploy in the lysimeter with known buried targets (PVC root analogs and fine wires) to benchmark reconstruction.

## Outputs
- Simulation notebooks (Python/Matlab) that generate pressure fields, spectra, and SIRT reconstructions for each matrix entry.
- A summary report comparing waveform types and probe geometries, with recommendations for the field prototype configuration.
