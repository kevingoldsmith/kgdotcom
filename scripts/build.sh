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
        *) echo "Usage: build -c -d -s"
           exit 1;;
    esac
done

if $debug ; then
    if $clean ; then
        rm -rf testoutput
    fi
    mkdir testoutput
    cp -r public/* testoutput
else
    if $clean ; then
        rm -rf output
    fi
    mkdir output
    cp -r public/* output
fi
if ! $simple ; then
    if $debug ; then
        python generate-conference-pages.py --debug
        python generate-writing-page.py --debug
        python generate-other-pages.py --debug
    else        
        python generate-conference-pages.py
        python generate-writing-page.py
        python generate-other-pages.py
    fi
fi

if $debug ; then
    open testoutput/index.html
fi
