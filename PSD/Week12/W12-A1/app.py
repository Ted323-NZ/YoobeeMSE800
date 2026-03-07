from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_flask():
    return "Hello Flask Framework!"


@app.route("/bye")
def bye_flask():
    return "Bye Flask Framework!"


@app.route("/user/<username>")
def greet_user(username):
    return f"Hello, {username}!"


if __name__ == "__main__":
    app.run(debug=True)
