# https://flask.palletsprojects.com/en/2.0.x/quickstart/

from flask import Flask, request

from markupsafe import escape

from structure import *

app = Flask(__name__)

@app.route("/api/")
def hello_world():
    return "Hello, World!"

@app.route("/api/graph")
def graph_load():

    return {'a': f'{g.V().toList()}'}

@app.route("/api/components_id/<id>")
def get_component_by_id(id):
    return str(Component.from_id(escape(id)))

@app.route("/api/components_name/<name>")
def get_component_by_name(name):
    return str(Component.from_db(str(escape(name))))

@app.route("/api/component_list")
def get_component_list():
    component_range = escape(request.args.get('range'))
    
    range_bounds = tuple(map(int, component_range.split(',')))

    assert len(range_bounds) == 2

    components = Component.get_list(range=range_bounds)
    
    return {'result': [{'name': c.name, 'id': c.id} for c in components] }

@app.route("/api/component_count")
def get_component_count():
    return {'result': Component.get_count()}