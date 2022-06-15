# https://flask.palletsprojects.com/en/2.0.x/quickstart/

#from crypt import methods
from re import split
from flask import Flask, request
from flask.scaffold import F
from markupsafe import escape
from time import time
from padloper.structure import *


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
                    'comments': c.revision.comments
                    if c.revision is not None else None,
                }
            }
            for c in components
        ]
    }


@app.route("/api/set_component_type", methods=['POST'])
def set_component_type():
    """Given the component type name, and comments,
    set a component type to the serverside.

    The URL parameters are:

    name - the name of the component type.

    comments - the comments associated with the component type.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    val_name = escape(request.args.get('name'))
    val_comments = escape(request.args.get('comments'))

    # Need to initialize an instance of a component type first.
    component_type = ComponentType(val_name, val_comments)

    component_type.add()

    return {'result': True}


@app.route("/api/set_component_revision", methods=['POST'])
def set_component_revision():
    """Given the component revision name, component type and comments,
    set a component revision to the serverside.

    The URL parameters are:

    name - the name of the component revision.

    type - the name of the component type.

    comments - the comments associated with the component revision.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    val_name = escape(request.args.get('name'))
    val_type = escape(request.args.get('type'))
    val_comments = escape(request.args.get('comments'))

    # Query the database and return a ComponentType instance based on component type.
    component_type = ComponentType.from_db(val_type)

    # Need to initialize an instance of a component revision first.
    component_revision = ComponentRevision(
        val_name, component_type, val_comments)

    component_revision.add()

    return {'result': True}


@app.route("/api/set_component", methods=['POST'])
def set_component():
    """Given the component name, component type and component revision,
    set a component to the serverside.

    The URL parameters are:

    name - the name of the component.

    type - the component type associated with the component type.

    revision - the revision associated with the component.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    val_name = escape(request.args.get('name')).split(';')
    val_type = escape(request.args.get('type'))
    val_revision = escape(request.args.get('revision'))

    # Query the database and return the ComponentType instance based on component type.
    component_type = ComponentType.from_db(val_type)

    # Query the database and return the ComponentRevision instance based on component type.
    component_revision = ComponentRevision.from_db(
        val_revision, component_type)

    for name in val_name:
        # Need to initialize an instance of a component first.
        component = Component(
            name, component_type, component_revision)

        component.add()

    return {'result': True}


@app.route("/api/set_property_type", methods=['POST'])
def set_property_type():
    """Given the property type name, allowed component types ,units,allowed regex, number of values and comments,
    set a property type to the serverside.

    The URL parameters are:

    name - the name of the property type.

    type - the name of the allowed component type.

    units - the units of the property type.

    allowed_reg - the allowed regex of the property type.

    values - number of values of the property type.

    comments - the comments associated with the property type.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    val_name = escape(request.args.get('name'))
    # A list of allowed component types.
    val_type = escape(request.args.get('type')).split(';')
    val_units = escape(request.args.get('units'))
    val_allowed_reg = escape(request.args.get('allowed_reg'))
    val_values = escape(request.args.get('values'))
    val_comments = escape(request.args.get('comments'))

    allowed_list = []
    # Query the database and return a list of ComponentType instance based on component type.
    for name in val_type:
        allowed_list.append(ComponentType.from_db(name))
    # Need to initialize an instance of a property type first.
    property_type = PropertyType(
        val_name, val_units, val_allowed_reg, val_values, allowed_list, val_comments)

    property_type.add()

    return {'result': True}


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


@app.route("/api/property_type_count")
def get_property_type_count():
    """Given a URL parameter 'filters', return a dictionary with a value 
    'result' and corresponding value being the number of property types that 
    satisfy said filters.

    filters - of the form "<str>,<str>;...;<str>,<str>", consisting
    of three-tuples of strings with the tuples separated by semicolons and the
    tuples' contents separated by commas.

    :return: A dictionary with a value 'result' and corresponding value being
    the number of property type that satisfy the filters. 
    :rtype: dict
    """

    filters = request.args.get('filters')

    filter_tuples = read_filters(filters)

    return {
        'result': PropertyType.get_count(filters=filter_tuples)
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
                'allowed_types': [t.name for t in pt.allowed_types],
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


@app.route("/api/component_end_property")
def end_component_property():
    """Given the component name, property type, time, user ID and comments, end the property for the component.

    The URL parameters are:

    name - the name of the component to end the property for.

    propertyType - the name of the property type of the property.

    time - the UNIX time for when the property is ended.

    uid - the ID of the user that is ending the property.

    comments - the comments associated with the property termination.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """

    val_name = escape(request.args.get('name'))
    val_property_type = escape(request.args.get('propertyType'))
    val_time = int(escape(request.args.get('time')))
    val_uid = escape(request.args.get('uid'))
    val_comments = escape(request.args.get('comments'))

    property_type = PropertyType.from_db(val_property_type)

    # Initializing the component instance from the name provided as the url parameter.
    component = Component.from_db(val_name)

    property = component.get_property(property_type, val_time, False)

    component.unset_property(
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


@app.route("/api/component_end_connection")
def end_component_connection():
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

    already_disconnected = False

    try:
        c1.disconnect(
            component=c2, time=val_time, uid=val_uid, comments=val_comments
        )
    except ComponentsAlreadyDisconnectedError:
        already_disconnected = True

    return {'result': not already_disconnected}


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


@app.route("/api/set_flag_type", methods=['POST'])
def set_flag_type():
    """Given the flag type name and comments,
    set a flag type to the serverside.

    The URL parameters are:

    name - the name of the flag type.

    comments - the comments associated with the flag type.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    val_name = escape(request.args.get('name'))
    val_comments = escape(request.args.get('comments'))

    # Need to initialize an instance of a component revision first.
    flag_type = FlagType(
        val_name, val_comments)

    flag_type.add()

    return {'result': True}


@app.route("/api/set_flag_severity", methods=['POST'])
def set_flag_severity():
    """Given the flag severity value,
    set a flag severity to the serverside.

    The URL parameters are:

    value - numerical value associated indicating the severity of a flag.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    val_value = escape(request.args.get('value'))

    # Need to initialize an instance of a component revision first.
    flag_severity = FlagSeverity(
        val_value)

    flag_severity.add()

    return {'result': True}


@app.route("/api/set_flag", methods=['POST'])
def set_flag():
    """Given the flag name,start_time,end_time,comments,flag_severity,flag_type and flag_components,
    set a flag to the serverside.

    The URL parameters are:

    name - The name of the flag.

    start_time - The start time of the flag.

    end_time - The end time of the flag.

    comments - The comments relating to the flag.

    flag_severity - The FlagSeverity instance representing the severity of the flag.

    flag_type - The FlagType instance representing the type of the flag.

    flag_components - A list of Component instances related to the flag.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    val_name = escape(request.args.get('name'))
    val_start_time = escape(request.args.get('start_time'))
    val_end_time = escape(request.args.get('end_time'))
    val_comments = escape(request.args.get('comments'))
    val_flag_severity = escape(request.args.get('flag_severity'))
    val_flag_type = escape(request.args.get('flag_type'))
    val_flag_components = escape(
        request.args.get('flag_components')).split(';')

    flag_severity = FlagSeverity.from_db(val_flag_severity)
    flag_type = FlagType.from_db(val_flag_type)

    allowed_list = []
    # Query the database and return a list of Component instances based on component name.
    if val_flag_components != ['Global']:
        for name in val_flag_components:
            allowed_list.append(Component.from_db(name))
    # Need to initialize an instance of Flag first.
    flag = Flag(val_name, val_start_time, val_end_time,
                flag_severity, flag_type, allowed_list, val_comments)

    flag.add()

    return {'result': True}


@app.route("/api/flag_count")
def get_flag_count():
    """Given a URL parameter 'filters', return a dictionary with a value 
    'result' and corresponding value being the number of flags that 
    satisfy said filters.

    filters - of the form "<str>,<str>;...;<str>,<str>", consisting
    of three-tuples of strings with the tuples separated by semicolons and the
    tuples' contents separated by commas.

    :return: A dictionary with a value 'result' and corresponding value being
    the number of flag that satisfy the filters. 
    :rtype: dict
    """

    filters = request.args.get('filters')

    filter_triples = read_filters(filters)

    return {
        'result': Flag.get_count(filters=filter_triples)
    }


@app.route("/api/flag_list")
def get_flag_list():
    """Given three URL parameters 'range', 'orderBy', 'orderDirection', 
    and 'filters', return a dictionary containing a key 'result' with its 
    corresponding value being an array of dictionary representations of each 
    flag in the desired list.

    The URL parameters are:

    range - of the form "<int>;<int>" -- two integers split by a semicolon,
    where the first integer denotes the index first property type to be 
    considered in the list and the second integer denotes the last flag
    to be shown in the list.

    orderBy - the field to order the flag list by.

    orderDirection - either "asc" or "desc" for ascending/descending,
    respectively.

    filters - of the form "<str>,<str>,<int>;...;<str>,<str>,<int>", consisting of 
    three-tuples of strings with the tuples separated by semicolons and the
    tuples' contents separated by commas.

    :return: A dictionary containing a key 'result' with its corresponding value
    being an array of dictionary representations of each flag
    in the desired list.
    :rtype: dict

    """
    list_range = escape(request.args.get('range'))
    order_by = escape(request.args.get('orderBy'))
    order_direction = escape(request.args.get('orderDirection'))

    filters = request.args.get('filters')

    filter_triples = read_filters(filters)

    range_bounds = tuple(map(int, list_range.split(';')))

    # A bunch of assertions to make sure everything is as intended.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    # query to padloper
    flags = Flag.get_list(
        range=range_bounds,
        order_by=order_by,
        order_direction=order_direction,
        filters=filter_triples,
    )

    return {
        'result': [
            {
                'name': f.name,
                'id': f.id(),
                'start_time': f.start_time,
                'end_time': f.end_time,
                'comments': f.comments,
                'flag_severity': {
                    'value': f.flag_severity.value,
                },
                'flag_type': {
                    'name': f.flag_type.name,
                    'comments': f.flag_type.comments
                },
                'flag_components': [t.name for t in f.flag_components]
            }
            for f in flags
        ]
    }


@app.route("/api/flag_type_list")
def get_flag_type_list():
    """Given three URL parameters 'range', 'orderBy', 'orderDirection', 
    and 'nameSubstring', return a dictionary containing a key 'result' with its 
    corresponding value being an array of dictionary representations of each 
    flag type in the desired list.

    range - of the form "<int>;<int>" -- two integers split by a semicolon,
    where the first integer denotes the index first component type to be 
    considered in the list and the second integer denotes the last component 
    type to be shown in the list.

    orderBy - the field to order the flag type list by, a string.

    orderDirection - either "asc" or "desc" for ascending/descending,
    respectively.

    nameSubstring - substring of the name of flag types to consider.

    :return: A dictionary containing a key 'result' with its corresponding value
    being an array of dictionary representations of each flag type in the
    desired list.
    :rtype: dict
    """

    flag_range = escape(request.args.get('range'))
    order_by = escape(request.args.get('orderBy'))
    order_direction = escape(request.args.get('orderDirection'))
    name_substring = escape(request.args.get('nameSubstring'))

    range_bounds = tuple(map(int, flag_range.split(';')))

    # A bunch of assertions to make sure everything is as intended.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    # query to padloper
    flag_types = FlagType.get_list(
        range=range_bounds,
        order_by=order_by,
        order_direction=order_direction,
        name_substring=name_substring
    )

    return {
        'result': [
            {
                'name': f.name,
                'id': f.id(),
                'comments': f.comments
            }
            for f in flag_types
        ]
    }


@app.route("/api/flag_type_count")
def get_flag_type_count():
    """Given a URL parameter 'nameSubstring', return a dictionary with a value 
    'result' and corresponding value being the number of flag types that 
    have said substring in their name.

    nameSubstring - substring of the name of flag types to consider.

    :return: A dictionary with a value 'result' and corresponding value being
    the number of flag types that satisfies the name substring.
    :rtype: dict
    """

    name_substring = escape(request.args.get('nameSubstring'))

    return {'result': FlagType.get_count(name_substring=name_substring)}


@app.route("/api/flag_severity_list")
def get_flag_severity_list():
    """Given three URL parameters 'range', 'orderBy', 'orderDirection', return a dictionary containing a key 'result' with its 
    corresponding value being an array of dictionary representations of each 
    flag severity in the desired list.

    range - of the form "<int>;<int>" -- two integers split by a semicolon,
    where the first integer denotes the index first component type to be 
    considered in the list and the second integer denotes the last flag severity to be shown in the list.

    orderBy - the field to order the flag severity list by, a string.

    orderDirection - either "asc" or "desc" for ascending/descending,
    respectively.

    :return: A dictionary containing a key 'result' with its corresponding value
    being an array of dictionary representations of each flag severity in the
    desired list.
    :rtype: dict
    """

    flag_range = escape(request.args.get('range'))
    order_by = escape(request.args.get('orderBy'))
    order_direction = escape(request.args.get('orderDirection'))

    range_bounds = tuple(map(int, flag_range.split(';')))

    # A bunch of assertions to make sure everything is as intended.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    # query to padloper
    flag_severities = FlagSeverity.get_list(
        range=range_bounds,
        order_by=order_by,
        order_direction=order_direction,
    )

    return {
        'result': [
            {
                'value': f.value,
                'id': f.id(),
            }
            for f in flag_severities
        ]
    }


@app.route("/api/set_permission", methods=['POST'])
def set_permission():
    """Given the permission name and comments associated with the permission,
    set a permission to the serverside.

    The URL parameters are:

    name - the name of the component.

    comment - comments associated with the permission.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    val_name = escape(request.args.get('name'))
    val_comment = escape(request.args.get('comment'))

    # Need to initialize an instance of a component first.
    permission = Permission(
        val_name, val_comment)

    permission.add()

    return {'result': True}


@app.route("/api/set_user_group", methods=['POST'])
def set_user_group():
    """Given the name of the group, comments associated with the group and the list of permissions attached to the group, set a user group to the serverside.

    The URL parameters are:

    name - The name of the user group.

    comment - Comments associated with the user group.

    permission - List of allowed permissions

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """

    val_name = escape(request.args.get('name'))
    val_comment = escape(request.args.get('comment'))
    # A list of allowed permissions.
    val_permission = escape(request.args.get('permission')).split(';')

    allowed_list = []
    # Query the database and return a list of Permission instances based on permission name.
    for name in val_permission:
        allowed_list.append(Permission.from_db(name))

    user_group = UserGroup(val_name, val_comment, allowed_list)

    user_group.add()

    return {'result': True}


@app.route("/api/set_user", methods=['POST'])
def set_user():
    """Given username, password, institution and the list of allowed user group,set a user to the serverside.

    The URL parameters are:

    uname - The username associated with the user.

    pwd_hash - The hashed and salted password.

    institution - Name of the institution.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """

    val_uname = escape(request.args.get('uname'))
    val_pwd_hash = escape(request.args.get('pwd'))
    val_institution = escape(request.args.get('institution'))
    val_user_group = escape(request.args.get('user_group')).split(';')

    allowed_list = []

    for name in val_user_group:
        allowed_list.append(UserGroup.from_db(name))

    user = User(val_uname, val_pwd_hash, val_institution, allowed_list)

    user.add()

    return {'result': True}
