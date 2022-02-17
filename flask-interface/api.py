# https://flask.palletsprojects.com/en/2.0.x/quickstart/

from padloper.structure import *
from re import split
from flask import Flask, request
from flask.scaffold import F

from markupsafe import escape
from time import time


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
                'id': c.id(),
                'type': {
                    'name': c.type.name,
                    'comments': c.type.comments,
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
                'id': c.id(),
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
                'id': c.id(),
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


@app.route("/api/property_type_list")
def get_property_type_list():
    list_range = escape(request.args.get('range'))
    order_by = escape(request.args.get('orderBy'))
    order_direction = escape(request.args.get('orderDirection'))
    name_substring = escape(request.args.get('nameSubstring'))

    range_bounds = tuple(map(int, list_range.split(';')))

    # A bunch of assertions to make sure everything is as intended.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    # query to padloper
    property_types = PropertyType.get_list(
        range=range_bounds, 
        order_by=order_by,
        order_direction=order_direction,
        name_substring=name_substring
    )

    return {
        'result': [
            {
                'name': pt.name, 
                'id': pt.id(),
                'units': pt.units,
                'allowed_regex': pt.allowed_regex,
                'n_values': pt.n_values,
                'allowed_types': [ t.name for t in pt.allowed_types ],
                'comments': pt.comments,
            }   
            for pt in property_types
        ] 
    }


@app.route("/api/component_set_property")
def set_component_property():

    val_name = escape(request.args.get('name'))
    val_property_type = escape(request.args.get('propertyType'))
    val_time = int(escape(request.args.get('time')))
    val_uid = escape(request.args.get('uid'))
    val_comments = escape(request.args.get('comments'))
    val_value_count = int(escape(request.args.get('valueCount')))
    val_values = escape(request.args.get('values'))

    values = val_values.split(';')

    # if this is false, then you put a semicolon in a value name!!!
    assert len(values) == val_value_count

    property_type = PropertyType.from_db(val_property_type)

    component = Component.from_db(val_name)

    property = Property(values=values, property_type=property_type)

    component.set_property(
        property=property, 
        time=val_time, 
        uid=val_uid, 
        comments=val_comments
    )

    return {'result': True}



@app.route("/api/component_add_connection")
def add_component_connection():

    val_name1 = escape(request.args.get('name1'))
    val_name2 = escape(request.args.get('name2'))
    val_time = int(escape(request.args.get('time')))
    val_uid = escape(request.args.get('uid'))
    val_comments = escape(request.args.get('comments'))

    c1, c2 = Component.from_db(val_name1), Component.from_db(val_name2)

    already_connected = False

    try:
        c1.connect(
            component=c2, time=val_time, uid=val_uid, comments=val_comments
        )
    except ComponentsAlreadyConnectedError:
        already_connected = True

    return {'result': not already_connected}


@app.route("/api/get_all_connections_at_time")
def get_all_connections_at_time():

    val_name = escape(request.args.get('name'))
    val_time = int(escape(request.args.get('time')))

    c = Component.from_db(val_name)

    connections = c.get_all_connections_at_time(val_time)

    return {
        'result': [
            {
                'inVertexName': conn.inVertex.name,
                'outVertexName': conn.outVertex.name,
                'id': conn.id(),
            }   
            for conn in connections
        ] 
    }