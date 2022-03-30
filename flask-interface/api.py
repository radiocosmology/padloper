# https://flask.palletsprojects.com/en/2.0.x/quickstart/

from padloper.structure import *
from re import split
from flask import Flask, request
from flask.scaffold import F

from markupsafe import escape
from time import time


# see https://stackoverflow.com/a/27876800

# The flask application
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

# Can also implement something like this.
# @app.route("/api/components_id/<id>")
# def get_component_by_id(id):
#     return str(Component.from_id(escape(id)))



@app.route("/api/components_name/<name>")
def get_component_by_name(name):
    """Given a name of a component, return a dictionary containing the
    dictionary representation of the component in its 'result' field.

    :param name: The component name
    :type name: str
    :return: Return a dictionary with a key/value pair of 'result' and the
    dictionary representation of the component with said name
    :rtype: dict
    """
    return {
        'result': Component.get_as_dict(str(escape(name)))
    }



@app.route("/api/component_list")
def get_component_list():
    """Given three URL parameters 'range', 'orderBy', 'orderDirection', 
    and 'filters', return a dictionary containing a key 'result' with its 
    corresponding value being an array of dictionary representations of each 
    component in the desired list.

    The URL parameters are:

    range - of the form "<int>;<int>" -- two integers split by a semicolon,
    where the first integer denotes the index first component to be considered
    in the list and the second integer denotes the last component to be shown
    in the list.

    orderBy - the field to order the component list by.

    orderDirection - either "asc" or "desc" for ascending/descending,
    respectively.

    filters - of the form "<str>,<str>,<str>;...<str>,<str>,<str>", consisting
    of three-tuples of strings with the tuples separated by semicolons and the
    tuples' contents separated by commas.

    :return: A dictionary containing a key 'result' with its corresponding value
    being an array of dictionary representations of each component in the
    desired list.
    :rtype: dict
    """

    # extract the component range from the url parameters
    component_range = escape(request.args.get('range'))
    
    # extract the min/max
    range_bounds = tuple(map(int, component_range.split(';')))

    # extract the orderBy
    order_by = escape(request.args.get('orderBy'))

    # extract the orderDirection
    order_direction = escape(request.args.get('orderDirection'))

    # extract the filters
    filters = request.args.get('filters')

    # read the filters, put them into the three-tuples
    filter_triples = read_filters(filters)

    # make sure that the range bounds only consist of a min/max, and that
    # the order direction is either asc or desc.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    components = Component.get_list(
        range=range_bounds, 
        order_by=order_by,
        order_direction=order_direction,
        filters=filter_triples,
    )
    
    # TODO: Why not use Component.get_as_dict?
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
    """Given a URL parameter 'filters', return a dictionary with a value 
    'result' and corresponding value being the number of components that satisfy
    said filters.

    filters - of the form "<str>,<str>,<str>;...;<str>,<str>,<str>", consisting
    of three-tuples of strings with the tuples separated by semicolons and the
    tuples' contents separated by commas.

    :return: A dictionary with a value 'result' and corresponding value being
    the number of components that satisfy the filters. 
    :rtype: dict
    """

    filters = request.args.get('filters')

    filter_triples = read_filters(filters)

    return {'result': Component.get_count(filters=filter_triples)}


@app.route("/api/component_types_and_revisions")
def get_component_types_and_revisions():
    """Return a dictionary with a value 'result' and corresponding value 
    being a list of all the component types and their corresponding revisions.

    # TODO: This should ideally never, ever be used. Querying every type and 
    # corresponding revision is a very bad idea. In the web interface, instead
    of fetching this URL, create a ComponentTypeAutocomplete and
    ComponentRevisionAutocomplete that will query the limited component list
    that has a min/max range instead.

    :return: A dictionary with a value 'result' and corresponding value 
    being a list of all the component types and their corresponding revisions.
    :rtype: dict
    """

    types = ComponentType.get_names_of_types_and_revisions()

    return {'result': types}
    

@app.route("/api/component_type_list")
def get_component_type_list():
    """Given three URL parameters 'range', 'orderBy', 'orderDirection', 
    and 'nameSubstring', return a dictionary containing a key 'result' with its 
    corresponding value being an array of dictionary representations of each 
    component type in the desired list.

    range - of the form "<int>;<int>" -- two integers split by a semicolon,
    where the first integer denotes the index first component type to be 
    considered in the list and the second integer denotes the last component 
    type to be shown in the list.

    orderBy - the field to order the component type list by, a string.

    orderDirection - either "asc" or "desc" for ascending/descending,
    respectively.

    nameSubstring - substring of the name of component types to consider.

    :return: A dictionary containing a key 'result' with its corresponding value
    being an array of dictionary representations of each component type in the
    desired list.
    :rtype: dict
    """

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
    """Given a URL parameter 'nameSubstring', return a dictionary with a value 
    'result' and corresponding value being the number of component types that 
    have said substring in their name.

    nameSubstring - substring of the name of component types to consider.

    :return: A dictionary with a value 'result' and corresponding value being
    the number of components that satisfies the name substring.
    :rtype: dict
    """
    
    name_substring = escape(request.args.get('nameSubstring'))

    return {'result': ComponentType.get_count(name_substring=name_substring)}


@app.route("/api/component_revision_list")
def get_component_revision_list():
    """Given three URL parameters 'range', 'orderBy', 'orderDirection', 
    and 'filters', return a dictionary containing a key 'result' with its 
    corresponding value being an array of dictionary representations of each 
    component revision in the desired list.

    The URL parameters are:

    range - of the form "<int>;<int>" -- two integers split by a semicolon,
    where the first integer denotes the index first component revision to be 
    considered in the list and the second integer denotes the last component 
    to be shown in the list.

    orderBy - the field to order the component revision list by.

    orderDirection - either "asc" or "desc" for ascending/descending,
    respectively.

    filters - of the form "<str>,<str>;...;<str>,<str>", consisting of 
    two-tuples of strings with the tuples separated by semicolons and the
    tuples' contents separated by commas.

    :return: A dictionary containing a key 'result' with its corresponding value
    being an array of dictionary representations of each component revision 
    in the desired list.
    :rtype: dict
    """
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
    """Given a URL parameter 'filters', return a dictionary with a value 
    'result' and corresponding value being the number of component types that 
    satisfy said filters.

    filters - of the form "<str>,<str>;...;<str>,<str>", consisting
    of three-tuples of strings with the tuples separated by semicolons and the
    tuples' contents separated by commas.

    :return: A dictionary with a value 'result' and corresponding value being
    the number of components that satisfy the filters. 
    :rtype: dict
    """

    filters = request.args.get('filters')

    filter_tuples = read_filters(filters)

    return {
        'result': ComponentRevision.get_count(filters=filter_tuples)
    }


@app.route("/api/property_type_list")
def get_property_type_list():
    """Given three URL parameters 'range', 'orderBy', 'orderDirection', 
    and 'filters', return a dictionary containing a key 'result' with its 
    corresponding value being an array of dictionary representations of each 
    property type in the desired list.

    The URL parameters are:

    range - of the form "<int>;<int>" -- two integers split by a semicolon,
    where the first integer denotes the index first property type to be 
    considered in the list and the second integer denotes the last property type 
    to be shown in the list.

    orderBy - the field to order the property type list by.

    orderDirection - either "asc" or "desc" for ascending/descending,
    respectively.

    filters - of the form "<str>,<str>;...;<str>,<str>", consisting of 
    two-tuples of strings with the tuples separated by semicolons and the
    tuples' contents separated by commas.

    :return: A dictionary containing a key 'result' with its corresponding value
    being an array of dictionary representations of each property type 
    in the desired list.
    :rtype: dict

    """
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
    property_types = PropertyType.get_list(
        range=range_bounds, 
        order_by=order_by,
        order_direction=order_direction,
        filters=filter_tuples,
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
    """Given the component name, property type, time, user ID, comments,
    the values associated with the property, along with the count of values,
    set a property for the component.

    The URL parameters are:

    name - the name of the component to set the property for.

    propertyType - the name of the property type of the property.

    time - the UNIX time for when the property is set.

    uid - the ID of the user that set the property.

    comments - the comments associated with the property set.

    values - the values of the property, of the form "<str>;<str>;...;<str>",
    separated by semicolons.

    valueCount - the number of values of the property.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """

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
    """Given the names of the two components to connect, the time to make the
    connection, the ID of the user making this connection, and the comments
    associated with the connection, connect the two components.

    The URL parameters are:

    name1 - the name of the first component

    name2 - the name of the second component

    time - the UNIX time for when the connection is made

    uid - the ID of the user that has made the connection

    comments - Comments associated with the connection

    :return: Return a dictionary with a key 'result' and value being a boolean
    that is True if and only if the components were not already connected
    beforehand.
    :rtype: dict
    """

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
    """Given a component name and a time to check all connections, return all 
    connections of the component at a certain time in dictionary format.

    The URL parameters are:

    name - the name of the component to query the connections for.

    time - the time to query the connections at.

    :return: Return a dictionary with a key 'result' and value being a list of
    dictionary representations for connections, given by the names of the two
    components connected, along with the ID of the edge in the DB.
    :rtype: dict
    """

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