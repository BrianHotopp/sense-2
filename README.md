# SenSE demo source code
This is the source code for Sense 2 - an extansion of [SenSE](https://sense.mgruppi.me) - the Semantic Shift Exploration toolkit.

Run backend
python3 app/run_gunicorn.py --bind localhost:5000 wsgi:app --timeout 500


Run frontend:
cd demo-f
npm run dev --host