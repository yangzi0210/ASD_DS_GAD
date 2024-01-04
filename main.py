import argparse
import torch
import os
import pandas as pd
from datetime import datetime
from construct_graph import population_graph
from kfold_eval import kfold_mlp, kfold_gcn
from training import graph_pooling, extract
import warnings

warnings.filterwarnings("ignore")  # 忽略UserWarning兼容性警告

parser = argparse.ArgumentParser()

parser.add_argument('--seed', type=int, default=13, help='random seed')
parser.add_argument('--batch_size', type=int, default=128, help='batch size')
parser.add_argument('--lr', type=float, default=0.0001, help='learning rate')
parser.add_argument('--nhid', type=int, default=256, help='hidden size of MLP')
parser.add_argument('--pooling_ratio', type=float, default=0.05, help='pooling ratio')
parser.add_argument('--dropout_ratio', type=float, default=0.01, help='dropout ratio')
parser.add_argument('--data_dir', type=str, default='./data', help='root of all the datasets')
parser.add_argument('--device', type=str, default='cuda:0', help='for macos')
parser.add_argument('--check_dir', type=str, default='./checkpoints', help='root of saved models')
parser.add_argument('--result_dir', type=str, default='./results', help='root of classification results')
parser.add_argument('--verbose', type=bool, default=True, help='print training details')

args = parser.parse_args()
# Set random seed
torch.manual_seed(args.seed)

if __name__ == '__main__':
    # check if exists downsampled brain imaging data
    downsample_file = os.path.join(args.data_dir, 'ABIDE_downsample',
                                   'ABIDE_pool_{:.3f}_.txt'.format(args.pooling_ratio))
    # if not os.path.exists(downsample_file):
    #     print('Running graph pooling with pooling ratio = {:.3f}'.format(args.pooling_ratio))
    graph_pooling(args)
    # print('start')

    start_time = datetime.now()

    # load sparse brain networking
    '''
    numpy array 871 * 379 float
    '''
    downsample = pd.read_csv(downsample_file, header=None, sep='\t').values

    # kfold_mlp(downsample, args)

    # use the best MLP model to extract further learned features
    # from pooling results
    # extract(downsample, args)

    # check if population graph is constructed
    adj_path = os.path.join(args.data_dir, 'population graph', 'ABIDE.adj')
    attr_path = os.path.join(args.data_dir, 'population graph', 'ABIDE.attr')

    # if not os.path.exists(adj_path) or not os.path.exists(attr_path):
    population_graph(args)

    # Load population graph
    edge_index = pd.read_csv(adj_path, header=None).values
    edge_attr = pd.read_csv(attr_path, header=None).values.reshape(-1)

    # run GCN
    kfold_gcn(edge_index, edge_attr, downsample.shape[0], args)
    end_time = datetime.now()
    spend_time = end_time - start_time
    print('end')
    print(f'Spend Time: {spend_time}')
