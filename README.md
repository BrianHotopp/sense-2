# SenSE demo source code
This is the source code for Sense 2 - an extension of [SenSE](https://sense.mgruppi.me) - the Semantic Shift Exploration toolkit.

# Usage

The app is a Vue single-page app that communicates with a Flask+SQLite backend.

To run the backend (from project root):
Create a virtual environment:
`cd backend`
`python3 -m venv venv`
Activate the virtual environment (Unix/MacOS):
`source venv/bin/activate`
Install dependencies:
`pip3 install -r requirements.txt`
Start the flask server
`./app/start.sh --clean-start`
The `--clean-start` flag tells the backend to delete existing artifacts and recreate necessary tables in the SQLite DB. On subsequent runs, exclude the flag to have added texts/embeddings/alignments persist:
`./app/start.sh`

Run frontend (from project root):
`cd demo-f`
Install dependencies:
`npm install`
Start the development server on localhost (defaults to `http://localhost:3000/`)
`npm run dev --host`
