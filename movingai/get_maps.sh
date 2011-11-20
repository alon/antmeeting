#!/bin/bash

ROOT=http://www.movingai.com/benchmarks/dao
for m in den501d den312d den020d brc202d lak304d; do
    if [ ! -e $m.jpg]; then
        wget $ROOT/$m.jpg
    fi
    if [ -e $m.map ]; then
        continue
    fi
    if [ ! -e $m.zip ]; then
        wget $ROOT/$m.zip
    fi
    unzip $m.zip
done
