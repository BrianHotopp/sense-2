#!/home/gruppi/projects/s4-demo/venv/bin/python3
# -*- coding: utf-8 -*-
import re
import sys
from gunicorn.app.wsgiapp import run

# Run run_gunicorn.py --bind localhost:5000 wsgi:app
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(run())
