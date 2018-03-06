#!/bin/bash

clean=false
debug=false
while getopts cd opts; do
    case ${opts} in
        c) clean=true ;;
        d) debug=true ;;
       \?) echo "Usage: build -c -d" ;;
    esac
done

if $clean ; then
    rm -rf output
fi
python generate-conference-pages.py
cp -r public/* output
if $debug ; then
    open output/index.html
fi
