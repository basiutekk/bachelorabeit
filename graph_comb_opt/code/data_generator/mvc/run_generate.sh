#!/bin/bash

min_n=15
max_n=20
gtype=erdos_renyi
p=0.5
m=4
output_root=../../../data/mvc

if [ ! -e $output_root ];
then
    mkdir -p $output_root
fi

python2 gen_graph_only.py \
    -save_dir $output_root \
    -max_n $max_n \
    -min_n $min_n \
    -num_graph 1000 \
    -p $p \
    -graph_type $gtype \
    -m $m
