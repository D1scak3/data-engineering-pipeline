#!/bin/bash

source ../env/bin/activate

bash port_forward.sh &

python3 ../src/cassandra/db_init.py -i localhost -p 9042 -k zenprice -s pickle_data -u pickle_data_unique -d pickle_results