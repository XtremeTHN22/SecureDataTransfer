#!/bin/bash

echo Creating virtual env...
if [ -d .venv ]; then
    echo Skipping virtual env creation.
else
    python3 -m venv .venv
    source .venv/bin/activate
    echo Successfully created virtual env.
fi
echo Installing dependencies...
pip install -r requirements.txt