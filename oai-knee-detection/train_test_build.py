# ==============================================================================
# Copyright (C) 2020 Bofei Zhang, Jimin Tan, Greg Chang, Kyunghyun Cho, Cem Deniz
#
# This file is part of OAI-KL-Grade-Classification
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ==============================================================================
import pandas as pd
import os
import sys
import pydicom as dicom
import time
import matplotlib.pyplot as plt
import cv2
import numpy as np
import matplotlib.patches as patches
import h5py
import argparse
'''
Build train and test for bounding box detector.
'''

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--dataset', type=str, help='where to load the content file')
parser.add_argument('-od', '--output-dir', type=str, help='Where to save the data')



def invert(img):
    img = img.max() - img
    return img


def writeDicom2H5(df,output_folder, oai_dataset, stage='train'):
    total_samples = df.shape[0]
    count = 0
    contents_folder = output_folder
    output_folder = output_folder + stage + '/'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    contents = []
    resize_shape = 896
    break_piont = 100000
    for idx,row in df.iterrows():
        start = time.time()
        file_name = row[0]
        bbox = np.array([int(i) for i in row[1:]])
        x1l, y1l, x2l, y2l = bbox[:4]
        x1r, y1r, x2r, y2r = bbox[4:]

        data_path = os.path.join(OAI_DATASET,month,file_name)
        count += 1
        if count == break_piont:
            break
        print('Process {}/{}'.format(count,total_samples))
        dicom_img = dicom.dcmread(data_path)
        # print('Photo Interpretation:', dicom_img.PhotometricInterpretation)
        img = dicom_img.pixel_array.astype(float)
        if dicom_img.PhotometricInterpretation == 'MONOCHROME1':
            img = invert(img)

        img = (np.maximum(img, 0) / img.max()) * 255.0
        row, col = img.shape
        img = cv2.resize(img, (resize_shape, resize_shape), interpolation=cv2.INTER_CUBIC)

        ratio_x = resize_shape / col
        ratio_y = resize_shape / row

        # normalize this coordinates to 0 - 1
        x1l = x1l * ratio_x
        x2l = x2l * ratio_x
        x1r = x1r * ratio_x
        x2r = x2r * ratio_x

        y1l = y1l * ratio_y
        y2l = y2l * ratio_y
        y1r = y1r * ratio_y
        y2r = y2r * ratio_y
        bbox_convert = np.array([x1l, y1l, x2l, y2l,
                                 x1r, y1r, x2r, y2r])
        bbox_convert = bbox_convert / resize_shape # normalize
        img_f_name = file_name.replace('/', '_')
        img_f_name = img_f_name + '.h5'
        output_data_path = output_folder + img_f_name
        f = h5py.File(output_data_path, 'w')
        f.create_dataset('data', data=img)
        f.close()
        contents.append([output_data_path] + bbox_convert.tolist())
    contents = pd.DataFrame(contents)
    contents.to_csv(contents_folder + '/' + stage + '.csv',index=False)
    print(contents)


def main(args):
    df1 = pd.read_csv('../data/OAI_test.csv',header=None,sep=' ')
    df2 = pd.read_csv('../data/OAI_val.csv',header=None,sep=' ')
    print(df1.head())
    print(df2.head())

    df = df1.append(df2)
    print(df.shape)

    month = '00m'
    OAI_DATASET = args.dataset
    output_folder = args.output_dir
    print(df.shape)
    train = df.sample(frac=0.7)
    df = df.drop(train.index)
    print(train.shape, df.shape)
    test = df.sample(frac=0.67)
    df = df.drop(test.index)
    val = df
    print('Training data {}; Test data {}; Val data {}.'\
          .format(train.shape[0],test.shape[0],val.shape[0]))
    writeDicom2H5(train, output_folder, OAI_DATASET, stage='train')
    writeDicom2H5(test, output_folder, OAI_DATASET, stage='test')
    writeDicom2H5(val, output_folder, OAI_DATASET, stage='val')


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
