#!/bin/bash

echo "Building the project..."
pyinstaller qtquickdetect.py --add-data="cfg/ultralytics/default.yaml:ultralytics/cfg" --add-data "ressources:ressources" --noconfirm
echo "Build done."