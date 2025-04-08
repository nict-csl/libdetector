#!/bin/bash

rm -f *.csv

python3 parse_main.py model ../../sample_data/model ./model_s.list

python3 parse_main.py test ../../sample_data/test ./test_s.list

