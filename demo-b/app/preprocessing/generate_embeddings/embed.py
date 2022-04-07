from multiprocessing import Pool
from gensim.models.word2vec import LineSentence
from gensim.models import Word2Vec
from app.preprocessing.WordVectors import WordVectors

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
