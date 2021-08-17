# https://flask.palletsprojects.com/en/2.0.x/quickstart/

from ..padloper.structure import *
from re import split
from flask import Flask, request
from flask.scaffold import F

from markupsafe import escape


# see https://stackoverflow.com/a/27876800

app = Flask(__name__)

def read_filters(filters):
    """Return a list of filter 3-tuples given a URL string containing the
    filters.

    :param filters: A string of the format 
    <name>,<ctype>,<revision>;...;<name>,<ctype>,<revision>
    where each substring separated by a ; is a filter.

    :type filters: str
    :return: A list of 3-tuples of the format (<name>, <ctype>, <revision>)
    :rtype: list[tuple[str, str, str]]
    """

    if filters is not None and filters != '':

        split_by_semicolon = filters.split(';')
        
        return [tuple(f.split(',')) for f in split_by_semicolon]

    else:
        return None


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
    
    range_bounds = tuple(map(int, component_range.split(';')))

    assert len(range_bounds) == 2

    order_by = escape(request.args.get('orderBy'))

    order_direction = escape(request.args.get('orderDirection'))

    filters = request.args.get('filters')

    filter_triples = read_filters(filters)

    assert order_by in {'name', 'component_type', 'revision'} \
        and order_direction in {'asc', 'desc'}

    components = Component.get_list(
        range=range_bounds, 
        order_by=order_by,
        order_direction=order_direction,
        filters=filter_triples,
    )
    
    return {
        'result': [
            {
                'name': c.name, 
                'id': c.id,
                'component_type': {
                    'name': c.component_type.name,
                    'comments': c.component_type.comments,
                },
                'revision': {
                    'name': c.revision.name if c.revision is not None else None,
                    'comments': c.revision.comments \
                        if c.revision is not None else None,
                }
            }   
            for c in components
        ] 
    }


@app.route("/api/component_count")
def get_component_count():

    filters = request.args.get('filters')

    filter_triples = read_filters(filters)

    return {'result': Component.get_count(filters=filter_triples)}


@app.route("/api/component_types_and_revisions")
def get_component_types_and_revisions():

    types = ComponentType.get_names_of_types_and_revisions()

    print(types)

    return {
        'result': types
    }
