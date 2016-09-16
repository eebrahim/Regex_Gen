#!/bin/sh
gprof $1 | python gprof2dot.py -s | dot -Tpng -o profiling.png
