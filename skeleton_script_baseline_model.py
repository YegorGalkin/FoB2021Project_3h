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


def parse_blosum(path: str):
    """
        Reads BLOSUM62 matrix file and stores in a 2-dimensional dictionary.
        :param path: BLOSUM62 substitution matrix file path
        :return: a 2-dimensional dict with amino acid (AA) substitution scores
    """
    # Read all lines from file
    with open(path, "r") as f:
        lines = f.readlines()

    # Remove column names and header
    cleaned_lines = [line.strip() for line in lines if not line.startswith('#') and not line.startswith('x')]

    # Get aminoacids from first column. Matrix is symmetric.
    aas = [line.split()[0] for line in cleaned_lines]

    # Get list of lists of scores converted to int. Skipped first column
    scores = [[int(ele) for ele in line.split()[1:]] for line in cleaned_lines]

    # Create dictionary of dictionaries with scores using aminoacids list as columns and rows.
    scores_dict = dict()
    for i, aa in enumerate(aas):
        scores_dict[aa] = {key: value for (key, value) in zip(aas, scores[i])}

    return scores_dict


def parse_vep(path: str):
    """
        Reads VEP file and parses HGVS IDs and corresponding AA reference-mutation pairs.
        :param path: VEP input file path
        :return: three lists with HGVS IDs, reference AAs, and corresponding mutation AAs, respectively
    """
    # Read all lines from file
    with open(path, "r") as f:
        lines = [line.strip().split() for line in f.readlines()][1:]
    # Convert list of split lines into tuples column-wise
    hgvs_ids, aas, codons = zip(*lines)

    # Split aas column into two tuples
    ref_aas, mut_aas = zip(*[ele.split('/') for ele in aas])

    return list(hgvs_ids), list(ref_aas), list(mut_aas)


def run_baseline(hgvs_ids: list, ref_aas: list, mut_aas: list, blosum_dict: dict):
    """
        Computes substitution scores for a dataset of SNPs using BLOSUM62 matrix.
        :param hgvs_ids: a list of HGVS IDs obtained from parse_vep()
        :param ref_aas: a list of corresponding reference AAs from parse_vep()
        :param mut_aas: a list of corresponding mutation AAs from parse_vep()
        :param blosum_dict: a 2-dimensional dict of BLOSUM62 substitution matrix from parse_blosum()
        :return: a list of calculated substitution scores
    """

    return [blosum_dict[ref_aa][mut_aa] for ref_aa, mut_aa in zip(ref_aas, mut_aas)]


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
