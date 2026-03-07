# Week 12 - Activity 1 - Flask framework

## Task
Create a Flask web app that shows:

`Hello Flask Framework!`

## Files
- `app.py`: minimal Flask application
- `requirements.txt`: Flask dependency

## Run
```bash
cd /Users/ginoted/Documents/GitHub/YoobeeMSE800/PSD/Week12/W12-A1
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug
```

Then open:

`http://127.0.0.1:5000/`

Because the file is named `app.py`, `flask run --debug` also works after activation.

## Routes

- `/` -> `Hello Flask Framework!`
- `/bye` -> `Bye Flask Framework!`
- `/user/<username>` -> `Hello, <username>!` (example: `/user/alice`)
