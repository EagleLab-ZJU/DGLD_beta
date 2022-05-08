for data in Cora Citeseer Pubmed
do
  for tau in 0.5 0.3
  do
    expname=$data'bs4096loss_log()_divide_n_as_scoreinfoCoLA_=tau'$tau
    dataset=$data
    CUDA_VISIBLE_DEVICES=3 python main.py --tau $tau --reinit True --dataset $dataset --keep_ratio 0.95 --batch_size 4096 --logdir log/$expname > log/$expname.log 
    # nohup python main.py --dataset $dataset --logdir log/$expname > log/$expname.log 2>&1 &
  done
done
