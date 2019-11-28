#!/bin/bash

PYTHON_FILES="../src/runomatic.py"
PYTHON_FILES2="../src/stacks/*.py"
PO_FILE=runomatic/runomatic.pot
PO_FILE2=runoconfig/runoconfig.pot

mkdir -p runomatic/
mkdir -p runoconfig/

xgettext $PYTHON_FILES -o $PO_FILE
xgettext $PYTHON_FILES2 -o $PO_FILE2

