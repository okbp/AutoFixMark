#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import glob
import os
import sys

import sys, os
sys.path.insert(0, os.path.abspath('./app'))
from predict_pathways import load_json, evaluate

def main():
    defs = load_json("./definitions/kegg_key_enzymes.json")
    tests = glob.glob('./test/test_*.json')
    all_pass = True

    for tf in sorted(tests):
        case = load_json(tf)
        observed = case['input_ids']
        expected = case['expected']

        # Evaluate all pathways
        results = {
            pw['pathway_name']: evaluate(pw['definition'], observed)
            for pw in defs['pathway_list']
        }

        # Compare against expected values for each case
        for name, exp in expected.items():
            actual = results.get(name)
            status = 'PASS' if actual == exp else 'FAIL'
            print(f"{os.path.basename(tf)} - {name}: expected={exp}, actual={actual} -> {status}")
            if status == 'FAIL':
                all_pass = False

    sys.exit(0 if all_pass else 1)

if __name__ == '__main__':
    main()

# "Usage: python3 test/test_all.py"