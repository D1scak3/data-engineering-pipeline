#!/bin/bash

parallel time python3 manual_exporter.py -c exporter_conf.ini -f long_product_group_id_23 -t ::: "pickle-data" # "pickle-data" "pickle-data" "pickle-data" "pickle-data"