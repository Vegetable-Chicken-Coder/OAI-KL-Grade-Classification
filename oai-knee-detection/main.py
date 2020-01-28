import pandas as pd
from model.dataloader import DicomDataset
import torchvision.transforms as transforms
import torch.utils.data as data
from model.model import ResNet
import torch
import numpy as np
from torch.autograd import Variable
from tqdm import tqdm
import sys
import argparse
'''
Output bounding box from given model
'''
parser = argparse.ArgumentParser(description='Annotation')
parser.add_argument('-md', '--model_dir', action="store", dest="model_dir", type=str,
                    help="model directory",
                    default='/gpfs/data/denizlab/Users/bz1030/oai-knee-detection/test/model_2020-01-28_21-17-58/epoch_1.pth')
parser.add_argument('-cd', '--content-dir', action="store", dest="content_dir", type=str,
                    help="content file", default='/gpfs/data/denizlab/Users/bz1030/KneeNet/KneeProject/Dataset/OAI_summary.csv')
parser.add_argument('-dh', '--data-home', action="store", dest="data_home", type=str,
                    help="data home directory", default='/gpfs/data/denizlab/Datasets/OAI_original')
parser.add_argument('-m', '--month', action="store", dest="month", type=str,
                    help="which part of OAI to be processed", default='00m')

if __name__ =='__main__':
    args = parser.parse_args()
    Month = args.month
    contents = args.content_dir
    data_home = args.data_home
    load_model = args.model_dir
    USE_CUDA = torch.cuda.is_available()
    df = pd.read_csv(contents)
    df = df.loc[df.Visit == Month]
    annot_dataset = df[['Folder', 'Visit']].drop_duplicates().reset_index()
    annot_dataset.drop('index', axis=1, inplace=True)
    print(annot_dataset.head())
    dataset2annot = DicomDataset(annot_dataset, data_home, None)
    annot_loader = data.DataLoader(dataset2annot, batch_size=16)
    net = torch.load(load_model) if USE_CUDA else torch.load(load_model, map_location='cpu')
    net.eval()
    if USE_CUDA:
        net.cuda()
    rows =[]
    cols =[]
    ratios_x = []
    ratios_y = []
    bboxs = []
    all_names = []
    bar = tqdm(total=len(annot_loader), desc='Processing', ncols=90)
    for i, (batch, row, col, ratio_x,ratio_y,f_name) in enumerate(annot_loader):
        if USE_CUDA:
            inputs = Variable(batch.cuda())
        else:
            inputs = Variable(batch)
        output = net(inputs)

        bboxs.append(output.data.cpu().numpy())
        rows.extend(row.data.cpu().numpy().tolist())
        cols.extend(col.data.cpu().numpy().tolist())
        ratios_x.extend(ratio_x.data.cpu().numpy().tolist())
        ratios_y.extend(ratio_y.data.cpu().numpy().tolist())
        all_names.extend(f_name)
        bar.update(1)
    bboxs = np.vstack(bboxs)
    print(bboxs.shape)
    print(len(rows), len(cols), len(ratios_y), len(ratios_x), len(all_names))
    df = pd.DataFrame(bboxs)
    df['rows'] = rows
    df['cols'] = cols
    df['ratios_x'] = ratios_x
    df['ratios_y'] = ratios_y
    df['fname'] = all_names
    df.to_csv('output{}.csv'.format(Month), index=False)