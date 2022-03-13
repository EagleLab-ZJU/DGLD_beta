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
from common.sample import CoLASubGraphSampling

def safe_add_self_loop(g):
    newg = dgl.remove_self_loop(g)
    newg = dgl.add_self_loop(newg)
    return newg

class CoLADataSet(DGLDataset):
    def __init__(self, base_dataset_name='Cora', subgraphsize=4):
        super(CoLADataSet).__init__()
        self.dataset_name = base_dataset_name
        self.subgraphsize = subgraphsize
        self.oraldataset = GraphNodeAnomalyDectionDataset(name=self.dataset_name)
        self.dataset = self.oraldataset[0]
        self.colasubgraphsampler = CoLASubGraphSampling(length=self.subgraphsize)
        self.paces = []
        self.random_walk_sampling()
        self.normalize_feat()
    def normalize_feat(self):
        self.dataset.ndata['feat'] = F.normalize(self.dataset.ndata['feat'], p=1, dim=1)
        norm = EdgeWeightNorm(norm='both')
        self.dataset = safe_add_self_loop(self.dataset)
        norm_edge_weight = norm(self.dataset, edge_weight=torch.ones(self.dataset.num_edges()))
        self.dataset.edata['w'] = norm_edge_weight
        print(norm_edge_weight)

    def random_walk_sampling(self):
        self.paces = self.colasubgraphsampler(self.dataset, list(range(self.dataset.num_nodes())))

    def graph_transform(self, g):
        newg = safe_add_self_loop(g)
        # add virtual node as target node.
        newg.add_nodes(1)
        newg.ndata['feat'][-1] = newg.ndata['feat'][0]
        newg = safe_add_self_loop(newg)
        # Anonymization
        newg.ndata['feat'][0] = 0
        return newg

    def __getitem__(self, i):
        pos_subgraph = self.graph_transform(dgl.node_subgraph(self.dataset, self.paces[i]))
        neg_idx = np.random.randint(self.dataset.num_nodes())
        neg_subgraph = self.graph_transform(dgl.node_subgraph(self.dataset, self.paces[neg_idx]))
        return pos_subgraph, neg_subgraph

    def __len__(self):
        return self.dataset.num_nodes()

    def process(self):
        pass

if __name__ == '__main__':

    dataset = CoLADataSet()
    # print(dataset[0].edges())
    ans = []
    for i in range(100):
        dataset.random_walk_sampling()
        ans.append(dataset[502][1].ndata[dgl.NID].numpy().tolist())
    print(set([str(t) for t in ans]))
    # graph, label = dataset[0]
    # print(graph, label)
