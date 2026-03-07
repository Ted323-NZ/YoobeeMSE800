from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_flask():
    return "Hello Flask Framework!"


@app.route("/bye")
def bye_flask():
    return "Bye Flask Framework!"


if __name__ == "__main__":
    app.run(debug=True)
