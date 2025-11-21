# Beginner quickstart: running the soil acoustic simulator
This guide walks through every step to run the virtual experiments on a fresh computer. No prior Python experience is required.

## 1) Check your Python installation
The simulator only needs the standard library (no `pip install` required).

```bash
python --version
```
- If you see a version (e.g., `Python 3.10.12`), you are ready.
- If the command is not found, install Python 3.9+ from https://www.python.org/downloads/ and reopen your terminal.

> Tip: On macOS you might need to use `python3` instead of `python`. Replace `python` with `python3` in the commands below if needed.

## 2) Download or clone this repository
If you have Git installed:
```bash
git clone https://github.com/YOUR_ORG/Final-Project.git
cd Final-Project
```
Otherwise, download the ZIP from GitHub, unzip it, and open a terminal in the project folder.

## 3) Run a first simulation (copy-paste friendly)
This command generates a simple sine-wave test at 1.5 kHz and writes the results to `outputs/sim_sine.json`.
```bash
python simulate.py --waveform sine --frequency 1500 --amplitude 10 --duration 0.01 --output outputs/sim_sine.json
```
What you should see:
- A short pause while the solver runs
- A message like `Saved simulation to outputs/sim_sine.json`

## 4) Add a synthetic root target
To see how a buried object changes the signal, add a target and use a square wave to emphasize harmonics:
```bash
python simulate.py \
  --waveform square --frequency 5000 --amplitude 20 --duration 0.004 \
  --target root,32,32,4,0.9,1.3 --output outputs/sim_square_root.json
```
You can add multiple targets by repeating `--target ...` on the same command.

## 5) Inspect the output
Each run saves a JSON file. Open it with any text editor, or print the first few lines:
```bash
head -n 40 outputs/sim_square_root.json
```
Key fields:
- `times_s`: time stamps for each sample
- `receivers`: simulated voltage at each receiver (default `rx0` at grid position 56,56)
- `interference_map` (optional): a coarse view of wave interactions across the grid
- `metadata`: waveform and solver settings used for the run

## 6) Explore parameters
Use `--help` to see all options:
```bash
python simulate.py --help
```
Common tweaks:
- `--receivers 40,40 56,56` to record at multiple locations
- `--chirp-end 8000` to sweep from `--frequency` up to 8 kHz
- `--noise-std 0.001` to inject more measurement noise
- `--skip-interference` to speed up runs if you only need receiver traces

## 7) Troubleshooting
- **"python: command not found"**: Install Python 3.9+ and reopen the terminal.
- **"Permission denied" when saving**: Write to a folder you can access, e.g., `--output ./sim.json`.
- **"No such file or directory"**: Make sure you are inside the project folder (run `ls` to confirm files like `simulate.py` are visible).
- **Windows PowerShell quoting**: Use backticks for line continuation, e.g., replace `\` with `` ` `` if copying the multi-line command.

With these steps you can run every example in `docs/simulation-plan.md` without extra setup.
