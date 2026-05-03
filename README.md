# Multichannel ECG preprocessing pipeline
Removes spike artifacts, applies low-pass and notch filtering, and corrects baseline wander and DC offset.
After preprocessing, per-channel artifact counts and signal connectivity are reported, followed by a variance-based validation.

## Usage

### Shell script
Run the preprocessing pipeline and plot the resulting signals.

```bash
./run_pipeline.sh <input_file> <output_dir>
```

### Python scripts
The shell script executes both scripts sequentially. These can also be run independently as follows.

#### Preprocessing pipeline
```bash
python scripts/testing_pipeline.py --f <input_file> --out <output_dir>
```

##### Arguments
- `--f` : path to input `.mat` file containing `ecg` and optionally `fs` variables.
- `--out` : path to output directory where preprocessed signal will be saved.

#### Plotter function
Plot multichannel ECG signals.
```bash
python scripts/plotter.py --f <input_file>
```

##### Arguments
- `--f` : path to input `.mat` file containing `ecg` and optionally `fs` variables.

## Author
wpzamora97
