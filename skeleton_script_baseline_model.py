#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Description:
    Baseline impact predictor of SNPs in VEP format.
    Uses raw BLOSUM62 matrix from a text file for scoring.
"""

import argparse
import sys
import os


def parse_args():
    """
        Parses inputs from the commandline.
        :return: inputs as a Namespace object
    """

    parser = argparse.ArgumentParser(description='Generates baseline model predictions.')
    # Arguments
    parser.add_argument('vep', help='a path to the VEP input file')
    parser.add_argument('blosum', help='a path to the BLOSUM62 input file')
    parser.add_argument('-o', dest='out_path', help='a path to write the output .tsv file with baseline model scores. '
                                                    'This arguments is required!', required=True)

    return parser.parse_args()


def parse_blosum(path):
    """
        Reads BLOSUM62 matrix file and stores in a 2-dimensional dictionary.
        :param path: a str with the BLOSUM62 substitution matrix file path
        :return: a 2-dimensional dict with amino acid (AA) substitution scores
    """

    aas = []
    aa_scores = []
    with open(path, "rb") as f:
        for line in f:
            # Convert bytes to str
            line = line.decode('UTF-8')
            # Skip headers
            if line.startswith('#') or line.startswith('x'):
                continue
            # Store AAs and scores (matrix is symmetric)
            else:
                aas.append(line.strip('\n').split()[0])
                aa_scores.append(line.strip('\n').split()[1:len(line)])

    # Create a 2-dimensional dictionary with AAs as keys and empty dictionaries as values
    blosum_dict = {}
    for aa in aas:
        blosum_dict[aa] = {}

    #########################
    ### START CODING HERE ###
    #########################
    # We have double list prepared so we just populate the dictionaries
    for i in range(len(aas)):
        for j in range(len(aas)):
            blosum_dict[aas[i]][aas[j]] = aa_scores[i][j]
    #########################
    ###  END CODING HERE  ###
    #########################

    return blosum_dict


def parse_vep(path):
    """
        Reads VEP file and parses HGVS IDs and corresponding AA reference-mutation pairs.
        :param path: a str with the VEP input file path
        :return: three lists with HGVS IDs, reference AAs, and corresponding mutation AAs, respectively
    """

    hgvs_ids = []
    ref_aas = []
    mut_aas = []
    with open(path, "rb") as f:
        # Read lines
        for line in f:
            # Convert bytes to str
            line = line.decode('UTF-8').strip('\n')
            # Skip header
            if line.startswith('#'):
                continue
            else:
                # Get HGVS ID from the first column and append to the list
                hgvs_ids.append(line.split('\t')[0])
                # Get amino acid mutation which is in the second column in the file
                vars = line.split('\t')[1]
                #########################
                ### START CODING HERE ###
                #########################
                # vars contains ref and mut aas separated by /
                ref_aa, mut_aa = vars.split('/')
                ref_aas.append(ref_aa)
                mut_aas.append(mut_aa)
                #########################
                ###  END CODING HERE  ###
                #########################
    return hgvs_ids, ref_aas, mut_aas


def run_baseline(hgvs_ids, ref_aas, mut_aas, blosum_dict):
    """
        Computes substitution scores for a dataset of SNPs using BLOSUM62 matrix.
        :param hgvs_ids: a list of HGVS IDs obtained from parse_vep()
        :param ref_aa: a list of corresponding reference AAs from parse_vep()
        :param mut_aa: a list of corresponding mutation AAs from parse_vep()
        :param blosum: a 2-dimensional dict of BLOSUM62 substitution matrix from parse_blosum()
        :return: a list of calculated substitution scores
    """

    # A list to store substitution scores for a dataset of SNPs
    scores = []

    #########################
    ### START CODING HERE ###
    #########################
    for i in range(len(hgvs_ids)):
        # Get reference and mutation AAs from the corresponding lists
        ref_aa = ref_aas[i]
        mut_aa = mut_aas[i]

        # Compute BLOSUM62 substitution score the reference AA and the mutation AA stored in blosum_dict
        score = blosum_dict[ref_aa][mut_aa]

        # Append the score to scores
        scores.append(score)

    #########################
    ###  END CODING HERE  ###
    #########################

    return scores


def write_data(hgvs_ids, scores, out_filepath):
    """
        Writes baseline model output to a .tsv file.
        :param hgvs_ids: a list of HGVS IDs obtained from parse_vep()
        :param scores: a list of corresponding BLOSUM62 substitution scores from run_baseline()
        :param out_filepath: a str with the output .tsv file path
    """

    # Open the file to write baseline model results
    with open(out_filepath, 'w') as f:
        # First line contains headers (tab-delimited HGVS ID and Score)
        f.write('# ID\tScore\n')
        # for SNP (its respective HGVS ID) and the calculated score
        for id, score in zip(hgvs_ids, scores):
            # Write HGVS ID and the calculated score to the file with tab separation
            f.write(id + '\t' + score + '\n')

        f.close()


def main():

    # Process arguments
    args = parse_args()
    vep_path = args.vep
    blosum_path = args.blosum
    out_filepath = args.out_path

    out_dir, out_filename = os.path.split(out_filepath)
    # Check if output filename contains .tsv extension
    if '.tsv' not in out_filename:
        sys.exit(r'ERROR: filename "%s" in the output file path argument should contain .tsv extension!' % out_filename)

    # Check if output directory exists
    if not os.path.exists(out_dir):
        sys.exit(r'ERROR: output directory "%s" to store baseline model output does not exist! Follow instructions in'
                 r'the manual!' % out_dir)

    # Parse BLOSUM62 matrix into a 2-dimensional dictionary
    blosum_dict = parse_blosum(blosum_path)
    # Parse VEP input file into lists of HGVS IDs, reference AAs, and corresponding mutation AAs
    hgvs_ids, ref_aas, mut_aas = parse_vep(vep_path)
    # Run baseline model
    scores = run_baseline(hgvs_ids, ref_aas, mut_aas, blosum_dict)
    # Write to a file
    write_data(hgvs_ids, scores, out_filepath)


if __name__ == "__main__":
    main()
