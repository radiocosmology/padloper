# https://flask.palletsprojects.com/en/2.0.x/quickstart/

from flask import Flask

from markupsafe import escape

from structure import *

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/graph")
def graph_load():
    return f"<p>The list of vertices in the graph: {g.V().toList()}</p>"

@app.route("/components_id/<id>")
def get_component_by_id(id):
    return str(Component.from_id(escape(id)))

@app.route("/components_name/<name>")
def get_component_by_name(name):
    return str(Component.from_db(str(escape(name))))