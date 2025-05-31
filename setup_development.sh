#!/usr/bin/bash

git config --global filter.strip-notebook-output.clean "echo $pwd; ./venv/bin/python3 -m jupyter nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --to=notebook --stdin --stdout --log-level=ERROR"
