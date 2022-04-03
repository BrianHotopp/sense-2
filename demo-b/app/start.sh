#!/bin/sh
python3 app/run_gunicorn.py --bind localhost:5000 wsgi:app --timeout 99999999
