import chunk
from multiprocessing import Pool
import nltk
from gensim.models.word2vec import LineSentence
from gensim.models import Word2Vec
from app.preprocessing.WordVectors import WordVectors
import re
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
    return "{}\n".format(" ".join(
        filter(
            lambda x: len(x) >= min_size,
            (x.lower() for x in nltk.word_tokenize(r_acronym.sub("", r_html.sub("", line)))),
        )
    ))

def scrub_line(line, min_sent_len=4):
    """
    Removes degenerate lines that are less than 4 tokens long (including whitespace lines)
    splits a line into multiple sentences if there is more than one sentence on the input line
    line: str
    returns: str
    """
    return "{}\n".format("\n".join(
        filter(
            lambda x: len(nltk.word_tokenize(x)) > min_sent_len,
            nltk.sent_tokenize(line),
        )
    ))

def initial_scrub(in_path, out_path, workers=48, chunksize=10000):
    """
    in_path: Path object to a plaintext_file
    out_path: Path object to the location we should write the scrubbed file
    reads the file and writes a file to out_path such that every line contains exactly one sentence as determined by nltk's sentence tokenizer
    uses streams and iterators so we don't load the entire file into memory at once
    will consume tons of memory if the whole file is on one line
    creates file at out_path if it doesn't exist
    """
    with in_path.open() as f_in:
        # open file to write out, creating it if it doesn't exist
        with out_path.open("w") as f_out:
            with Pool(workers) as p:
                for s_res in p.imap(scrub_line, f_in, chunksize=chunksize):
                    if s_res.strip():
                        f_out.write(s_res)

def initial_tokenize(in_path, out_path, workers = 48, chunksize=10000):
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

def generate_embedding(
    file_in, size=100, window=5, min_count=5, wv_workers=48
):
    """
    generate Word2Vec embedding for sentences with given parameters.
    file in contains preprocessed sentences; one per line
    """
    with file_in.open() as f:
        sentences = LineSentence(f)
        model = Word2Vec(
            sentences,
            vector_size=size,
            window=window,
            min_count=min_count,
            workers=wv_workers
        )
        # create a WordVectors object from the model
        wv = WordVectors(model.wv.index_to_key, vectors=model.wv.vectors)
        return wv
