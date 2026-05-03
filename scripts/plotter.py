#@description: plotter
#@author: wpzamora97

import argparse, sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot preprocessed ECG signal")
    parser.add_argument("--f", type=str, required=True, help="Path to preprocessed .mat file")

    try:
        # parse arguments
        args = parser.parse_args()
        input_path = Path(args.f)

        # validate filepath and .mat extension
        if not input_path.is_file() or input_path.suffix.lower() != '.mat':
            raise FileNotFoundError("Invalid or non-existent .mat file")

        # load MATLAB struct
        mat_struct = loadmat(input_path)
        
        # validate required keys
        if not 'ecg' in mat_struct:
            raise KeyError("Missing 'ecg' in the .mat file")

        # read data
        signal = mat_struct['ecg']
        fs = np.squeeze(mat_struct['fs']) if 'fs' in mat_struct else 1000

        # ensure (channels, samples) orientation
        match signal.ndim:
            case 1: # handle 1D signals
                signal = signal[np.newaxis, :]
            case 2: # handle 2D signals
                rows, cols = signal.shape
                if rows > cols: 
                    signal = signal.T
            case _: # handle corrupt signals
                raise TypeError("ECG must be a 1D or 2D ndarray")

        # create time vector
        n_ch, n_samples = signal.shape
        t = np.arange(n_samples) / fs

        # render figure
        fig, axes = plt.subplots(n_ch, 1, sharex=True)
        fig.suptitle(input_path.stem, fontsize=15, fontweight="bold")

        for index, (ax, ch) in enumerate(zip(np.atleast_1d(axes), signal)):
            ax.plot(t, ch, 'k', lw=.75)
            ax.set_ylabel(f"Ch{index:02d}", rotation=90, labelpad=10, fontweight="bold")
            ax.set_yticks(ticks=[])
            # remove box around plots
            for spine in ax.spines.values():
                spine.set_visible(False)
            # remove x tick marks; except from last channel
            if index < n_ch - 1:
                ax.tick_params(bottom=False)

        np.atleast_1d(axes)[-1].set_xlabel("Time (s)")
        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"\n{type(e).__name__}: {e}\n")
        sys.exit(1)
