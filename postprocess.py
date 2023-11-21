# Coding: utf-8
# Author: Hongru WANG (https://rulegreen.github.io/)
# Institution: WISE Lab, The Chinese University of Hong Kong
# Date: 21/Nov 2023
import re
import os
import json
import argparse
from utils import *
import bibtexparser
from bibtexparser.bwriter import BibTexWriter

def is_contain_var(line):
    if "month=" in line.lower().replace(" ",""):
        return True # special case
    line_clean = line.lower().replace(" ","")
    if "=" in line_clean:
        # We ask if there is {, ', ", or if there is an integer in the line (since integer input is allowed)
        if ('{' in line_clean or '"' in line_clean or "'" in line_clean) or has_integer(line):
            return False
        else:
            return True
    return False

def has_integer(line):
    return any(char.isdigit() for char in line)

def post_processing(output_bib_entries, removed_value_names, abbr_dict):
    bibparser = bibtexparser.bparser.BibTexParser(ignore_nonstandard_types=False)
    bib_entry_str = ""
    for entry in output_bib_entries:
        for line in entry:
            if is_contain_var(line):
                continue
            bib_entry_str += line
        bib_entry_str += "\n"
    parsed_entries  = bibtexparser.loads(bib_entry_str, bibparser)
    if len(parsed_entries.entries) < len(output_bib_entries)-5:
        print("Warning: len(parsed_entries.entries) < len(output_bib_entries) -5 -->", len(parsed_entries.entries), len(output_bib_entries))
        output_str = ""
        for entry in output_bib_entries:
            for line in entry:
                # if any([re.match(r".*%s.*=.*"%n, line) for n in removed_value_names if len(n)>1]):
                #     continue
                output_str += line
            output_str += "\n"
        return output_str
    for output_entry in parsed_entries.entries:
        # remove too many authors
        author = output_entry["author"]
        if "\n" in author:
            author_list = author.replace(" and", "").replace(",", "").split("\n")
        else:
            author_list = author.replace(",", "").split(" and ")
        if len(author_list) > 1:
            short_author = author_list[0] + " et al."
            output_entry["author"] = short_author
        for remove_name in removed_value_names:
            if remove_name in output_entry:
                del output_entry[remove_name]
        for (short, pattern) in abbr_dict:
            for place in ["booktitle", "journal"]:
                if place in output_entry:
                    if re.match(pattern, output_entry[place]):
                        output_entry[place] = short

    writer = BibTexWriter()
    return bibtexparser.dumps(parsed_entries, writer=writer)


if __name__ == "__main__":
    filepath = os.path.dirname(os.path.abspath(__file__)) + '/'
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action='store_true', help="Print the version of Rebiber.")
    parser.add_argument("-i", "--input_bib", default="./test.bib",
                        type=str, help="The input bib file")
    parser.add_argument("-o", "--output_bib", default="same",
                        type=str, help="The output bib file")
    parser.add_argument("-l", "--bib_list", default=filepath+"bib_list.txt",
                        type=str, help="The list of candidate bib data.")
    parser.add_argument("-a", "--abbr_tsv", default=filepath+"/short/abbr.tsv",
                        type=str, help="The list of conference abbreviation data.")
    parser.add_argument("-d", "--deduplicate", default=True,
                        type=bool, help="True to remove entries with duplicate keys.")
    parser.add_argument("-s", "--shorten", default=True,
                        type=bool, help="True to shorten the conference names.")
    parser.add_argument("-r", "--remove", default="",
                        type=str, help="A comma-separated list of values you want to remove, such as '--remove url,biburl,address,publisher,organization,number,doi,timestamp,editor,issn'.")
    args = parser.parse_args()

    # read data
    all_bib_entries = load_bib_file(args.input_bib)
    
    abbr_dict = load_abbr_tsv(args.abbr_tsv)
    removed_value_names = [s.strip() for s in args.remove.split(",")]

    # post processing
    output_string = post_processing(all_bib_entries, removed_value_names, abbr_dict)
    output_path = args.input_bib if args.output_bib == "same" else args.output_bib
    with open(output_path, "w", encoding='utf8') as output_file:
        output_file.write(output_string)