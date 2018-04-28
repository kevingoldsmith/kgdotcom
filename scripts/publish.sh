#!/bin/bash

pushd output
scp -rv . $SCP_DEST
popd