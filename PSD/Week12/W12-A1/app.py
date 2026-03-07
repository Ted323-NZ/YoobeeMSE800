from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def hello_flask():
    return "Hello Flask Framework!"


@app.route("/bye")
def bye_flask():
    return "Bye Flask Framework!"


@app.route("/user")
@app.route("/user/")
@app.route("/user/<username>")
def greet_user(username=None):
    name = (username or request.args.get("username", "")).strip() or "Guest"
    return f"Hello, {name}!"


if __name__ == "__main__":
    app.run(debug=True)
