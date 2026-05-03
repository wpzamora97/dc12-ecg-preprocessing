#@description: plotter
#@author: wpzamora97

import argparse
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot preprocessed ECG signal")
    parser.add_argument("--f", type=str, required=True, help="Path to preprocessed .mat file")

    # parse arguments
    args = parser.parse_args()
    path = Path(args.f)

    # load MATLAB struct
    mat_struct = loadmat(path)
    
    # read data
    signal = mat_struct['ecg']
    fs = mat_struct['fs']
    fs = int(np.squeeze(fs)) # convert to integer

    # ensure (channels, samples) orientation
    rows, cols = signal.shape
    if rows > cols:
        signal = signal.T

    # create time vector
    n_ch, n_samples = signal.shape
    t = np.arange(n_samples) / fs

    # render figure
    fig, axes = plt.subplots(n_ch, 1, figsize=(12,10), sharex=True)
    fig.suptitle(path.stem, fontsize=15, fontweight="bold")

    for index, (ax, ch) in enumerate(zip(axes, signal)):
        ax.plot(t, ch, 'k', lw=.75)
        ax.set_ylabel(f"Ch{index:02d}", rotation=90, labelpad=10, fontweight="bold")
        ax.set_yticks(ticks=[])
        # remove box around plots
        for spine in ax.spines.values():
            spine.set_visible(False)
        # remove x tick marks; except from last channel
        if index < n_ch - 1:
            ax.tick_params(bottom=False)

    axes[-1].set_xlabel("Time (s)")
    plt.tight_layout()
    plt.show()
