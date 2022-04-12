import http.client
import itertools
import json
import requests

def upload(filepath, ptname, desc):
    """ "
    uploads a plaintext file to the server
    """
    url = "http://127.0.0.1:5000/uploadFile"
    files = {'file': open(filepath, 'rb')} 
    data = {'name': ptname, 'description': desc}
    # convert data to string
    s = json.dumps(data)

    values = {'data':s}
    r = requests.post(url, files=files, data=values)
    # get result as python dict
    res = r.json()
    print("uploaded file:", res)
    print(res)
    return res



def embed(
    conn, id, name="default word2vec", desc="vector size 100, default window size"
):
    headers = {"Content-Type": "application/json"}
    pl = {"id": id, "name": name, "description": desc}
    conn.request("POST", "/generateEmbedding", json.dumps(pl), headers)
    # get result as json and return
    res = conn.getresponse()
    data = res.read()
    decoded = data.decode("utf-8")
    # convert to json
    json_data = json.loads(decoded)
    return json_data


def align_global_default(conn, id1, id2):
    pl = {
        "e1_id": id1,
        "e2_id": id2,
        "name": "global",
        "description": "global alignment default settings",
        "config": {"alignment_type": "global", "args": {}, "neighbors": 5},
    }
    headers = {"Content-Type": "application/json"}
    conn.request("POST", "/generateAlignment", json.dumps(pl), headers)
    pass


def align_s4_default(conn, id1, id2):
    pl = {
	"e1_id":id1,
	"e2_id":id2,
	"name":"s4",
	"description":"s4 alignment default settings",
	"config":{
		"alignment_type": "s4",
		"args": {},
		"neighbors": 5
}
}

    headers = {"Content-Type": "application/json"}
    conn.request("POST", "/generateAlignment", json.dumps(pl), headers)


def align_noise_aware_default(conn, id1, id2):
    pl = {
	"e1_id":id1,
	"e2_id":id2,
	"name":"noise-aware",
	"description":"noise-aware alignment default settings",
	"config":{
		"alignment_type": "noise-aware",
		"args": {},
		"neighbors": 5
}
}

    headers = {"Content-Type": "application/json"}
    conn.request("POST", "/generateAlignment", json.dumps(pl), headers)


if __name__ == "__main__":
    import os
    import sys

    # take the first argument as the directory where our files are

    if len(sys.argv) < 2:
        print("Usage: python3 autogen.py <directory>")
        exit(1)
    # try to connect to the server
    # upload the files in the directory
    plaintext_ids = []
    for file in os.listdir(sys.argv[1]):
        if file.endswith(".txt"):
            print("uploading file: " + file)
            # get the full path to the file
            filepath = os.path.join(sys.argv[1], file)
            # upload
            res = upload(filepath, file, "automatically generated description")
            # get the id of the file
            plaintext_ids.append(str(res["id"]))
    # now we have uploaded all the files, we can generate the vectors
    # embed each file with default word2vec parameters
    embedding_ids = []
    for id in plaintext_ids:
        conn = http.client.HTTPConnection("127.0.0.1:5000")
        print("embedding file: " + id)
        res = embed(conn, id)
        embedding_ids.append(str(res["id"]))
        conn.close()
    # generate alignments
    print("generating alignments")
    # for every combination of embedding, generate alignments
    for id1, id2 in itertools.combinations(embedding_ids, 2):
        if id1 != id2:
            conn = http.client.HTTPConnection("127.0.0.1:5000")
            align_global_default(conn, id1, id2)
            conn.close()
            conn = http.client.HTTPConnection("127.0.0.1:5000")
            align_s4_default(conn, id1, id2)
            conn.close()
            conn = http.client.HTTPConnection("127.0.0.1:5000")
            align_noise_aware_default(conn, id1, id2)
            conn.close()