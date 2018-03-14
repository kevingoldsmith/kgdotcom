#!/bin/bash

clean=false
debug=false
simple=false
writing=false
while getopts cdsw opts; do
    case ${opts} in
        c) clean=true ;;
        d) debug=true ;;
        s) simple=true ;;
        w) writing=true ;;
        *) echo "Usage: build -c -d -s -w" 
           exit 1;;
    esac
done

if $clean ; then
    rm -rf output
fi
if ! $simple ; then
    if ! $writing ; then
        python generate-conference-pages.py
    fi
    python generate-writing-page.py
fi
cp -r public/* output
if $debug ; then
    if ! $writing ; then
        open output/index.html
    else
        open output/writing.html
    fi
fi
