from multiprocessing import Pool
import nltk
import re

"""
contains functions to tokenize a scrubbed plaintext
"""

# global compile regex
r = re.compile("[a-zA-Z\.]+")
r_html = re.compile("<.*?>")  # Match HTML tags
r_acronym = re.compile("\.")

def remove_small(line, min_size=4):
    # todo remove unicode chars from each line
    # for now, min_size=4 cleans them all
    """
    Removes tokens that are smaller than min_count from the input line
    Removes html tags and acronyms
    """
    return "{}\n".format(
        " ".join(
            filter(
                lambda x: len(x) >= min_size,
                (
                    x.lower()
                    for x in nltk.word_tokenize(r_acronym.sub("", r_html.sub("", line)))
                ),
            )
        )
    )


def initial_tokenize(in_path, out_path, workers=48, chunksize=10000):
    """
    in_path: Path object to a scrubbed plaintext file
    out_path: Path object to the location we should write the tokenized file
    reads the file and writes a file to out_path such that every line contains a tokenized sentence
    creates file at out_path if it doesn't exist
    """
    with in_path.open() as f_in:
        with out_path.open("w") as f_out:
            with Pool(workers) as p:
                for s_res in p.imap(remove_small, f_in, chunksize=chunksize):
                    for s in s_res:
                        f_out.write(s)
