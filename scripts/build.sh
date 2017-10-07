#!/bin/bash

rm -rf talks
python generate-conference-pages.py
cp -r public/* talks
open talks/index.html
