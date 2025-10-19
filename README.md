# ECG Arrhythmia Classification Platform

This project delivers an end-to-end workflow for building, training, and deploying a deep-learning
model that separates normal and arrhythmic heartbeats using the MIT-BIH Arrhythmia Database.
It includes:

- **Preprocessing pipeline** for converting PhysioNet `.dat`, `.hea`, and `.atr` files into
a clean beat-level dataset.
- **Lightweight 1-D CNN** training script with artifact export (model weights, metrics, dataset CSV).
- **Streamlit dashboard** that lets you upload MIT-BIH records, visualize beats, and obtain
live arrhythmia predictions.

## Project Structure

```
.
├── app.py                # Streamlit dashboard
├── data/                 # Place MIT-BIH records here (not tracked)
├── inference.py          # Helper utilities for loading models and running inference
├── requirements.txt      # Python dependencies
├── src/
│   ├── data_pipeline.py  # Data loading and preprocessing functions
│   ├── models/
│   │   └── cnn.py        # Compact 1-D CNN definition and training helpers
│   └── utils/
│       └── signal.py     # Signal processing utilities (filters, segmentation)
├── train.py              # End-to-end training entry point
└── artifacts/            # Training outputs (model, metrics, dataset exports)
```

## 1. Setup

1. **Create & activate a virtual environment** (recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux / macOS
   .venv\Scripts\activate     # Windows
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## 2. Download the MIT-BIH Arrhythmia Database

The dataset is available from [PhysioNet](https://physionet.org/content/mitdb/1.0.0/).
Download the `.dat`, `.hea`, and `.atr` files for the records you wish to use. Place them inside
`data/` (or any directory of your choice) preserving the original filenames, e.g.:

```
data/
├── 100.atr
├── 100.dat
├── 100.hea
├── 101.atr
└── ...
```

You can use the `wfdb` CLI for convenience:

```bash
pip install wfdb
wfdb fetch 100 101 103 105 106 108 109 112 114 115 -p mitdb -o data
```

## 3. Preprocess and Train the Model

Run the training script after downloading the records:

```bash
python train.py --data-dir data --records 100 101 103 105 106 108 109 112 114 115 --epochs 15
```

Key outputs (saved under `artifacts/` by default):

- `dataset.csv`: Beat-level dataset (first column is label, remaining columns are normalized samples).
- `summary.json`: Class distribution of the processed dataset.
- `history.joblib`: Training/validation loss and accuracy history.
- `ecg_cnn.pt`: Trained PyTorch checkpoint.
- `metrics.json`: Final validation metrics snapshot.

### Customization Tips

- Adjust `--window` to change the beat segment duration (default 0.66s).
- Choose a different lead with `--use-lead` (0 or 1).
- Provide your own record list via `--records`.
- Set `--output-dir` to store artifacts elsewhere.

## 4. Launch the Streamlit Dashboard

After training, start the dashboard:

```bash
streamlit run app.py
```

Inside the app:

1. Confirm the data directory (default `data/`).
2. Point to the trained model checkpoint (default `artifacts/ecg_cnn.pt`).
3. Pick a record and click **Run prediction** to visualize beats, predictions, and probability scores.

The dashboard displays:

- Predicted prevalence of arrhythmia vs normal beats.
- Interactive beat explorer with waveform plot and prediction details.
- Table of beat-level predictions and probabilities.

## 5. Evaluation & Reporting

- Validation metrics from training are stored in `artifacts/metrics.json`.
- Use the `history.joblib` file to plot learning curves in a notebook:

  ```python
  import joblib
  history = joblib.load("artifacts/history.joblib")
  ```

- Exported CSV files can feed additional analytics or classical ML baselines.

## 6. Next Steps & Stretch Ideas

- Integrate Grad-CAM or attention visualizations for explainability.
- Augment training with PTB-XL or noise injections to improve robustness.
- Deploy the Streamlit app to Hugging Face Spaces or Streamlit Community Cloud.
- Wrap the inference utilities in a FastAPI service for integration with other systems.

## License

This project builds on the MIT-BIH Arrhythmia Database, which has its own usage terms.
Ensure you comply with PhysioNet's credentialed access guidelines when downloading and using the data.
