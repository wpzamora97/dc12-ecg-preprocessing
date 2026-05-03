#!/bin/bash

#@description: ECG Preprocessing Pipeline
#@usage: ./run_preprocessing.sh <input_file> <output_dir>
#@author: wpzamora97

if  [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_file> <output_dir>"
    exit 1
fi
input_file="$1"
output_dir="$2"

filename="$(basename "$input_file")"
name="${filename%.*}"

python scripts/testing_pipeline.py --f "$input_file" --out "$output_dir" && \
python scripts/plotter.py --f "${output_dir}/${name}_preprocessed.mat"
