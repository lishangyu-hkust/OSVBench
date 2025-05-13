#!/bin/bash

SECONDS=0
# Pass down the specification results obtained from invoking LLMs.
docker build --build-arg SPEC_TO_RUN="$1" --tag "local_osv" .
docker run -v </path/to/>OSVBench/outputs:/root/hyperkernel/outputs --rm local_osv $1
echo "Time elapsed for specification correctness checking: $SECONDS s"

