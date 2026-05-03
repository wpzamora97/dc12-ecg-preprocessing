#!/bin/bash

#@description: ECG Preprocessing Pipeline
#@usage: ./run_preprocessing.sh <input_file> <output_dir>
#@author: wpzamora97

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_file> <output_dir>"
    exit 1
fi

python scripts/processing_pipeline.py --f "$1" --out "$2"
