#!/bin/bash
set -e # throws error if any command fails. otherwise would just keep going.

make data
make transitions_default
make manchester_scaled_data
make synthetic_manchester_repl
