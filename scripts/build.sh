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
        python -m kgdotcom.cli --debug
    else        
        python -m kgdotcom.cli
        python -m kgdotcom.generators.sitemap
    fi
fi

if $debug ; then
    echo "Starting development server on http://localhost:8000"
    
    # Start server in testoutput directory
    (cd testoutput && exec python -m http.server 8000) &
    SERVER_PID=$!
    sleep 1
    open http://localhost:8000
    echo "Development server running (PID: $SERVER_PID)"
    echo "Press Ctrl+C to stop the server"
    
    # Function to cleanup server
    cleanup() {
        echo "Stopping development server..."
        # Kill the process group to ensure we get the Python process
        kill -TERM -$SERVER_PID 2>/dev/null || kill $SERVER_PID 2>/dev/null
        # Also kill any remaining http.server processes on port 8000
        pkill -f "http.server 8000" 2>/dev/null
        exit 0
    }
    
    # Trap signals to kill server
    trap cleanup SIGINT SIGTERM EXIT
    
    # Keep script running until interrupted
    while kill -0 $SERVER_PID 2>/dev/null; do
        sleep 1
    done
fi
