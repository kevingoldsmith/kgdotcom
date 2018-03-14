#!/bin/bash

clean=false
debug=false
simple=false
while getopts cds opts; do
    case ${opts} in
        c) clean=true ;;
        d) debug=true ;;
        s) simple=true ;;
        *) echo "Usage: build -c -d -s" 
           exit 1;;
    esac
done

if $clean ; then
    rm -rf output
fi
if ! $simple ; then
	python generate-conference-pages.py
	python generate-writing-page.py
fi
cp -r public/* output
if $debug ; then
    open output/index.html
fi
