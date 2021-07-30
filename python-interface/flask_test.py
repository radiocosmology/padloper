# https://flask.palletsprojects.com/en/2.0.x/quickstart/

from flask import Flask

from graph_connection import g

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/graph")
def graph_load():
    return f"<p>The list of vertices in the graph: {g.V().toList()}</p>"