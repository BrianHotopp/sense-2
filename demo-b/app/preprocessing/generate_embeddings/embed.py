from multiprocessing import Pool
import nltk
from gensim.models import Word2Vec
from app.preprocessing.WordVectors import WordVectors

def cleanup_sentences(line, min_token_length=4):
    # regex = re.compile("\W+")
    sents = nltk.sent_tokenize(line)
    sentences = list()
    for sent in sents:
        tokens = nltk.word_tokenize(sent)
        s = [t for t in tokens if len(t) > min_token_length]
        if len(s) > 0:
            sentences.append(s)
    return sentences

def cleanup_corpus(lines, workers):
    """
    Clean-up corpus by taking sentences and word tokens, removing non-word tokens.
    """
    with Pool(workers) as p:
        pool_sents = p.map(cleanup_sentences, lines)

    sentences = list()
    for s in pool_sents:
        sentences.extend(s)

    return sentences

def preprocess(lines, workers=48):
    sentences = cleanup_corpus(lines, workers)
    return sentences
     
def generate_embedding(path, size=100, window=5, min_count=5, workers=48):
    """
    generate Word2Vec embedding for plaintext file
    path: pathlib file object
    """
    # open the file and preprocess the lines
    with path.open() as f:
        lines = f.readlines()
    sentences = preprocess(lines)
    # generate the embedding
    # print how many sentences are in the corpus
    print(sentences)
    model = Word2Vec(sentences, vector_size=size, window=window, min_count=min_count, workers=workers)
    # create a WordVectors object from the model
    wv = WordVectors(model.wv.index_to_key, vectors = model.wv.vectors)
    return wv