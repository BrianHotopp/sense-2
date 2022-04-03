import json
import argparse
from pydoc import doc

"""
Converts ArXiV JSON files to line text files
"""

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("output")

args = parser.parse_args()

with open(args.input) as fin:
    data = json.load(fin)
with open(args.output, "w") as fout:
    for article in data:
        fout.write("%s\n" % (" ".join(article)))
print("Done.")

