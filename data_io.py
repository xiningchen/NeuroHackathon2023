"""
Supportive functions for file input and output from .xlsx, .mat, .csv
Last updated: Feb. 16 2023
Author(s): Xining Chen
"""
import os
import networkx as nx
import pickle as pkl
import importlib
import numpy as np
import pandas as pd
from tqdm import tqdm
import controllability as ctrb
importlib.reload(ctrb)
from scipy.io import loadmat


def __check_path(full_path):
    if not os.path.exists(os.path.dirname(full_path)):
        os.makedirs(os.path.dirname(full_path))


def open_data(path, num=1064, ftype="graphml"):
    all_data = {}
    c = 0
    for root, dirs, files in os.walk(path):
        for file in tqdm(files):
            if c >= num:
                break
            if not file.endswith(f".{ftype}"):
                continue
            G = nx.read_graphml(f'{path}{file}')
            # --- Alison ---
            # Add code here to convert nx graph --> Adj matrix.
            # Store adj. matrix into a variable called avg_mat (you need to define this above, outside the loops)
            # Take the average using 'c' (counting how many files read) by avg_mat/c and then return that value.
            # -----
            all_data[file] = G
            c += 1
    return all_data


def open_data2(path, num=1064, ftype="graphml"):
    all_data = {}
    c = 0
    min_w = 100000
    max_w = 0
    mW = 0
    for root, dirs, files in os.walk(path):
        for file in tqdm(files):
            if c >= num:
                break
            if not file.endswith(f".{ftype}"):
                continue
            G = nx.read_graphml(f'{path}{file}')
            adjMat = nx.to_numpy_array(G, weight="number_of_fibers")
            if np.count_nonzero(adjMat) == 0:
                print("No brain data #", file)
                continue
            meanWeight = adjMat.sum() / np.count_nonzero(adjMat)
            if meanWeight < min_w:
                min_w = meanWeight
            if meanWeight > max_w:
                max_w = meanWeight
            mW += meanWeight

            adjMat = adjMat/meanWeight
            G_norm = nx.from_numpy_array(adjMat)

            avgCtrbDict = ctrb.avg_control(G_norm)
            nx.set_node_attributes(G, avgCtrbDict, name='avgCtrb')

            modalCtrbDict = ctrb.modal_control(G_norm)
            nx.set_node_attributes(G, modalCtrbDict, name='modCtrb')

            all_data[file] = G
            c += 1
    print("Group connectome edge weight info: ")
    print("\tmin mean W:", min_w)
    print("\tmax mean W:", max_w)
    print("\tGroup mean W:", mW/c)
    return all_data


def save_to_pickle(data, path, pickle_name):
    """
    Save some data to a pickle.
    :param data: data to be saved
    :param path: path to save location
    :param pickle_name: name of pickle file
    :return:
    """
    if '.pkl' not in pickle_name:
        pickle_name += '.pkl'
    file_path = os.path.join(path, pickle_name)
    __check_path(file_path)
    with open(file_path, 'wb') as f:
        pkl.dump(data, f)
    print(f"Saved to {file_path}.")


def load_from_pickle(path, pickle_name):
    """
    Load data from a pickle
    :param path: path to file location
    :param pickle_name: pickle name to be read
    :return: data stored in pickle
    """
    file_path = os.path.join(path, pickle_name)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            res = pkl.load(f)
        return res
    else:
        return []


def load_all_pickles(path, keyword=""):
    """
    Load all pickles at some path.
    :param path: path to a folder.
    :param keyword: keyword to check if file's name contains this word.
    :return:
    """
    all_data = {}
    for root, dirs, files in os.walk(path):
        for file in (files):
            if not file.endswith('.pkl'):
                continue
            if keyword == "":
                with open(root + file, 'rb') as f:
                    all_data[file] = pkl.load(f)
            elif keyword in file:
                with open(root + file, 'rb') as f:
                    all_data[file] = pkl.load(f)
    return all_data


def write_text_file(content, path):
    with open(path, "w") as f:
        f.write(content)