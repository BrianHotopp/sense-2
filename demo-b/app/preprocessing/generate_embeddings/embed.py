import chunk
from multiprocessing import Pool
import nltk
from gensim.models.word2vec import LineSentence
from gensim.models import Word2Vec
from app.preprocessing.WordVectors import WordVectors

def tokenize(in_path, workers=16, chunksize=10000):
    """
    in_path: Path object to a plaintext_file
    returns: iterator of sentences where each element is list(list(str))
    """
    with in_path.open() as f:
        with Pool(workers) as p:
            for sentence in p.imap(nltk.word_tokenize, f, chunksize):
                yield sentence
                
def scrub_line(line, min_sent_len = 4):
    """
    Removes degenerate lines that are less than 4 tokens long (including whitespace lines)
    splits a line into multiple sentences if there is more than one sentence on the input line
    """
    return list(filter(lambda x: len(nltk.word_tokenize(x)) > min_sent_len, nltk.sent_tokenize(line)))

def initial_scrub(in_path, out_path, workers=48, chunksize=10000):
    """
    in_path: Path object to a plaintext_file
    out_path: Path object to the location we should write the scrubbed file
    reads the file and writes a file to out_path it such that every line contains exactly one sentence as determined by nltk's sentence tokenizer
    uses streams and iterators so we don't load the entire file into memory at once
    will consume tons of memory if the whole file is on one line
    """
    with in_path.open() as f_in:
        # open file to write out
        with out_path.open('w') as f_out:
            with Pool(workers) as p:
                for s_res in p.imap(scrub_line, f_in, chunksize=chunksize):
                    for s in s_res:
                        f_out.write(f"{s}\n")
        

def generate_embedding(file_in, size=100, window=5, min_count=5, token_workers=16, wv_workers=48):
    """
    generate Word2Vec embedding for sentences with given parameters.
    """
    input_corpus = LineSentence(file_in) 
    model = Word2Vec(input_corpus, vector_size=size, window=window, min_count=min_count, workers=wv_workers)
    # create a WordVectors object from the model
    wv = WordVectors(model.wv.index_to_key, vectors = model.wv.vectors)
    return wv
