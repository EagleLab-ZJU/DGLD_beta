expname=cora_info_bs4096_aug_exp1
dataset=Cora

if [ ! -d log  ];then
  mkdir log
  echo mkdir log
else
  echo dir exist
fi
 CUDA_VISIBLE_DEVICES=1 nohup python main.py --num_epoch 100 --batch_size 4096 --dataset $dataset --logdir log/$expname > log/$expname.log 2>&1 &
# nohup python main.py --dataset $dataset --logdir log/$expname > log/$expname.log 2>&1 &
# CUDA_VISIBLE_DEVICES=1 nohup python main.py --num_epoch 100 --batch_size 4096 --dataset Cora > log/cora_info_bs4096_aug_exp2.log 2>&1 &
# CUDA_VISIBLE_DEVICES=1 nohup python main.py --num_epoch 100 --batch_size 4096 --dataset Cora --aug_type node_shuffle  > log/cora_info_bs4096_aug_exp3.log 2>&1 &
# CUDA_VISIBLE_DEVICES=1 nohup python main.py --num_epoch 100 --batch_size 4096 --dataset Cora --aug_type random_mask --aug_ratio 0.5  > log/cora_info_bs4096_aug_exp4.log 2>&1 &
# CUDA_VISIBLE_DEVICES=1 nohup python main.py --num_epoch 100 --batch_size 4096 --dataset Cora --aug_type random_mask --aug_ratio 0.2  > log/cora_info_bs4096_aug_exp5.log 2>&1 &