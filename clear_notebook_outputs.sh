#!/bin/bash

# Find all Jupyter Notebook files in subdirectories
notebooks=$(find "$(pwd)" -name "*.ipynb")

# Loop through each notebook and clear outputs, normalize, and handle missing ID field warning
for notebook in $notebooks; do
    jupyter nbconvert --clear-output --inplace "$notebook"
    jupyter nbconvert --to notebook --clear-output --inplace --output "$notebook" "$notebook"
done

echo "Cleared outputs, normalized, and handled missing ID field warning for all Jupyter Notebooks in subdirectories."
