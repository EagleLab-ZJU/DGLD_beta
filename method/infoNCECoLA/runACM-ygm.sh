expname=acm_info_raw_bs4096_exp1
dataset=ACM

if [ ! -d log  ];then
  mkdir log
  echo mkdir log
else
  echo dir exist
fi
 CUDA_VISIBLE_DEVICES=1 nohup python main.py --num_epoch 100 --batch_size 4096 --dataset $dataset > log/$expname.log 2>&1 &
# nohup python main.py --dataset $dataset --logdir log/$expname > log/$expname.log 2>&1 &
