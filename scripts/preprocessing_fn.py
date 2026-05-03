#@description: preprocessing functions
#@author: wpzamora97

import numpy as np
from scipy.signal import butter, filtfilt, iirnotch
from scipy.ndimage import median_filter

def remove_spikes(signal:np.ndarray, fs:int|np.unsignedinteger=1000, mad_factor=10.0):
    """
    Remove high-amplitude spike artifacts from multichannel signals through MAD-based
    thresholding on the first-difference signal and linear interpolation over detected windows.

    Parameters
    ----------
    signal : np.ndarray
        Multichannel signal with shape (n_channels, n_samples)
    fs : int or np.unsignedinteger
        Sampling frequency in Hz. Default is 1000 Hz.
    mad_factor : float, optional
        MAD threshold multiplier. Higher values reduce sensitivity. Default is 10.0.

    Returns
    -------
    signal : np.ndarray
        Spike-free signal of shape (n_channels, n_samples); modified in-place.
        
    """
    # initialize report
    n_ch, _ = signal.shape
    report = np.zeros(n_ch, dtype=int)
    # first difference per channel: capture abrupt changes
    diff = np.diff(signal, prepend=signal[:,:1], axis=1)

    # compute MAD on the differential signal
    median = np.median(diff, axis=1, keepdims=True)
    mad    = np.median(np.abs(diff - median), axis=1, keepdims=True)
    # compute thresholding value
    threshold = mad_factor * mad / 0.6745
    
    # flag jumps
    discon = np.abs(diff - median) > threshold
    # max spike window length: considers each pair <'max_window' as flags for the same spike; 10 ms
    max_window = int(.01 * fs)

    # iterate over channels
    for index, (segm, d) in enumerate(zip(signal, discon)):
        # get flags indexes for current channel/segment
        flags = np.flatnonzero(d)
        # skip segments without spikes
        if flags.size <= 1: # it require at least one onset and one offset to form a window
            continue

        # split flags into windows
        splits, = np.where(np.diff(flags) > max_window)
        # build spikes windows as (onset, offset); windows with one flag are discarded
        windows = [
            win for win in np.split(flags, splits + 1) if win.size > 1
        ]
        # skip segments if flagged samples don;t fit within max window
        if not windows:
            continue
        # add number of peaks per channel to report
        report[index] = len(windows)

        # iterate over the spikes windows found
        for onset, offset, in windows:
            # fix the offset shift; 'np.diff' calculates sample 'n' as: x[n] - x[n-1]
            offset -= 1
            # anchor points for interpolation; use last clean sample before onset and first after offset
            anchors = [onset - 1, offset + 1]
            # interpolate in-place for current spike
            segm[onset:offset + 1] = np.interp(
                x=np.arange(onset, offset + 1), xp=np.asarray(anchors), fp=segm[anchors].flatten()
            )

    return signal, report

def preprocess_signal(signal:np.ndarray, fs:int|np.unsignedinteger=1000, lp_cutoff=40, notch_cutoff=50, eps=1e-6):
    """
    Preprocesses signals by applying bandpass and notch filtering to a multichannel signal.
    Baseline wander and DC offset are removed through a median filter cascade.

    Parameters
    ----------
    signal : np.ndarray
        Multichannel signal with shape (n_channels, n_samples).
    fs : int or np.unsignedinteger
        Sampling frequency in Hz. Default is 1000 Hz.
    lp_cutoff : float, optional
        Low-pass filter cutoff frequency in Hz. Default is 40 Hz.
    notch_cutoff : float, optional
        Notch filter frequency for powerline interference in Hz. Default is 50 Hz.
    eps : float, optional
        Variance threshold below which a channel is considered disconnected. Default is 1e-6.

    Returns
    -------
    signal : np.ndarray
        Filtered signal of shape (n_channels, n_samples).

    """
    # ensure 'fs' to be a single scalar
    fs = int(np.squeeze(fs))
    # detect connected channels; will be omitted from preprocessing to optimize computational performance
    connected = np.var(signal, axis=1) > eps
    
    # design low-pass filter; removes high-frequency noise, e.g. EMG interference, etc.
    b_lp, a_lp = butter(N=4, Wn=lp_cutoff, btype='low', fs=fs)
    # design notch filter; removes powerline interference, default for the european standard: 50 Hz
    b_n, a_n  = iirnotch(w0=notch_cutoff, Q=30, fs=fs)

    # window sizes for baseline estimation; 200ms removes QRS, 600ms removes T-wave
    win1 = int(0.2 * fs) | 1
    win2 = int(0.6 * fs) | 1

    # iterate over channels and filter
    for conn_flag, segm in zip(connected, signal):
        # skip disconnected channels
        if not conn_flag:
            continue
        # estimate and subtract baseline via median filter cascade
        baseline = median_filter(median_filter(segm, win1), win2)
        segm[:]  = segm - baseline
        # apply low-pass and notch filters over signals; 'filtfilt' applies the filter forward and backward to achieve zero-phase distortion
        segm[:] = filtfilt(b_lp, a_lp, segm)
        segm[:] = filtfilt(b_n,  a_n,  segm)

    return signal, connected
