import numpy as np
import torch
import torch.optim as optim
from torch.utils.data.sampler import SubsetRandomSampler
from torch.utils.data import DataLoader
from dgl.dataloading import GraphDataLoader
from torch.utils.tensorboard import SummaryWriter
import sys
sys.path.append("../../")

from common.dataset import GraphNodeAnomalyDectionDataset
from utils.utils import seed_everything
from utils.print import lcprint, cprint

from dataset import CoLADataSet
from colautils import get_parse, train_epoch, test_epoch, train_model, multi_round_test, get_staticpseudolabel, get_staticpseudolabel_mask
from model import CoLAModel
def print_mean_std(arr, descript='.'):
    print(descript, f":{round(np.mean(arr)*100,2)}({round(np.var(arr)*100, 2)})")
if __name__ == "__main__":
    args = get_parse()
    seed_everything(args.seed)
    print(args)
    if torch.cuda.is_available():
        device = torch.device("cuda:" + str(args.device))
    else:
        device = torch.device("cpu")
    # dataset
    dataset = CoLADataSet(args.dataset)
    train_loader = GraphDataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        drop_last=False,
        shuffle=True,
    )
    test_loader = GraphDataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        drop_last=False,
        shuffle=False,
    )
    from test_csv import ExpRecord
    exprecord = ExpRecord("alpha.csv")
    tau_map = {
        "Cora":0.6,
        "Citeseer":1.5,
        "Pubmed":0.2,
        "BlogCatalog":1.5,
        "Flickr":2.0,
        "ACM":0.2,
        "ogbn-arxiv":0.2,
    }
    for alpha in [0, 0.1, 0.2, 0.3, 0.5, 0.6, 0.8, 0.9, 1.0]:
        args.tau = tau_map[args.dataset]
        print(args.tau)
        args.alpha = alpha
        # model optimizer loss
        model = CoLAModel(
            in_feats=dataset[0][0].ndata["feat"].shape[1],
            out_feats=args.embedding_dim,
            global_adg=args.global_adg,
            tau=args.tau,
            alpha=args.alpha,
            generative_loss_w=args.generative_loss_w,
            score_type=args.score_type,
            loss_type=args.loss_type
        ).to(device)
        print(model)
        
        # train
        writer = SummaryWriter(log_dir=args.logdir)

        cprint("training", color='info')
        train_model(model, args, train_loader, test_loader, writer, device, pseudo_label_type='none')
        cprint("after training===> multi-round test", color='info')
        # multi-round test to create pseudo label
        final_score, a_score, s_score = multi_round_test(args, test_loader, model, device)
        cprint("self labeling", color='info')
        args_dict = vars(args)
        args_dict["auc"] = final_score
        args_dict["attribute_auc"] = a_score
        args_dict["structure_auc"] = s_score
        exprecord.add_record(args_dict)


        
        