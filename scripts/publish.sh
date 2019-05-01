#!/bin/bash

pushd output
scp -rv $(pwd) ${SCP_DEST}
popd