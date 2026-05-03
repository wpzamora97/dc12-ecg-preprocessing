# ECG Preprocessing Pipeline
Preprocessing pipeline for multichannel ECG signals.
Removes spike artifacts, applies low-pass and notch filtering, and removes baseline wander and DC offset.

## Usage

### Shell script
```bash
./scripts/run_pipeline.sh <input_file> <output_dir>
```

### Python
```bash
python scripts/processing_pipeline.py --f <input_file> --out <output_dir>
```

## Arguments
- `--f`   : path to input `.mat` file containing `ecg` and `fs` variables.
- `--out` : path to output directory where preprocessed signal will be saved.

## Plotter
Visualizes multichannel ECG signals.
Works on both raw and preprocessed files.

### Python
```bash
python scripts/plotter.py --f <input_file>
```

### Arguments
- `--f` : path to `.mat` file containing `ecg` and `fs` variables.

## Author
wpzamora97
