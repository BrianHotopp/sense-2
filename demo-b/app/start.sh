#!/bin/bash
# if we passed the clean-start flag, then we should remove the old data
# we do this by setting the clean start flag in the environment,
# which is later loaded in the flask app and used to determine if we should remove
export FLASK_CLEAN_START=false
if [ "$1" = "--clean-start" ]; then
    export FLASK_CLEAN_START=true
fi

python3 app/run_gunicorn.py --bind localhost:5000 wsgi:app --timeout 99999999 --workers 2
