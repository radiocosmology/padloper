# https://flask.palletsprojects.com/en/2.0.x/quickstart/

from padloper.structure import *
from re import split
from flask import Flask, request
from flask.scaffold import F

from markupsafe import escape


# see https://stackoverflow.com/a/27876800

app = Flask(__name__)

def read_filters(filters):
    """Return a list of filter tuples given a URL string containing the
    filters.

    :param filters: A string consisting of , and ;
    where each substring separated by a ; is a filter, and each substring
    separated by , is a parameter for a filter.

    :type filters: str
    :return: A list of tuples
    :rtype: list[tuple]
    """

    if filters is not None and filters != '':

        split_by_semicolon = filters.split(';')
        
        return [tuple(f.split(',')) for f in split_by_semicolon]

    else:
        return None


@app.route("/api/")
def hello_world():
    return "Hello, World!"

@app.route("/api/components_id/<id>")
def get_component_by_id(id):
    return str(Component.from_id(escape(id)))

@app.route("/api/components_name/<name>")
def get_component_by_name(name):
    return {
        'result': Component.get_as_dict(str(escape(name)))
    }

@app.route("/api/component_list")
def get_component_list():
    component_range = escape(request.args.get('range'))
    
    range_bounds = tuple(map(int, component_range.split(';')))

    order_by = escape(request.args.get('orderBy'))

    order_direction = escape(request.args.get('orderDirection'))

    filters = request.args.get('filters')

    filter_triples = read_filters(filters)

    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

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

    return {'result': types}
    

@app.route("/api/component_type_list")
def get_component_type_list():
    component_range = escape(request.args.get('range'))
    order_by = escape(request.args.get('orderBy'))
    order_direction = escape(request.args.get('orderDirection'))
    name_substring = escape(request.args.get('nameSubstring'))

    range_bounds = tuple(map(int, component_range.split(';')))

    # A bunch of assertions to make sure everything is as intended.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    # query to padloper
    component_types = ComponentType.get_list(
        range=range_bounds, 
        order_by=order_by,
        order_direction=order_direction,
        name_substring=name_substring
    )

    return {
        'result': [
            {
                'name': c.name, 
                'id': c.id,
                'comments': c.comments
            }   
            for c in component_types
        ] 
    }


@app.route("/api/component_type_count")
def get_component_type_count():
    
    name_substring = escape(request.args.get('nameSubstring'))

    return {'result': ComponentType.get_count(name_substring=name_substring)}


@app.route("/api/component_revision_list")
def get_component_revision_list():
    list_range = escape(request.args.get('range'))
    order_by = escape(request.args.get('orderBy'))
    order_direction = escape(request.args.get('orderDirection'))

    filters = request.args.get('filters')

    filter_tuples = read_filters(filters)

    range_bounds = tuple(map(int, list_range.split(';')))

    # A bunch of assertions to make sure everything is as intended.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    # query to padloper
    component_revisions = ComponentRevision.get_list(
        range=range_bounds, 
        order_by=order_by,
        order_direction=order_direction,
        filters=filter_tuples,
    )

    return {
        'result': [
            {
                'name': c.name, 
                'id': c.id,
                'comments': c.comments,
                'allowed_type': {
                    'name': c.allowed_type.name,
                    'comments': c.allowed_type.comments,
                },
            }   
            for c in component_revisions
        ] 
    }

@app.route("/api/component_revision_count")
def get_component_revision_count():
    
    filters = request.args.get('filters')

    filter_tuples = read_filters(filters)

    return {
        'result': ComponentRevision.get_count(filters=filter_tuples)
        }