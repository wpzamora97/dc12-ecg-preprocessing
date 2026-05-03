#@description: runs and tests the ECG preprocessing functions
#@author: wpzamora97

import argparse, sys, time
import numpy as np
from pathlib import Path
from scipy.io import loadmat, savemat
from preprocessing_fn import remove_spikes, preprocess_signal

#%% PIPELINE

if __name__ == "__main__":
    # setup parser
    parser = argparse.ArgumentParser(description="Runs and tests ECG preprocessing")
    parser.add_argument("--f", type=str, required=True, help="Input ECG signal file path")
    parser.add_argument("--out", type=str, required=True, help="Output directory to save preprocessed signal")

    print("\nSTARTING ECG PREPROCESSING PIPELINE...")

    try:
        # parse arguments
        args = parser.parse_args()
        input_path = Path(args.f)

        # validate filepath and .mat extension
        if not input_path.is_file() or input_path.suffix.lower() != '.mat':
            raise FileNotFoundError("Invalid or non-existent .mat file")

        # load MATLAB struct
        mat_struct = loadmat(file_name=input_path, struct_as_record=False)

        # validate required keys
        if not 'ecg' in mat_struct:
            raise KeyError("Missing 'ecg' in the .mat file")

        # read data
        raw_ecg = mat_struct['ecg']
        fs =  mat_struct['fs'] if 'fs' in mat_struct else None

        # validate data types
        # scipy.io.loadmat converts MATLAB matrices to NumPy ndarrays by default
        # therefore, MATLAB's double types will be read as np.float64, and integers as np.uint*
        if raw_ecg.dtype != np.float64:
            raise TypeError("ECG must be a float64 ndarray")
        if fs is not None and not np.issubdtype(fs.dtype, np.unsignedinteger):
            raise TypeError("Fs must be an unsigned integer")
        
        # handle 1D signals; expand it to (1, samples)
        if raw_ecg.ndim == 1:
            raw_ecg = raw_ecg[np.newaxis, :]
        # handle 2D signals; ensure (channels, samples) orientation
        elif raw_ecg.ndim == 2:
            # transpose when unambiguous; sample dimension is always assumed to be the largest
            # square matrices remain unchanged
            rows, cols = raw_ecg.shape
            if rows > cols:
                raw_ecg = raw_ecg.T
        # anything beyond 2D is considered corrupt
        else:
            raise TypeError("ECG must be a 1D or 2D ndarray")

        # keep a copy of raw for validation metrics
        raw_copy = raw_ecg.copy()

        # define start time
        runtime = time.perf_counter()

        # preprocessing pipeline: fs will only be passed if it is not None
        processed_signal, spikes = remove_spikes(raw_ecg, **{'fs': fs} if fs is not None else {})
        processed_signal, connected = preprocess_signal(processed_signal, **{'fs': fs} if fs is not None else {})

        # runtime
        runtime = time.perf_counter() - runtime

        # get output signal dimension
        n_ch, n_samples = processed_signal.shape
        # precompute overall testing metrics
        metrics = {
            "v_raw" : [], "v_out" : []
        }
        for raw, out in zip(raw_copy, processed_signal):
            metrics["v_raw"].append(np.var(raw))
            metrics["v_out"].append(np.var(out))

        # save preprocessed signal
        out_path = Path(args.out)
        out_path.mkdir(parents=True, exist_ok=True) # ensure output dir existence
        out_path = out_path / (input_path.stem + "_preprocessed.mat")
        # save preprocessed signal as .mat
        savemat(file_name=out_path, mdict={'ecg': processed_signal, 'fs': fs if fs is not None else 1000})
        print(f"\nOUTPUT PATH: {out_path}")
        
        # general report
        print(
        f"\nRUNTIME : {runtime:.4f}s                 \n"
        f"\nOUTPUT SHAPE : {processed_signal.shape}  \n"
        f"\nPREPROCESSING REPORT                       "
        f"\n────────────────────────────────────────── "
        f"\n" + "\n".join(f"Ch{ch:02d} : {n} spike(s) removed | {'connected' if is_conn else 'disconnected'}" for ch, (n, is_conn) in enumerate(zip(spikes, connected)))
        )
        # overall testing metrics report
        print(
        f"\nOVERALL VALIDATION METRICS                 "
        f"\n────────────────────────────────────────── "
        f"\n{'':<4}{'VAR_RAW':>10}{'VAR_OUT':>10}{'RESULTS':>13}"
        f"\n" + "\n".join(f"Ch{ch:02d}{metrics['v_raw'][ch]:>10.2e}{metrics['v_out'][ch]:>10.2e}{'TEST PASSED' if metrics['v_out'][ch] < metrics['v_raw'][ch] else 'TEST FAILED':>13}" for ch, is_conn in enumerate(connected) if is_conn)
        )
        print("\nPIPELINE COMPLETED\n")

    except Exception as e:
        print(f"\n{type(e).__name__}: {e}\n")
        sys.exit(1)
