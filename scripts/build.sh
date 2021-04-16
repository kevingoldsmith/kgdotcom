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
    cp public/.htaccess testoutput
else
    if $clean ; then
        rm -rf output
    fi
    mkdir output
    cp -r public/* output
    cp public/.htaccess output
fi
if ! $simple ; then
    if $debug ; then
        python generate_site.py --debug
    else        
        python generate_site.py
        python generate_sitemap.py
    fi
fi

if $debug ; then
    open testoutput/index.html
fi
