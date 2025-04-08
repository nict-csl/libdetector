#!/bin/bash

cd script_parse
chmod a+x *.sh
./run_parse.sh

cd ../script_analysis/
chmod a+x *.sh
./run_analysis.sh






