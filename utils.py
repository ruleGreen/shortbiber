# Coding: utf-8
# Author: Hongru WANG (https://rulegreen.github.io/)
# Institution: WISE Lab, The Chinese University of Hong Kong
# Date: 21/Nov 2023

import re

def load_abbr_tsv(abbr_tsv_file):
    abbr_dict = []
    with open(abbr_tsv_file) as f:
        for line in f.read().splitlines():
            ls = line.split("|")
            if len(ls) == 2:
                abbr_dict.append((ls[0].strip(), ls[1].strip())) 
    return abbr_dict

def normalize_title(title_str):
    title_str = re.sub(r'[^a-zA-Z]',r'', title_str) 
    return title_str.lower().replace(" ", "").strip()


def load_bib_file(bibpath):
    all_bib_entries = []
    with open(bibpath, encoding='utf8') as f:
        bib_entry_buffer = []
        lines = f.readlines() + ["\n"]

        brace_count = 0  # Keep track of opened and closed braces

        for line in lines:
            if "@string" in line:
                continue
            if line.strip().startswith("%") or line.strip().startswith("#") or line.strip().startswith("//"):
                bib_entry_buffer = []
                continue
            
            bib_entry_buffer.append(line)
            brace_count += line.count("{") - line.count("}")

            # If brace_count is zero, then all opened braces have been closed
            if brace_count == 0:
                # Filter out the entries that only contain ['\n'] or ['']
                if bib_entry_buffer != ['\n'] and bib_entry_buffer != ['']:
                    all_bib_entries.append(bib_entry_buffer)
                bib_entry_buffer = []

    # print(all_bib_entries)
    return all_bib_entries
