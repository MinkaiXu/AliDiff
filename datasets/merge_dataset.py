import pickle
from torch.utils.data import Dataset
from torch_geometric.data import Data
from .pl_data import ProteinLigandData


# FOLLOW_BATCH2 = ('protein_element', 'ligand_element', 'ligand_bond_type', 'ligand_element2', 'ligand_bond_type2')
FOLLOW_BATCH2 = ('protein_element', 'protein_element2', 'ligand_element', 'ligand_bond_type', 'ligand_element2', 'ligand_bond_type2')


class ProteinLigandDPOData(Data):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def from_protein_ligand_dicts(protein_dict=None, **kwargs):
        instance = ProteinLigandData(**kwargs)

        if protein_dict is not None:
            for key, item in protein_dict.items():
                instance[key] = item
            
        return instance

    def __inc__(self, key, value, *args, **kwargs):
        if key == 'ligand_bond_index':
            return self['ligand_element'].size(0)
        elif key == 'ligand_bond_index2':
            return self['ligand_element2'].size(0)
        else:
            return super().__inc__(key, value)


class MergedProteinLigandData(Dataset):
    def __init__(self, dataset1, dataset2):
        self.dataset1 = dataset1
        self.dataset2 = dataset2
        with open('data/affinity_info.pkl', 'rb') as f:
            self.affinity_info = pickle.load(f)
        with open('data/chem_info.pkl', 'rb') as f:
            self.chem_info = pickle.load(f)

        assert len(dataset1) == len(dataset2), "Preference Datasets must have the same length"
        self.length = max(len(dataset1), len(dataset2))


    def __len__(self):
        return self.length  # Return the maximum length of the two datasets

  
    def __getitem__(self, idx):
        # Get a sample from each dataset
        sample1 = self.dataset1[idx % len(self.dataset1)]  # Use modulo to loop through dataset1
        sample2 = self.dataset2[idx % len(self.dataset2)]  # Use modulo to loop through dataset2
        affinity1 = self.affinity_info[sample1['ligand_filename'][:-4]]['vina']
        affinity2 = self.affinity_info[sample2['ligand_filename'][:-4]]['vina']
        sa1 = self.chem_info[sample1['ligand_filename'][:-4]]['sa']
        sa2 = self.chem_info[sample2['ligand_filename'][:-4]]['sa']
        qed1 = self.chem_info[sample1['ligand_filename'][:-4]]['qed']
        qed2 = self.chem_info[sample2['ligand_filename'][:-4]]['qed']
        # assert affinity1 >= affinity2, "Affinity1 must be greater than Affinity2"

        # Combine the information from both samples
        merged_sample = {
            "protein_element": sample1["protein_element"],
            "protein_molecule_name": sample1["protein_molecule_name"],
            "protein_pos": sample1["protein_pos"],
            "protein_is_backbone": sample1["protein_is_backbone"],
            "protein_atom_name": sample1["protein_atom_name"],
            "protein_atom_to_aa_type": sample1["protein_atom_to_aa_type"],
            "ligand_smiles": sample1["ligand_smiles"],
            "ligand_element": sample1["ligand_element"],
            "ligand_pos": sample1["ligand_pos"],
            "ligand_bond_index": sample1["ligand_bond_index"],
            "ligand_bond_type": sample1["ligand_bond_type"],
            "ligand_center_of_mass": sample1["ligand_center_of_mass"],
            "ligand_atom_feature": sample1["ligand_atom_feature"],
            "ligand_hybridization": sample1["ligand_hybridization"],
            "ligand_nbh_list": sample1["ligand_nbh_list"],
            "affinity": affinity1,
            "sa": sa1,
            "qed": qed1,

            # Include information from dataset2
            "protein_element2": sample2["protein_element"],
            "protein_pos2": sample2["protein_pos"],
            "protein_atom_feature2" : sample2["protein_atom_feature"],
            "ligand_smiles2": sample2["ligand_smiles"],
            "ligand_element2": sample2["ligand_element"],
            "ligand_pos2": sample2["ligand_pos"],
            "ligand_bond_index2": sample2["ligand_bond_index"],
            "ligand_bond_type2": sample2["ligand_bond_type"],
            "ligand_center_of_mass2": sample2["ligand_center_of_mass"],
            "ligand_atom_feature2": sample2["ligand_atom_feature"],
            "ligand_hybridization2": sample2["ligand_hybridization"],
            "ligand_nbh_list2": sample2["ligand_nbh_list"],
            "affinity2": affinity2,
            "sa2": sa2,
            "qed2": qed2,

            "protein_filename" : sample1["protein_filename"],
            "ligand_filename" : sample1["ligand_filename"] ,
            "protein_atom_feature" : sample1["protein_atom_feature"],
            "ligand_atom_feature_full" :sample1["ligand_atom_feature_full"],
            "ligand_bond_feature" : sample1["ligand_bond_feature"],

            "ligand_filename2" : sample2["ligand_filename"] ,
            "ligand_atom_feature_full2" : sample2["ligand_atom_feature_full"],
            "ligand_bond_feature2" :sample2["ligand_bond_feature"]
        }

        return ProteinLigandDPOData(**merged_sample)

