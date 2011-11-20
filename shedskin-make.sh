#!/bin/bash

if ! `python -mshedskin`; then
    echo install shedskin
fi
shedskin -e Final.py && make
echo DONE, now run multiple_runs.py
