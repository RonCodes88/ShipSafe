import flask
from flask import request

app = flask.Flask(__name__)

@app.route("/read")
def read_file():
    filename = request.args.get("f")
    with open("/var/data/" + filename, "r") as f:
        return f.read()
