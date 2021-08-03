# https://flask.palletsprojects.com/en/2.0.x/quickstart/

from flask import Flask

from markupsafe import escape

from structure import *

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/graph")
def graph_load():

    return {'a': f'{g.V().toList()}'}

@app.route("/components_id/<id>")
def get_component_by_id(id):
    return str(Component.from_id(escape(id)))

@app.route("/components_name/<name>")
def get_component_by_name(name):
    return str(Component.from_db(str(escape(name))))

@app.route("/components_list/&limit=<limit>")
def get_component_list(limit):
    
    components = Component.get_list(limit=limit)

    print(components)

    return {'result': [{'name': c.name, 'id': c.id} for c in components] }