from ctypes import alignment
import time
import uuid
from flask import Flask, request, jsonify, current_app, g
import argparse
import numpy as np
import pickle
from sklearn.decomposition import PCA
import json
import sqlite3
import app.preprocessing.generate_embeddings.occurrences as occ
import app.preprocessing.generate_embeddings.embed as embed
from app.preprocessing.generate_examples.alignment.align import Alignment
from preprocessing.WordVectors import WordVectors
from flask_cors import CORS
from pathlib import Path

DATABASE = "app/db/demo_app.db"
UPLOAD_FOLDER = "app/uploads"
SCRUBBED_FOLDER = "app/scrubbed"
OCCURRENCES_FOLDER = "app/occurrences"
EMBEDDINGS_FOLDER = "app/embeddings"
ALIGNMENTS_FOLDER = "app/alignments"
TOKENIZED_FOLDER = "app/tokenized"
ALLOWED_EXTENSIONS = set(["txt"])

sqlite3.register_adapter(np.float64, float)
def clean_start():
    # reset the database
    init_db()
    # Delete all files in the uploads folder
    for file in Path(UPLOAD_FOLDER).glob("*"):
        file.unlink()
    # Delete all files in the scrubbed folder
    for file in Path(SCRUBBED_FOLDER).glob("*"):
        file.unlink()
    # Delete all files in the occurrences folder
    for file in Path(OCCURRENCES_FOLDER).glob("*"):
        file.unlink()
    # Delete all files in the embeddings folder
    for file in Path(EMBEDDINGS_FOLDER).glob("*"):
        file.unlink()
    # Delete all files in the alignments folder
    for file in Path(ALIGNMENTS_FOLDER).glob("*"):
        file.unlink()
    # Delete all files in the tokenized folder
    for file in Path(TOKENIZED_FOLDER).glob("*"):
        file.unlink()
    

def allowed_file(filename):
    """
    Check if the file is allowed
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def make_dicts(cursor, row):
    """
    Convert the sqlite3 cursor to a list of dictionaries
    """
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


def get_db():
    """
    connect to the sqlite db
    """
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = make_dicts
    return db


def init_db():
    """
    Initialize the database
    """
    with app.app_context():
        db = get_db()
        with current_app.open_resource("db/schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


def write_db(query, args=()):
    """
    Write to the database
    """
    db = get_db()
    db.execute(query, args)
    db.commit()


def write_db_ret_last(query, args=()):
    """
    Write to the database, returning the last inserted id
    """
    db = get_db()
    db.execute(query, args)
    db.commit()
    id = db.execute("SELECT last_insert_rowid()").fetchone()["last_insert_rowid()"]
    return id


def query_db(query, args=(), one=False):
    """
    Query the database
    """
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SCRUBBED_FOLDER"] = SCRUBBED_FOLDER
app.config["OCCURRENCES_FOLDER"] = OCCURRENCES_FOLDER 
app.config["EMBEDDINGS_FOLDER"] = EMBEDDINGS_FOLDER
app.config["ALIGNMENTS_FOLDER"] = ALIGNMENTS_FOLDER
app.config["TOKENIZED_FOLDER"] = TOKENIZED_FOLDER 
CORS(app, resources={r"/*": {"origins": "*"}})
# uncomment this line to reset the db on app start
#clean_start()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    return current_app.send_static_file("layout.html")


@app.route("/getPlainTexts", methods=["GET"])
def getPlainTexts():
    """
    Get the plaintexts from the database
    """
    return jsonify(query_db("SELECT * FROM plaintexts"))


@app.route("/getAllEmbeddings")
def get_all_embeddings():
    """
    return all embeddings
    """
    return jsonify(query_db("SELECT * FROM embeddings"))


@app.route("/getEmbeddings", methods=["POST"])
def get_embeddings():
    """
    return embeddings for a given plaintext
    """
    data = request.get_json()
    # check if the request has a pt_id
    if "pt_id" in data:
        pt_id = data["pt_id"]
        return jsonify(query_db("SELECT * FROM embeddings WHERE pt_id = ?", (pt_id,)))
    else:
        print(data)
        return jsonify({"error": "No plaintext id provided"})


@app.route("/uploadFile", methods=["POST"])
def upload_file():
    """
    upload a large file
    """
    # check if the post request has the file part
    if "file" not in request.files:
        return jsonify({"message": "No file part in the request"}), 400
    file = request.files["file"]
    # retreive metadata
    # check if the post request has the data part
    if "data" not in request.form:
        return jsonify({"message": "No data part in the request"}), 400
    d = json.loads(request.form.get("data"))
    # check to see if the post request has the dataset name
    if "name" not in d:
        return jsonify({"message": "No dataset name in the request"}), 400
    dataset_name = d["name"]
    # check to see if the post request has the dataset description
    if "description" not in d:
        return jsonify({"message": "No dataset description in the request"}), 400
    dataset_description = d["description"]
    # if user does not select file, browser also submits an empty part without filename
    if file.filename == "":
        return jsonify({"message": "No file selected for uploading"}), 400
    if file and allowed_file(file.filename):
        # generate a random filename
        filename = Path(str(uuid.uuid4()) + ".txt")
        f_path = Path(app.config["UPLOAD_FOLDER"]) / filename
        file.save(f_path)
        # scrub the file and save the scrubbed copy
        # generate random scrub filename
        s_filename = Path(str(uuid.uuid4()) + ".txt")
        s_path = Path(app.config["SCRUBBED_FOLDER"]) / s_filename
        # scrub and write to s_path
        embed.initial_scrub(f_path, s_path)
        # tokenize the scrubbed file and save the tokenized copy
        # generate random tokenized filename
        t_filename = Path(str(uuid.uuid4()) + ".txt")
        t_path = Path(app.config["TOKENIZED_FOLDER"]) / t_filename
        # tokenize and write to t_path
        embed.initial_tokenize(s_path, t_path)
        # generate occurrences
        occ_filename = Path(str(uuid.uuid4()) + ".txt")
        occ_path = Path(app.config["OCCURRENCES_FOLDER"]) / occ_filename
        occs = occ.get_occurrences(t_path)
        # pickle dump occs to occ_path
        with open(occ_path, "wb+") as f:
            pickle.dump(occs, f)
        # insert dataset_name, dataset_description, f_path, s_path, t_path, and occ_path into the database
        dataset_id = write_db_ret_last(
            "INSERT INTO plaintexts (name, description, p_path, s_path, t_path, occ_path) VALUES (?, ?, ?, ?, ?, ?)",
            (dataset_name, dataset_description, str(f_path), str(s_path), str(t_path), str(occ_path)),
        )
        return jsonify({"message": "File successfully uploaded and indexed", "id": dataset_id}), 201
    return jsonify({"message": "Allowed file types are txt"}), 400


# route to generate an embedding for a file in the database


@app.route("/generateEmbedding", methods=["POST"])
def generate_embedding():
    """
    generate an embedding for a file already in the database
    """
    # get request json
    d = request.get_json()
    # check to see if the request has the dataset id
    if "id" not in d:
        return jsonify({"message": "No dataset id in the request"}), 400
    # check to see if the request has a name
    if "name" not in d:
        return jsonify({"message": "No name in the request"}), 400
    # check to see if the request has a description
    if "description" not in d:
        return jsonify({"message": "No description in the request"}), 400
    pt_id = d["id"]
    e_name = d["name"]
    e_description = d["description"]
    # if the provided file id is not in the database
    pt = query_db("SELECT t_path FROM plaintexts WHERE id = ?", (pt_id,), one=True)
    if pt is None:
        return jsonify({"message": "Invalid file id"}), 400
    # get the path to the tokenized plaintext from the database response
    pt_p = pt["t_path"]
    pt_po = Path(pt_p)
    # generate the embedding
    print("opening file at " + str(pt_po))
    wv = embed.generate_embedding(pt_po)
    # generate a random filename for the embedding
    e_fn = Path(str(uuid.uuid4()) + ".txt")
    e_path = Path(app.config["EMBEDDINGS_FOLDER"]) / e_fn
    wv.to_file(e_path)
    # create entry in embeddings for the embedding, return the id
    e_id = write_db_ret_last(
        "INSERT INTO embeddings (name, description, pt_id, wv_path) VALUES (?, ?, ?, ?)",
        (e_name, e_description, pt_id, str(e_path)),
    )
    return jsonify({"message": "Embedding generated", "id": e_id}), 201


# route for generating alignments
@app.route("/generateAlignment", methods=["POST"])
def generate_alignment():
    """
    generates an alignment for an existing pair of embeddings using their ids
    """
    # get request json
    d = request.get_json()
    e1_id = max(d["e1_id"], d["e2_id"])
    e2_id = min(d["e1_id"], d["e2_id"])
    name = d["name"]
    description = d["description"]
    config = d["config"]
    # if the embedding ids are the same
    if e1_id == e2_id:
        return jsonify({"message": "Cannot align embeddings with themselves"}), 400
    # if the provided e1_id is not in the database
    e1 = query_db("SELECT wv_path FROM embeddings WHERE id = ?", (e1_id,), one=True)
    if e1 is None:
        return jsonify({"message": f"Invalid embedding id: {e1_id}"}), 400
    e1wvp = Path(e1["wv_path"])
    # if the provided e2_id is not in the database
    e2 = query_db("SELECT wv_path FROM embeddings WHERE id = ?", (e2_id,), one=True)
    if e2 is None:
        return jsonify({"message": f"Invalid embedding id: {e2_id}"}), 400
    e2wvp = Path(e2["wv_path"])
    # get the wv object for the first embedding
    wv1 = WordVectors.from_file(e1wvp)
    # get the wv object for the second embedding
    wv2 = WordVectors.from_file(e2wvp)
    # get the words and vectors for the second alignment
    # generate the alignment (computes the two alignment matrices, the shifts, and the distances)
    a = Alignment.from_wv_and_config(wv1, wv2, config)
    # generate a random filename for the alignment
    a_fn = Path(str(uuid.uuid4()) + ".pickle")
    a_path = Path(app.config["ALIGNMENTS_FOLDER"]) / a_fn
    # dump the alignment to a_path
    with open(a_path, "wb") as f:
        pickle.dump(a, f)
    # create entry in alignments for the alignment, return the id
    a_id = write_db_ret_last(
        "INSERT INTO alignments (name, description, e1_id, e2_id, a_path) VALUES (?, ?, ?, ?, ?)",
        (name, description, e1_id, e2_id, str(a_path)),
    )
    return jsonify({"message": "Alignment generated", "id": a_id}), 201


@app.route("/getAlignments", methods=["POST"])
def get_alignments():
    """
    gets all the alignments for a pair of embeddings
    """
    # get request json
    d = request.get_json()
    e1_id = max(d["e1_id"], d["e2_id"])
    e2_id = min(d["e1_id"], d["e2_id"])
    # if the embedding ids are the same
    if e1_id == e2_id:
        return jsonify({"message": "Cannot align embeddings with themselves"}), 400
    # if the provided e1_id is not in the database
    if query_db("SELECT * FROM embeddings WHERE id = ?", (e1_id,), one=True) is None:
        return jsonify({"message": f"Invalid embedding id: {e1_id}"}), 400
    # if the provided e2_id is not in the database
    if query_db("SELECT * FROM embeddings WHERE id = ?", (e2_id,), one=True) is None:
        return jsonify({"message": f"Invalid embedding id: {e2_id}"}), 400
    # get the alignments
    r = query_db(
        "SELECT * FROM alignments WHERE e1_id = ? AND e2_id = ?", (e1_id, e2_id)
    )
    return jsonify({"message": "Alignments retrieved", "alignments": r}), 200


# get an alignment by its id
@app.route("/getAlignment", methods=["POST"])
def get_alignment():
    """
    gets an alignment by its id
    """
    # get request json
    d = request.get_json()
    # check if the request has an id
    if "id" not in d:
        return jsonify({"message": "No id provided"}), 400
    a_id = d["id"]
    # if the provided alignment id is not in the database
    if query_db("SELECT * FROM alignments WHERE id = ?", (a_id,), one=True) is None:
        return jsonify({"message": "Invalid alignment id"}), 400
    # get the alignment from the database
    a = query_db("SELECT * FROM alignments WHERE id = ?", (a_id,), one=True)
    return jsonify({"message": "Alignment retrieved", "alignment": a}), 200


@app.route("/getAlignmentConfigs")
def get_alignment_configs():
    """
    returns a list containing default alignment configurations
    """
    alignment_configs_path = Path("app/metadata/alignment_configs_example.json")
    # check path exists
    if not alignment_configs_path.exists():
        raise ValueError("Could not find alignment configs file")
    with alignment_configs_path.open() as f:
        return jsonify(json.load(f))


@app.route("/getTopShiftedWords", methods=["POST"])
def get_top_shifted_words():
    """
    gets the top shifted words for an alignment
    """
    # get request json
    d = request.get_json()
    # check if the request has an id
    if "id" not in d:
        return jsonify({"message": "No id provided"}), 400
    a_id = d["id"]
    # if the provided alignment id is not in the database
    r = query_db("SELECT * FROM alignments WHERE id = ?", (a_id,), one=True)
    if r is None:
        return jsonify({"message": "Invalid alignment id"}), 400
    # check if the request has a desired number of words
    if "num_words" not in d:
        return jsonify({"message": "No number of words provided"}), 400
    num_words = d["num_words"]
    # get the top shifted words
    a_path = Path(r["a_path"])
    # load alignment from a_path
    with open(a_path, "rb") as f:
        a = pickle.load(f)
    ts = a.top_shifted_words(num_words)
    return jsonify({"message": "Top shifted words retrieved", "shifted_words": ts}), 200

@app.route("/getExampleSentences", methods=["POST"])
def get_example_sentences():
    """
    given a word and an alignment id
    gets sentences from the original plaintexts showcasing
    semantically dissimilar usage of the word
    """
    # get request json
    d = request.get_json()
    # check if the request has an id
    if "id" not in d:
        return jsonify({"message": "No alignment id provided"}), 400
    a_id = d["id"]
    # get the alignment from the database
    a = query_db("SELECT e1_id, e2_id, a_path FROM alignments WHERE id = ?", (a_id,), one=True)
    # if the provided alignment id is not in the database
    if a is None:
        return jsonify({"message": "Invalid alignment id"}), 400
    # check if the request has a word
    if "word" not in d:
        return jsonify({"message": "No word provided"}), 400
    word = d["word"]
    e1_id = a["e1_id"]
    e2_id = a["e2_id"]
    a_path = Path(a["a_path"])

    # generate examples
    # load alignment from disk
    with open(a_path, "rb") as f:
        al = pickle.load(f)
    # get wordvectors and plaintext ids associated with the specified embeddings
    pt1_d = query_db(
        "SELECT pt_id, wv_path FROM embeddings WHERE id = ?", (e1_id,), one=True
    )
    pt2_d = query_db(
        "SELECT pt_id, wv_path FROM embeddings WHERE id = ?", (e2_id,), one=True
    )
    pt1_id = pt1_d["pt_id"]
    pt2_id = pt2_d["pt_id"]
    e1_v_po = Path(pt1_d["wv_path"])
    e2_v_po = Path(pt2_d["wv_path"])
    # get the path to the scrubbed plaintext and occs file from the database (for pt1)
    r = query_db("SELECT s_path, occ_path FROM plaintexts WHERE id = ?", (pt1_id,), one=True)
    occ1_po = Path(r["occ_path"])
    s1_po = Path(r["s_path"])
    # get the path to the scrubbed plaintext and occs file from the database (for pt2)
    r = query_db("SELECT s_path, occ_path FROM plaintexts WHERE id = ?", (pt2_id,), one=True)
    occ2_po = Path(r["occ_path"])
    s2_po = Path(r["s_path"])
    # load the occs files from disk
    with open(occ1_po, "rb") as f:
        occs1 = pickle.load(f)
    with open(occ2_po, "rb") as f:
        occs2 = pickle.load(f)
    # load the wv objects for both embeddings from disk
    wv1 = WordVectors.from_file(e1_v_po)
    wv2 = WordVectors.from_file(e2_v_po)
    sents = Alignment.get_example_sentences(word, occs1, occs2, s1_po, s2_po, al.Q, wv1, wv2)
    return jsonify({"message": "Example sentences retrieved", "sentences": sents}), 200

@app.route("/getContext", methods=["POST"])
def get_context():
    """
    gets a context for a word
    """
    # get request json
    d = request.get_json()
    # check if the request has an alignment id
    if "a_id" not in d:
        return jsonify({"message": "No alignment id provided"}), 400
    # get the alignment id
    a_id = d["a_id"]
    # check if the alignment id is valid
    db_r = query_db("SELECT * FROM alignments WHERE id = ?", (a_id,), one=True)
    if db_r is None:
        return jsonify({"message": "Invalid alignment id"}), 400
    # check if the request has a word
    if "word" not in d:
        return jsonify({"message": "No word provided"}), 400
    word = d["word"]
    # check if the request has a first
    if "first" not in d:
        return (
            jsonify(
                {
                    "message": "No first flag supplied, cannot know if target word is in first or second context of alignment"
                }
            ),
            400,
        )
    if d["first"] == "true":
        first = True
    elif d["first"] == "false":
        first = False
    # check if the request has a desired number of neighbors
    if "neighbors" in d:
        n_neighbors = 10

    al_p = Path(db_r["a_path"])
    # load pickled alignment from disk
    with open(al_p, "rb") as f:
        a = pickle.load(f)
    words, distances, v = a.get_context(word, first, n_neighbors)
    # zip words and distances into dict
    zipped = list(zip(words, distances))
    v_2d = PCA(n_components=2).fit_transform(v)
    return (
        jsonify(
            {"message": "Context retrieved", "neighbors": zipped, "vectors": v_2d.tolist()}
        ),
        200,
    )


@app.route("/getAllAlignmentVectors")
def get_all_alignment_vectors():
    """
    gets all alignment vectors
    """
    # get all alignment vectors
    r = query_db("SELECT count(word) FROM a_vectors")
    return jsonify({"message": "All alignment vectors retrieved", "vectors": r}), 200


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host address of the app"
    )
    parser.add_argument(
        "--production", action="store_true", help="Run in production mode (debug off)."
    )
    args = parser.parse_args()

    debug = not args.production
    app.run(host="0.0.0.0", debug=debug)
