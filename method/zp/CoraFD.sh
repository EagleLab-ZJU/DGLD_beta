for data in Cora 
do
  for tau in 0.02 0.05 0.1 0.2 0.5 1.0 1.5 2.0
  do
    expname=$data'FDCoLAInfoNeg-Pos'$tau
    dataset=$data
    CUDA_VISIBLE_DEVICES=0 python main.py --dataset $dataset --tau $tau --batch_size 2048 --num_epoch 20  --logdir log/$expname > log/$expname.log 
    # nohup python main.py --dataset $dataset --logdir log/$expname > log/$expname.log 2>&1 &
  done
done
#Flikcr BlogCatalog Cora  Citeseer