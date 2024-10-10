import os
import sys

import argparse
from datasets.pl_pair_dataset import PocketLigandPairDataset
from tqdm.auto import tqdm
import pickle
from collections import Counter



if __name__ == '__main__':
    def get_pdb_name(fn):
        return os.path.basename(fn)[:4]

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str, default='./data/crossdocked_v1.1_rmsd1.0_pocket10')
    parser.add_argument('--save_path', type=str, default='/tmp')

    args = parser.parse_args('')
    dataset = PocketLigandPairDataset(args.path)


    with open('data/affinity_info.pkl', 'rb') as f:
        affinity_info = pickle.load(f)



    unique_id = []
    pdb_visited = set()

    num_data = len(dataset)
    for idx in tqdm(range(num_data), 'Filter'):
        pdb_name = get_pdb_name(dataset[idx].ligand_filename)
        if pdb_name not in pdb_visited:
            unique_id.append(idx)
            pdb_visited.add(pdb_name)

    print('Number of Pairs: %d' % len(dataset))
    print('Number of PDBs:  %d' % len(pdb_visited))



    # calculate the number of pairs per protein
    counter = Counter()
    for idx in tqdm(range(num_data), 'Counting'):
        pdb_name = get_pdb_name(dataset[idx].ligand_filename)
        counter[pdb_name] += 1

    print('Number of Pairs per Protein')
    print(counter)

    # take the number of counters as list
    num_pairs = list(counter.values())
    print(max(num_pairs), min(num_pairs), sum(num_pairs) / len(num_pairs))

    # calculate the number of proteins that are more than 1 pair
    print('Number of Proteins that are more than 1 pair')



    # Assuming counter is already defined and populated as in your code
    filtered_keys = [key for key, value in counter.items() if value > 1]


    my_dict = {}
    for item in filtered_keys:
        my_dict[item] = []

    for idx in tqdm(range(len(dataset)), 'Filter'):
        pdb_name = get_pdb_name(dataset[idx].ligand_filename)
        if pdb_name in filtered_keys:
            my_dict[pdb_name].append(idx)


    dpo_idx = {}
    dpo_idx_sort = {}

    for idx in tqdm(range(len(dataset)), 'Filter'):
        pdb_name = get_pdb_name(dataset[idx].ligand_filename)
        if pdb_name in my_dict:
            aff_idx = my_dict[pdb_name]
            sort_dict = {}
            for item in aff_idx:
                if affinity_info[dataset[item]['ligand_filename'][:-4]]['vina'] > affinity_info[dataset[idx]['ligand_filename'][:-4]]['vina']:
                    sort_dict[item] = affinity_info[dataset[item]['ligand_filename'][:-4]]['vina']
            if sort_dict:
                #print(sort_dict)
                dpo_idx_sort[idx] = [max(sort_dict, key=sort_dict.get)]
                dpo_idx[idx] = list(sort_dict.keys())
            
    dpo_sort_filename = os.path.join(args.save_path, 'dpo_idx_sort_new.pkl')

    # Open a file for writing
    with open(dpo_sort_filename, 'wb') as file:  # The 'wb' argument indicates that you are writing to the file in binary mode
        # Dump the dictionary to a pickle file
        pickle.dump(dpo_idx_sort, file)

    dpo_filename = os.path.join(args.save_path, 'dpo_idx_new.pkl')

    # Open a file for writing
    with open(dpo_filename, 'wb') as file:  # The 'wb' argument indicates that you are writing to the file in binary mode
        # Dump the dictionary to a pickle file
        pickle.dump(dpo_idx, file)