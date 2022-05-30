import os
from os import path as osp
import torch.nn.functional as F
import joblib
import numpy as np
import pandas as pd
from tqdm import tqdm

import torch
import dgl
from dgl.data import DGLDataset
from dgl.nn.pytorch import EdgeWeightNorm

import sys 
sys.path.append('../../')
from common.dataset import GraphNodeAnomalyDectionDataset
from common.sample import CoLASubGraphSampling, UniformNeighborSampling
from common.utils import load_ACM

def safe_add_self_loop(g):
    newg = dgl.remove_self_loop(g)
    newg = dgl.add_self_loop(newg)
    return newg

class CoLADataSet(DGLDataset):
    def __init__(self, base_dataset_name='Cora', subgraphsize=4):
        super(CoLADataSet).__init__()
        self.dataset_name = base_dataset_name
        self.subgraphsize = subgraphsize
        # self.oraldataset = GraphNodeAnomalyDectionDataset(name=self.dataset_name)
        if self.dataset_name=='ACM':
            g=load_ACM()[0]
            self.oraldataset = GraphNodeAnomalyDectionDataset(name='custom',g_data=g,y_data=g.ndata['label'])
        else:
            self.oraldataset = GraphNodeAnomalyDectionDataset(name=self.dataset_name)

        self.dataset = self.oraldataset[0]
        self.colasubgraphsampler = CoLASubGraphSampling(length=self.subgraphsize)
        self.paces = []
        self.normalize_feat()
        self.random_walk_sampling()
    def normalize_feat(self):
        self.dataset.ndata['feat'] = F.normalize(self.dataset.ndata['feat'], p=1, dim=1)
        norm = EdgeWeightNorm(norm='both')
        self.dataset = safe_add_self_loop(self.dataset)
        norm_edge_weight = norm(self.dataset, edge_weight=torch.ones(self.dataset.num_edges()))
        self.dataset.edata['w'] = norm_edge_weight
        # print(norm_edge_weight)

    def random_walk_sampling(self):
        self.paces = self.colasubgraphsampler(self.dataset, list(range(self.dataset.num_nodes())))

    def graph_transform(self, g):
        newg = g
        return newg

    def __getitem__(self, i):
        pos_subgraph = self.graph_transform(dgl.node_subgraph(self.dataset, self.paces[i]))
        neg_idx = np.random.randint(self.dataset.num_nodes()) 
        while neg_idx == i:
            neg_idx = np.random.randint(self.dataset.num_nodes()) 
        neg_subgraph = self.graph_transform(dgl.node_subgraph(self.dataset, self.paces[neg_idx]))
        return pos_subgraph, neg_subgraph

    def __len__(self):
        return self.dataset.num_nodes()

    def process(self):
        pass

if __name__ == '__main__':
    dataset = CoLADataSet()
    ans = []
    for i in range(100):
        dataset.random_walk_sampling()
        ans.append(dataset[502][1].ndata[dgl.NID].numpy().tolist())
    print(set([str(t) for t in ans]))
