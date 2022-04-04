from ctypes import alignment
import time
from tkinter import W
import uuid
from flask import Flask, request, jsonify, current_app, session, g
import os
import argparse
import numpy as np
import pickle
from pyparsing import Word
from scipy.spatial.distance import cosine
from sklearn.decomposition import PCA
import json
import sqlite3
import app.preprocessing.generate_embeddings.embed as embed
from app.preprocessing.generate_examples.alignment.align import Alignment
from preprocessing.WordVectors import WordVectors
from werkzeug.utils import secure_filename
from flask_cors import CORS
from pathlib import Path

DATABASE = "app/db/demo_app.db"
UPLOAD_FOLDER = "app/uploads"
SCRUBBED_FOLDER = "app/scrubbed"
ALLOWED_EXTENSIONS = set(["txt"])

sqlite3.register_adapter(np.float64, float)


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


def fetch_alignment_configs():
    """
    return premade alignment configs
    """


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SCRUBBED_FOLDER"] = SCRUBBED_FOLDER
CORS(app, resources={r"/*": {"origins": "*"}})
# init_db()


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
    return embeddings
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
    # if user does not select file, browser also
    # submit an empty part without filename
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
        embed.initial_scrub(f_path, s_path)
        # insert dataset_name, dataset_description, f_path, and s_path into the database
        dataset_id = write_db_ret_last(
            "INSERT INTO plaintexts (name, description, p_path, s_path) VALUES (?, ?, ?, ?)",
            (dataset_name, dataset_description, str(f_path), str(s_path)),
        )
        # get id of the dataset
        return jsonify({"message": "File successfully uploaded", "id": dataset_id}), 201
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
    if query_db("SELECT * FROM plaintexts WHERE id = ?", (pt_id,), one=True) is None:
        return jsonify({"message": "Invalid file id"}), 400
    # get the path to the plaintext from the database
    pt_p = query_db("SELECT s_path FROM plaintexts WHERE id = ?", (pt_id,), one=True)[
        "s_path"
    ]
    pt_po = Path(pt_p)
    # generate the embedding
    wv = embed.generate_embedding(pt_po)
    # create entry in embeddings for the embedding, return the id
    e_id = write_db_ret_last(
        "INSERT INTO embeddings (name, description, pt_id) VALUES (?, ?, ?)",
        (e_name, e_description, pt_id),
    )

    # add the vectors of wv to the database
    for word in wv.get_words():
        # serialize the vector
        v = pickle.dumps(wv.get_vector(word))
        write_db(
            "INSERT INTO e_vectors (e_id, word, vector) VALUES (?, ?, ?)",
            (e_id, word, v),
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
    if query_db("SELECT * FROM embeddings WHERE id = ?", (e1_id,), one=True) is None:
        return jsonify({"message": f"Invalid embedding id: {e1_id}"}), 400
    # if the provided e2_id is not in the database
    if query_db("SELECT * FROM embeddings WHERE id = ?", (e2_id,), one=True) is None:
        return jsonify({"message": f"Invalid embedding id: {e2_id}"}), 400
    # get the words and vectors for the first alignment
    r = query_db("SELECT word, vector FROM e_vectors WHERE e_id = ?", (e1_id,))
    words1 = [x["word"] for x in r]
    vectors1 = np.array([pickle.loads(x["vector"]) for x in r])
    # get the words and vectors for the second alignment
    r = query_db("SELECT word, vector FROM e_vectors WHERE e_id = ?", (e2_id,))
    words2 = [x["word"] for x in r]
    vectors2 = np.array([pickle.loads(x["vector"]) for x in r])
    # load into the WordVector object
    wv1 = WordVectors(words1, vectors1)
    wv2 = WordVectors(words2, vectors2)
    # generate the alignment (computes the two alignment matrices, the shifts, and the distances)
    a = Alignment.from_wv_and_config(wv1, wv2, config)
    # create entry in alignments for the alignment, return the id
    a_id = write_db_ret_last(
        "INSERT INTO alignments (name, description, e1_id, e2_id) VALUES (?, ?, ?, ?)",
        (name, description, e1_id, e2_id),
    )
    # write the vectors in a into the database, along with the shifts and dists
    # print how many words are in the alignment
    # prepared statement for inserting into the database
    start = time.time()
    ps = "INSERT INTO a_vectors (a_id, first, word, vector) VALUES (?, ?, ?, ?)"
    # get datbase cursor
    c = get_db().cursor()
    ps_args = [
        (a_id, True, a.common[i], pickle.dumps(a.v1[i])) for i in range(len(a.common))
    ]
    c.executemany(ps, ps_args)
    ps_args = [
        (a_id, False, a.common[i], pickle.dumps(a.v2[i])) for i in range(len(a.common))
    ]
    c.executemany(ps, ps_args)
    # insert into shifts
    ps = "INSERT INTO shifts (a_id, word, shift) VALUES (?, ?, ?)"
    ps_args = [(a_id, a.common[i], a.shifts[i]) for i in range(len(a.common))]
    c.executemany(ps, ps_args)
    # insert into distances
    ps = "INSERT INTO dists (a_id, word1, word2, dist) VALUES (?, ?, ?, ?)"
    ps_args = [
        (a_id, a.common[i], a.common[j], a.dists[i, j])
        for i in range(len(a.common))
        for j in range(len(a.common))
    ]
    c.executemany(ps, ps_args)
    # commit changes
    get_db().commit()
    end = time.time()
    print(f"{len(a.common)} words in alignment, {end-start} seconds")
    return jsonify({"message": "Alignment generated", "id": a_id}), 201

    # get the existing alignments for a pair of embeddings


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
    if query_db("SELECT * FROM alignments WHERE id = ?", (a_id,), one=True) is None:
        return jsonify({"message": "Invalid alignment id"}), 400
    # check if the request has a desired number of words
    if "num_words" not in d:
        return jsonify({"message": "No number of words provided"}), 400
    num_words = d["num_words"]
    # get the top shifted words
    r = query_db(
        "SELECT word, shift FROM shifts WHERE a_id = ? ORDER BY shift DESC LIMIT ?",
        (a_id, num_words),
    )
    return jsonify({"message": "Top shifted words retrieved", "shifted_words": r}), 200


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
    if query_db("SELECT * FROM alignments WHERE id = ?", (a_id,), one=True) is None:
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
    first = d["first"]
    # check if the request has a desired number of neighbors
    if "neighbors" not in d:
        n_neighbors = 10
    else:
        n_neighbors = d["neighbors"]
    if first:
        # our target word is in the first context
        # get the closest n neighbors in the second context
        r = query_db(
            "SELECT word2 as neighbor, dist FROM dists WHERE a_id = ? AND word1 = ? ORDER BY dist ASC LIMIT ?",
            (a_id, word, n_neighbors),
        )
    else:
        # our target word is in the second context
        # get the closest n neighbors in the first context
        r = query_db(
            "SELECT word1 as neighbor, dist FROM dists WHERE a_id = ? AND word2 = ? ORDER BY dist ASC LIMIT ?",
            (a_id, word, n_neighbors),
        )
    # get the vectors for the neighbors
    v = []
    for i in range(len(r)):
        if first:
            vecb = query_db(
                "SELECT vector FROM a_vectors WHERE a_id = ? AND first = ? AND word = ?",
                (a_id, False, r[i]["neighbor"]),
                one=True,
            )
            # unpack the vector
            v.append(pickle.loads(vecb["vector"]))
        else:
            vecb = query_db(
                "SELECT vector FROM a_vectors WHERE a_id = ? AND first = ? AND word = ?",
                (a_id, True, r[i]["neighbor"]),
                one=True,
            )
            # unpack the vector
            v.append(pickle.loads(vecb["vector"]))
    # return the neighbors and their vectors
    v = np.array(v)
    v_2d = PCA(n_components=2).fit_transform(v)
    return (
        jsonify(
            {"message": "Context retrieved", "neighbors": r, "vectors": v_2d.tolist()}
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
