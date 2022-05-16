import numpy as np
import torch
import torch.optim as optim
from torch.utils.data.sampler import SubsetRandomSampler
from torch.utils.data import DataLoader
from dgl.dataloading import GraphDataLoader
from torch.utils.tensorboard import SummaryWriter

from DGLD.common.dataset import GraphNodeAnomalyDectionDataset
from DGLD.utils.utils import seed_everything
from .dataset import CoLADataSet
from .colautils import get_parse, train_epoch, test_epoch
from .model import CoLAModel

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
    # model optimizer loss
    model = CoLAModel(
        in_feats=dataset[0][0].ndata["feat"].shape[1],
        out_feats=args.embedding_dim,
        global_adg=args.global_adg,
    ).to(device)
    print(model)
    optimizer = optim.Adam(
        model.parameters(), lr=args.lr, weight_decay=args.weight_decay
    )
    criterion = torch.nn.BCEWithLogitsLoss()

    # train
    writer = SummaryWriter(log_dir=args.logdir)
    for epoch in range(args.num_epoch):
        train_loader.dataset.random_walk_sampling()
        loss_accum = train_epoch(
            epoch, args, train_loader, model, device, criterion, optimizer
        )
        writer.add_scalar("loss", float(loss_accum), epoch)
        predict_score = test_epoch(
            epoch, args, test_loader, model, device, criterion, optimizer
        )
        final_score, a_score, s_score = dataset.oraldataset.evalution(predict_score)
        writer.add_scalars(
            "auc",
            {"final": final_score, "structural": s_score, "attribute": a_score},
            epoch,
        )
        writer.flush()

    # multi-round test
    predict_score_arr = []
    for rnd in range(args.auc_test_rounds):
        test_loader.dataset.random_walk_sampling()
        predict_score = test_epoch(
            rnd, args, test_loader, model, device, criterion, optimizer
        )
        predict_score_arr.append(list(predict_score))

    predict_score_arr = np.array(predict_score_arr).T
    dataset.evaluation_multiround(predict_score_arr)
