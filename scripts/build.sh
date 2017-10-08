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
    rm -rf talks
fi
python generate-conference-pages.py
cp -r public/* talks
if $debug ; then
    open talks/index.html
fi
