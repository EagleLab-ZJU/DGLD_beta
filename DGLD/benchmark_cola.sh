batch=300
for data in Cora Citeseer Pubmed ogbn-arxiv ACM Flickr Blog
do
  expname=$data'CoLA'
  dataset=$data
  CUDA_VISIBLE_DEVICES=4 python main_cola.py --dataset $dataset --device 0 --batch_size $batch --logdir log/$expname > log/$expname.log 2>&1 &
done
