# NAME: gene_extraction.py
# AUTHOR: Andrew Weymes
# EMAIL: 23433267@student.uwa.edu.au
#
# DETAILS: This program reads in a csv file, downloads the genome assembly,
#          saves as genbank file, extracts genes of interest, and saves
#          to another csv file. Check README for further details.
#
# VERSION: 1.0


## IMPORT MODULES
from io import StringIO
import pandas as pd
from Bio import Entrez
import os
from Bio import SeqIO


## READ IN THE CSV FILE CONTAINING GENES OF INTEREST
goi = input("input the name of the file to read in here, include csv file extension.\n")
with open(goi, "r", encoding="utf-8-sig") as f:
    filename = f.readline().strip().replace(",","")
    accession = f.readline().strip().replace(",","")
    genes_of_interest = pd.read_csv(StringIO(f.read().lower()), sep=",")

print("FILE SUCCESSFULLY READ\n")


## DOWNLOAD THE GENBANK FILE FOR THE CORRESPONDING ACCESSION NUMBER
# SET EMAIL
Entrez.email = input("Please enter email here: ") # I added this as I plan on adding multi-file handling in future
print()

# SET FILE DOWNLOAD PARAMETERS
if not os.path.isfile(filename+" Assembly.gb"):
    assembly = Entrez.efetch(db="nucleotide", id=accession, rettype="gb", retmode="text")
    with open(filename+" Assembly.gb", "w") as output_file:
        output_file.write(assembly.read())
        print("GENOME ASSEMBLY SUCCESSFULLY FOUND AND SAVED\n")
else:
    print("FILE EXISTS, CHECK DIRECTORY\n")


## READ IN SAVED FILE
assembly = SeqIO.read(filename+" Assembly.gb", "gb")
print("ASSEMBLY FILE LOADED\n")


## EXTRACT ALL THE FEATURES
genes = [gene for gene in assembly.features if gene.type == "CDS"]


## GET SEQUENCES FOR GENES OF INTEREST
locus_tags = []
sequences = []

for i in genes_of_interest["gene"]:
    for n, gene in enumerate(genes):
        if "gene" in gene.qualifiers.keys():
            if gene.qualifiers["gene"][0].lower() == i:
                locus_tags.append(gene.qualifiers["locus_tag"][0])
                sequence = gene.extract(assembly)
                sequences.append(str(sequence.seq))
                break
            elif n == len(genes)-1: # There has to be a better way to do this?
                locus_tags.append("NOT FOUND")
                sequences.append("NOT FOUND")


## ASSIGN TO DATAFRAME AND SAVE TO CSV
genes_of_interest["locus_tags"] = locus_tags
genes_of_interest["sequences"] = sequences
genes_of_interest = genes_of_interest[["gene","locus_tags","description","sequences"]]
genes_of_interest.to_csv(filename+" Sequences.csv", index=False)

print("LOCUS TAGS AND SEQUENCES SUCCESSFULLY SAVED\n")


## PRINT FOLLOW UP IF ANY VOIDS
if "NOT FOUND" in genes_of_interest.locus_tags.values:
    print((genes_of_interest["locus_tags"] == "NOT FOUND").sum(), "GENES COULD NOT BE FOUND\n")
    print("THE FOLLOWING GENES WERE UNABLE TO BE FOUND:\n")
    print(genes_of_interest["gene"].loc[genes_of_interest["locus_tags"] == "NOT FOUND"],"\n")


## COMPLETE
print("PROGRAM SUCCESSFULLY COMPLETED.\n")
print("IF THERE ARE ISSUES OR SUGGESTIONS, PLEASE CONTACT ANDREW AT 23433267@student.uwa.edu.au")
