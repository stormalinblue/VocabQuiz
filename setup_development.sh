#!/usr/bin/bash

git config --local filter.strip-notebook-output.clean "\$PWD/venv/bin/python3 -m jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --to=notebook --stdin --stdout --log-level=ERROR"