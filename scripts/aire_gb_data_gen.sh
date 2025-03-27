#!/bin/bash
set -e # throws error if any command fails. otherwise would just keep going.

make final_data
make gb_scaled_data_summary
