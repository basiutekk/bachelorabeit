#!/bin/bash

frac_primal=0.2
edge_prob=$3

nmin_test=$1
nmax_test=$2

data_test=$HOME/data/dataset/rl_comb_opt/data/setcover/edge_prob-$edge_prob/nrange-$nmin_test-$nmax_test-n_graph-1000-p-$edge_prob-frac_primal-$frac_primal-seed-2.pkl

result_root=$HOME/scratch/results/rl_comb_opt/cpp_setcover/dqn

# max belief propagation iteration
max_bp_iter=5

# embedding size
embed_dim=64

# gpu card id
dev_id=$6

# max batch size for training/testing
batch_size=64

net_type=QNet

# set reg_hidden=0 to make a linear regression
reg_hidden=64

# learning rate
learning_rate=0.0001

# init weights with rand normal(0, w_scale)
w_scale=0.01

# nstep
n_step=2

min_n=$4
max_n=$5

num_env=10
mem_size=500000

max_iter=100000

# folder to save the trained model
save_dir=$result_root/embed-$embed_dim-nbp-$max_bp_iter-rh-$reg_hidden-primal-$frac_primal-ep-$edge_prob

if [ ! -e $save_dir ];
then
    mkdir -p $save_dir
fi

python evaluate.py \
    -dev_id $dev_id \
    -n_step $n_step \
    -data_test $data_test \
    -min_n $min_n \
    -max_n $max_n \
    -num_env $num_env \
    -max_iter $max_iter \
    -mem_size $mem_size \
    -learning_rate $learning_rate \
    -max_bp_iter $max_bp_iter \
    -net_type $net_type \
    -max_iter $max_iter \
    -save_dir $save_dir \
    -embed_dim $embed_dim \
    -batch_size $batch_size \
    -reg_hidden $reg_hidden \
    -momentum 0.9 \
    -l2 0.00 \
    -w_scale $w_scale
