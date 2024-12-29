# https://flask.palletsprojects.com/en/2.0.x/quickstart/

#from crypt import methods
from re import split
from flask import Flask, request, session
import requests
from flask.scaffold import F
from gremlin_python.process.traversal import TextP
from markupsafe import escape
import time
import padloper as p
import json
import os
from urllib.parse import unquote

# The flask application
app = Flask(__name__)
app.secret_key = os.urandom(24)

# set this to the oauth-proxy-server URL
PROXY_SERVER_URL = 'http://localhost:4000/'

p.set_user("test")

def tmp_timestamp(t, uid, comments):
    print("Note: needs to be replaced with proper user registration.")
    return p.Timestamp.__raw_init__(t, uid, int(time.time()), comments)

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

def parse_filters(filtstr, attrs, funcs):
    """Return a list of dictionaries as specified by the `filters` parameter of 
    Vertex.get_list()"""
    ret = []
    if filtstr is not None and filtstr != "":
        for filt in filtstr.split(";"):
            rdict = {}
            for f, a, fc in zip(filt.split(","), attrs, funcs):
                if f != "":
                    rdict[a] = fc(f)
            if len(rdict) > 0:
                ret.append(rdict)
    return ret


# Can also implement something like this.
# @app.route("/api/components_id/<id>")
# def get_component_by_id(id):
#     return str(Component.from_id(escape(id)))
    
def set_perms(username):
    """ Get user permissions from the database, and set as a sessions variable. 
    """
    try:
        user = p.User.from_db(username)
        perms = user.get_permissions()
        if perms:
            session['perms'] = perms
        else:
            session['perms'] = []


    except Exception as e:

        # For printing the exception in the terminal.
        print(e)

        return {'error': json.dumps(e, default=str)}


@app.route("/api/login", methods=['POST'])
def login():
    """ Handle user login.

    This function handles the login process for users. It expects a POST request
    with a JSON payload containing the user's username and GitHub access token.
    It then calls a proxy server to retrieve user data from GitHub using the access token,
    verifies that the retrieved username matches the provided username, and returns
    a response accordingly.

    Returns:
        A JSON response indicating the result of the login attempt.
    """
    try:
        username = request.json.get('username')
        access_token = request.json.get('accessToken')

        if not username or not access_token:
            return ({'error': 'Username and access token are required'}), 400
        
        headers = {'Authorization': 'Bearer ' + access_token}
        response = requests.get(PROXY_SERVER_URL + 'getUserData', headers=headers)

        if response.status_code == 200:
            data = response.json()

            if data.get('login') == username:
                session['user'] = username
                set_perms(username)
                return ({'message': f'Logged in as {username}'}), 200
            else:
                return ({'error': 'Username does not match'}), 401



        return ({'error': 'Failed to retrieve user data from proxy server'}), 500
    # TODO: make more specific
    except Exception as e:

        # For printing the exception in the terminal.
        print(e)

        return {'error': json.dumps(e, default=str)}
    

@app.route("/api/logout", methods=['POST'])
def logout():
    """Handle user logout.

    This function handles the logout process for users. It clears the session data,
    effectively logging the user out.
    """
    session.clear()

    return ({'message': 'Logged out successfully'}), 200


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
        'result': p.Component.from_db(str(escape(name)), permissions=session.get('perms')).as_dict(permissions=session.get('perms'))
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
    print(session.get('user'))
    print(session.get('perms'))

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
    filt = parse_filters(filters, ["name", "type", "version"],
                         [TextP.containing, lambda x: x, lambda x: x])

    # make sure that the range bounds only consist of a min/max, and that
    # the order direction is either asc or desc.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    components = p.Component.get_list(
        range=range_bounds,
        order_by=[(order_by, order_direction)],
        filters=filt,
        permissions=session.get('perms')
    )
    
    return {"result": [c.as_dict(bare=True) for c in components]}


@app.route("/api/set_component_type", methods=['POST'])
def set_component_type():
    """Given the component type name, and comments, set a component type to
    the serverside.

    The URL parameters are:

    name - the name of the component type.

    comments - the comments associated with the component type.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:

        val_name = escape(request.args.get('name'))
        val_comments = escape(request.args.get('comments'))

        # Need to initialize an instance of a component type first.
        component_type = p.ComponentType(name=val_name, comments=val_comments)


        component_type.add(permissions=session.get('perms'))

        return {'result': True}

    except Exception as e:

        # For printing the exception in the terminal.
        print(e)

        return {'error': json.dumps(e, default=str)}


@app.route("/api/replace_component_type", methods=['POST'])
def replace_component_type():
    """Given the new component type name, and comments,
    replace the old component type in the serverside.

    The URL parameters are:

    name - the name of the new component type.

    comments - the comments associated with the new component type.

    component_type - the name of the old component type being replaced.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:

        val_name = escape(request.args.get('name'))
        val_comments = escape(request.args.get('comments'))
        val_component_type = escape(request.args.get('component_type'))

        # Need to initialize an instance of the new component type first.
        component_type_new = p.ComponentType(name=val_name,
                                             comments=val_comments)

        # Gets the old component type from the database.
        component_type_old = p.ComponentType.from_db(val_component_type)

        component_type_old.replace(component_type_new, permissions=session.get('perms'))

        return {'result': True}

    except Exception as e:

        print(e)

        return {'error': json.dumps(e, default=str)}


@app.route("/api/set_component_version", methods=['POST'])
def set_component_version():
    """Given the component version name, component type and comments,
    set a component version to the serverside.

    The URL parameters are:

    name - the name of the component version.

    type - the name of the component type.

    comments - the comments associated with the component version.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:

        val_name = escape(request.args.get('name'))
        val_type = escape(request.args.get('type'))
        val_comments = escape(request.args.get('comments'))

        # Query the database and return a ComponentType instance based on
        # component type name.
        component_type = p.ComponentType.from_db(val_type)

        # Need to initialize an instance of a component version first.
        component_version = p.ComponentVersion(
            name=val_name, type=component_type, comments=val_comments)

        component_version.add(permissions=session.get('perms'))

        return {'result': True}

    except Exception as e:

        print(e)

        return {'error': json.dumps(e, default=str)}


@app.route("/api/replace_component_version", methods=['POST'])
def replace_component_version():
    """Given the new component version name, component type and comments,
    replace the old component version in the serverside.

    The URL parameters are:

    name - the name of the new component version.

    type - the name of the component type.

    comments - the comments associated with the new component version.

    component_version - the name of the old component verson being replaced.

    component_version_allowed_type - the name of the component type of the component version being replaced.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    return {'error': "This routine is broken … " +
                     "val_component_version_allowed_type == undefined"}
    try:
        val_name = escape(request.args.get('name'))
        val_type = escape(request.args.get('type'))
        val_comments = escape(request.args.get('comments'))
        val_component_version = escape(request.args.get('component_version'))
        val_component_version_allowed_type = escape(
            request.args.get('component_version_allowed_type'))

        # Query the database and return a ComponentType instance based on the
        # new component type name.
        component_type_new = p.ComponentType.from_db(val_type)

        # Query the database and return a ComponentType instance based on the
        # old component type name.
        component_type_old = p.ComponentType.from_db(
                val_component_version_allowed_type)

        # Need to initialize an instance of a component version.
        component_version_new = p.ComponentVersion(
            name=val_name, type=component_type_new, comments=val_comments)

        component_version_old = p.ComponentVersion.from_db(
            val_component_version)

        component_version_old.replace(component_version_new, permissions=session.get('perms'))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/set_component", methods=['POST'])
def set_component():
    """Given the component name, component type and component version,
    set a component to the serverside.

    The URL parameters are:

    name - list of names of components.

    type - the component type associated with the component type.

    version - the version associated with the component.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:

        val_name = escape(request.args.get('name')).split(';')
        val_type = escape(request.args.get('type'))
        val_version = escape(request.args.get('version'))

        # Query the database and return the ComponentType instance based on the 
        # component type name.
        component_type = p.ComponentType.from_db(val_type)

        # Query the database and return the ComponentVersion instance based on
        # component version name and
        # component type name.
        if val_version:
            component_version = p.ComponentVersion.from_db(val_version)
        else:
            component_version = None

        for name in val_name:
            # Need to initialize an instance of a component first.
            component = p.Component(name=name, type=component_type,
                                    version=component_version)
            component.add(permissions=session.get('perms'))

        return {'result': True}
    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/replace_component", methods=['POST'])
def replace_component():
    """Given the new component name, component type and component version,
    replace the old component in the serverside.

    The URL parameters are:

    name - the name of the new component.

    type - the component type associated with the new component.

    version - the version associated with the new component.

    component - the name of the component being replaced.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:

        val_name = escape(request.args.get('name'))
        val_type = escape(request.args.get('type'))
        val_version = escape(request.args.get('version'))
        val_component = escape(request.args.get('component'))

        # Query the database and return the ComponentType instance based on the
        # component type name.
        component_type = p.ComponentType.from_db(val_type)

        # Query the database and return the ComponentVersion instance based on
        # component version name and component type name.
        if val_version:
            component_version = p.ComponentVersion.from_db(val_version,
                                                           component_type)
        else:
            component_version = None

        # Need to initialize an instance of a component first.
        component_new = p.Component(name=val_name, type=component_type,
                                    version=component_version)
        component_old = p.Component.from_db(val_component)
        component_old.replace(component_new, permissions=session.get('perms'))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/disable_component")
def disable_component():
    """Given the component name, disable the component from the serverside.

    The URL parameters are:

    name - the name of the component.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    val_name = escape(request.args.get('name'))

    # Need to initialize an instance of a component first.
    component = p.Component.from_db(val_name)
    component.disable()

    return {'result': True}


@app.route("/api/set_property_type", methods=['POST'])
def set_property_type():
    """Given the property type name, allowed component types ,units,allowed regex, number of values and comments,
    set a property type to the serverside.

    The URL parameters are:

    name - the name of the property type.

    type - list of names of the allowed component types.

    units - the units of the property type.

    allowed_reg - the allowed regex of the property type.

    values - number of values of the property type.

    comments - the comments associated with the property type.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:
        val_name = escape(request.args.get('name'))
        # A list of allowed component types.
        val_type = escape(request.args.get('type')).split(';')
        val_units = escape(request.args.get('units'))
        val_allowed_reg = unquote(escape(request.args.get('allowed_reg')))
        val_values = escape(request.args.get('values'))
        val_comments = escape(request.args.get('comments'))

        allowed_list = []
        # Query the database and return a list of ComponentType instance based
        # on component type name.
        for name in val_type:
            allowed_list.append(p.ComponentType.from_db(name))
        
        # Need to initialize an instance of a property type first.
        property_type = p.PropertyType(name=val_name, units=val_units, 
                                       allowed_regex=val_allowed_reg,
                                       n_values=int(val_values), 
                                       allowed_types=allowed_list,
                                       comments=val_comments)
        property_type.add(permissions=session.get('perms'))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/replace_property_type", methods=['POST'])
def replace_property_type():
    """Given the new property type name, allowed component types, units, allowed
    regex, number of values and comments, replace the old property type in the
    serverside.

    The URL parameters are:

    name - the name of the new property type.

    type - list of the name sof the allowed component types associated with the
    new property type.

    units - the units of the new property type.

    allowed_reg - the allowed regex of the new property type.

    values - number of values of the new property type.

    comments - the comments associated with the new property type.

    property_type - the name of the old property type being replaced.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:

        val_name = escape(request.args.get('name'))
        # A list of allowed component types.
        val_type = escape(request.args.get('type')).split(';')
        val_units = escape(request.args.get('units'))
        val_allowed_reg = escape(request.args.get('allowed_reg'))
        val_values = escape(request.args.get('values'))
        val_comments = escape(request.args.get('comments'))
        val_property_type = escape(request.args.get('property_type'))

        allowed_list = []
        # Query the database and return a list of ComponentType instance based
        # on the component type name.
        for name in val_type:
            allowed_list.append(p.ComponentType.from_db(name))
        # Need to initialize an instance of a property type first.
        property_type_new = p.PropertyType(name=val_name, units=val_units, 
                                           allowed_regex=val_allowed_reg,
                                           n_values=int(val_values), 
                                           allowed_types=allowed_list,
                                           comments=val_comments)
        property_type_old = p.PropertyType.from_db(val_property_type)
        property_type_old.replace(property_type_new, permissions=session.get('perms'))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


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
    filt = parse_filters(filters, ["name", "type", "version"],
                         [TextP.containing, lambda x: x, lambda x: x])

    return {'result': p.Component.get_count(filters=filt, 
                                            permissions=session.get('perms'))}


@app.route("/api/component_types_and_versions")
def get_component_types_and_versions():
    """Return a dictionary with a value 'result' and corresponding value 
    being a list of all the component types and their corresponding versions.

    # TODO: This should ideally never, ever be used. Querying every type and 
    # corresponding version is a very bad idea. In the web interface, instead
    of fetching this URL, create a ComponentTypeAutocomplete and
    ComponentVersionAutocomplete that will query the limited component list
    that has a min/max range instead.

    :return: A dictionary with a value 'result' and corresponding value 
    being a list of all the component types and their corresponding versions.
    :rtype: dict
    """

    types = p.ComponentType.get_names_of_types_and_versions(permissions=session.get('perms'))
    ret = {}
    for t in types:
        ret[t["name"]] = t["versions"]
    return {'result': ret}


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

    # make sure that the range bounds only consist of a min/max, and that
    # the order direction is either asc or desc.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    types = p.ComponentType.get_list(
        range=range_bounds,
        order_by=[(order_by, order_direction)],
        filters=[{"name": TextP.containing(name_substring)}],
        permissions=session.get('perms')
    )
    
    return {"result": [t.as_dict() for t in types]}


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

    return {'result': p.ComponentType.get_count(
            filters=[{"name": TextP.containing(name_substring)}])}


@app.route("/api/component_version_list")
def get_component_version_list():
    """Given three URL parameters 'range', 'orderBy', 'orderDirection', 
    and 'filters', return a dictionary containing a key 'result' with its 
    corresponding value being an array of dictionary representations of each 
    component version in the desired list.

    The URL parameters are:

    range - of the form "<int>;<int>" -- two integers split by a semicolon,
    where the first integer denotes the index first component version to be 
    considered in the list and the second integer denotes the last component 
    to be shown in the list.

    orderBy - the field to order the component version list by.

    orderDirection - either "asc" or "desc" for ascending/descending,
    respectively.

    filters - of the form "<str>,<str>;...;<str>,<str>", consisting of 
    two-tuples of strings with the tuples separated by semicolons and the
    tuples' contents separated by commas.

    :return: A dictionary containing a key 'result' with its corresponding value
    being an array of dictionary representations of each component version 
    in the desired list.
    :rtype: dict
    """
    list_range = escape(request.args.get('range'))
    order_by = escape(request.args.get('orderBy'))
    order_direction = escape(request.args.get('orderDirection'))

    filters = request.args.get('filters')
    filt = parse_filters(filters, ["name", "type"],
                         [TextP.containing, lambda x: x])

    range_bounds = tuple(map(int, list_range.split(';')))

    # A bunch of assertions to make sure everything is as intended.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    vers = p.ComponentVersion.get_list(
        range=range_bounds,
        order_by=[(order_by, order_direction)],
        filters=filt
    )
    
    return {"result": [v.as_dict() for v in vers]}

@app.route("/api/component_version_count")
def get_component_version_count():
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
    filt = parse_filters(filters, ["name", "type"],
                         [TextP.containing, lambda x: x])

    return {'result': p.ComponentVersion.get_count(filters=filt)}


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
    filt = parse_filters(filters, ["name", "allowed_types"],
                         [TextP.containing, lambda x: x])

    return {
        'result': p.PropertyType.get_count(filters=filt)
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
    filt = parse_filters(filters, ["name", "allowed_types"],
                         [TextP.containing, lambda x: x])

    range_bounds = tuple(map(int, list_range.split(';')))

    # A bunch of assertions to make sure everything is as intended.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    ptypes = p.PropertyType.get_list(
        range=range_bounds,
        order_by=[(order_by, order_direction)],
        filters=filt
    )

    return {"result": [pt.as_dict() for pt in ptypes]}


@app.route("/api/component_set_property", methods=['POST'])
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
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:

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

        property_type = p.PropertyType.from_db(val_property_type)

        component = p.Component.from_db(val_name)

        property = p.Property(values=values, type=property_type)

        t = tmp_timestamp(val_time, val_uid, val_comments)
        component.set_property(property, start=t,
                               permissions=session.get('perms')) 

        return {'result': True}

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/component_end_property")
def end_component_property():
    """Given the component name, property type, time, user ID and comments, end
    the property for the component.

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

    property_type = p.PropertyType.from_db(val_property_type)

    # Initializing the component instance from the name provided as the url
    # parameter.
    component = p.Component.from_db(val_name)

    property = component.get_property(property_type, val_time)
    if property == None:
        raise p.ComponentPropertyStartTimeExceedsInputtedTime(
                    f"{component.name} has no property with the given "\
                     "combination of time and property type. Make sure time "\
                     "inputted is later than property start time."
                )

    t = tmp_timestamp(val_time, val_uid, val_comments)
    component.unset_property(property, t, permissions=session.get('perms'))

    return {'result': True}


@app.route("/api/component_replace_property")
def replace_component_property():
    """Given the component name, property type and the replaced time, user ID,
    comments, the values associated with the property, along with the count of
    values, replace the old property for the component.

    The URL parameters are:

    name - the name of the component to replace the property for.

    propertyType - the name of the property type of the property. 
    This attribute remains same for both the old and the new property.

    time - the UNIX time for when the new property is set.

    uid - the ID of the user that sets the new property.

    comments - the comments associated with the new property.

    values - the values of the new property, of the form
    "<str>;<str>;...;<str>", separated by semicolons.

    valueCount - the number of values of the new property.

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

    property_type = p.PropertyType.from_db(val_property_type)

    component = p.Component.from_db(val_name)

    property_new = p.Property(values=values, type=property_type)

    t = tmp_timestamp(val_time, val_uid, val_comments)

    component.replace_property(propertyTypeName=val_property_type,
                               property=property_new, at_time=val_time, 
                               uid=val_uid,
                               start = t, comments=val_comments,
                               permissions=session.get('perms'))

    # component.replace_property()

    return {'result': True}


@app.route("/api/component_disable_property")
def disable_component_property():
    """Given the component name and the name of the property type, disable the
    property from the serverside.
    """
    val_name = escape(request.args.get('name'))
    val_property_type = escape(request.args.get('propertyType'))

    component = p.Component.from_db(val_name)

    component.disable_property(
        propertyTypeName=val_property_type,
        permissions=session.get('perms')
    )

    return {'result': True}


@app.route("/api/component_add_connection", methods=['POST'])
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
    beforehand, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:

        val_name1 = escape(request.args.get('name1'))
        val_name2 = escape(request.args.get('name2'))
        val_time = int(escape(request.args.get('time')))
        val_uid = escape(request.args.get('uid'))
        val_comments = escape(request.args.get('comments'))
        val_is_replacement = escape(request.args.get('isreplacement'))
        
        val_is_replacement = True if val_is_replacement == 'True' else False

        c1, c2 = p.Component.from_db(val_name1), p.Component.from_db(val_name2)

        t = tmp_timestamp(val_time, val_uid, val_comments)
        c1.connect(c2, t, is_replacement=val_is_replacement, permissions=session.get('perms'))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/component_end_connection")
def end_component_connection():
    """Given the names of the two components that are already connected, the
    time to end the connection, the ID of the user ending this connection, and
    the comments associated with ending the connection, end the conenction
    between the two components.

    The URL parameters are:

    name1 - the name of the first component

    name2 - the name of the second component

    time - the UNIX time for when the connection is ended

    uid - the ID of the user that has ended the connection

    comments - Comments associated with the ending the connection

    :return: Return a dictionary with a key 'result' and value being a boolean
    that is True if and only if the components were not already disconnected
    beforehand.
    :rtype: dict
    """

    val_name1 = escape(request.args.get('name1'))
    val_name2 = escape(request.args.get('name2'))
    val_time = int(escape(request.args.get('time')))
    val_uid = escape(request.args.get('uid'))
    val_comments = escape(request.args.get('comments'))

    c1, c2 = p.Component.from_db(val_name1), p.Component.from_db(val_name2)

    already_disconnected = False

    try:
        t = tmp_timestamp(val_time, val_uid, val_comments)
        c1.disconnect(c2, t, permissions=session.get('perms'))
    except ComponentsAlreadyDisconnectedError:
        already_disconnected = True

    return {'result': not already_disconnected}


@app.route("/api/component_disable_connection")
def disable_component_connection():
    """Given the names of the two components to disable the connection between,
    disable the connection between the two components.

    The URL parameters are:

    name1 - the name of the first component

    name2 - the name of the second component
    """

    val_name1 = escape(request.args.get('name1'))
    val_name2 = escape(request.args.get('name2'))

    c1, c2 = p.Component.from_db(val_name1), p.Component.from_db(val_name2)
    # Get the connection object, and then disable it.
    raise RuntimeError("This function needs to be fixed! The time at which " \
                       "the connection is to be disabled needs to be " \
                       "specified.")
    return {'result': True}


@app.route("/api/get_connections")
def get_connections():
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

    c = p.Component.from_db(val_name)

    connections = c.get_connections(at_time=val_time)

    return {
        'result': [
            {
                'inVertex': conn.inVertex.as_dict(),
                'outVertex': conn.outVertex.as_dict(),
                'subcomponent': True if isinstance(conn,
                                                   p.RelationSubcomponent) \
                                else False,
                'id': conn.id(),
            }
            for conn in connections
        ]
    }

@app.route("/api/get_subcomponents", methods=['GET'])
def get_subcomponents():
    """Given a component name, return the names of all subcomponents of the component.

    The URL parameters are:

    name - the name of the component to query the subcomponents for.

    :return: Return a dictionary with a key 'result' and value being a list of
    names for subcomponents.
    :rtype: dict
    """

    val_name = escape(request.args.get('name'))

    c = p.Component.from_db(val_name)

    subcomponents = c.get_subcomponents()

    return {
        'result': [
            subcomponent.name \
            for subcomponent in subcomponents
        ]
    }


@app.route("/api/component_add_subcomponent", methods=['POST'])
def add_component_subcomponent():
    """Given the name of the the component that is a subcomponent along with the
    name of the main component, establish the appropriate relation.

    The URL parameters are:

    name1 - the name of the main component

    name2 - the name of the subcomponent

    :return: Return a dictionary with a key 'result' and value being a boolean
    that is True if and only if the component was not a subcomponent beforehand,
    otherwise, a dictionary with a key 'error' with the corresponding value of
    appropriate exception.
    :rtype: dict
    """
    try:

        val_name1 = escape(request.args.get('name1'))
        val_name2 = escape(request.args.get('name2'))

        c1, c2 = p.Component.from_db(val_name1), p.Component.from_db(val_name2)

        already_subcomponent = False

        try:
            c1.subcomponent_connect(
                component=c2,
                permissions=session.get('perms')
            )
        except ComponentAlreadySubcomponentError:
            already_subcomponent = True

        return {'result': not already_subcomponent}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/component_disable_subcomponent")
def disable_component_subcomponent():
    """Given the name of the the component that is a subcomponent along with the
    name of the main component, disable the appropriate connection.

    The URL parameters are:

    name1 - the name of the main component

    name2 - the name of the subcomponent

    :return: Return a dictionary with a key 'result' and value being a boolean
    that is True.
    :rtype: dict
    """

    val_name1 = escape(request.args.get('name1'))
    val_name2 = escape(request.args.get('name2'))

    c1, c2 = p.Component.from_db(val_name1), p.Component.from_db(val_name2)
    c1.disable_subcomponent(otherComponent=c2, permissions=session.get('perms'))

    return {'result': True}


@app.route("/api/set_flag_type", methods=['POST'])
def set_flag_type():
    """Given the flag type name and comments, set a flag type to the serverside.

    The URL parameters are:

    name - the name of the flag type.

    comments - the comments associated with the flag type.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:

        val_name = escape(request.args.get('name'))
        val_comments = escape(request.args.get('comments'))

        # Need to initialize an instance of a component version first.
        flag_type = p.FlagType(val_name, val_comments)
        flag_type.add(permissions=session.get('perms'))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/replace_flag_type", methods=['POST'])
def replace_flag_type():
    """Given the new flag type name and comments, replace the old flag type from
    the serverside.

    The URL parameters are:

    name - the name of the flag type.

    comments - the comments associated with the flag type.

    flag_type - the name of the old flag type being replaced.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:
        val_name = escape(request.args.get('name'))
        val_comments = escape(request.args.get('comments'))
        val_flag_type = escape(request.args.get('flag_type'))

        # Need to initialize an instance of a flag type first.
        flag_type_new = p.FlagType(name=val_name, comments=val_comments)
        flag_type_old = p.FlagType.from_db(val_flag_type)
        flag_type_old.replace(flag_type_new, permissions=session.get('perms'))
        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/set_flag_severity", methods=['POST'])
def set_flag_severity():
    """Given the flag severity name, set a flag severity to the serverside.

    The URL parameters are:

    name - name indicating the severity of a flag.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    val_name = escape(request.args.get('name'))

    # Need to initialize an instance of a component version first.
    flag_severity = p.FlagSeverity(val_name)

    flag_severity.add(permissions=session.get('perms'))

    return {'result': True}


@app.route("/api/replace_flag_severity", methods=['POST'])
def replace_flag_severity():
    """Given the new flag severity name, replace the old flag severity from the
    serverside.

    The URL parameters are:

    name - name indicating the severity of a flag.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    val_name = escape(request.args.get('name'))
    val_flag_severity = escape(request.args.get('flag_severity'))

    # Need to initialize an instance of a flag severity first.
    flag_severity_new = p.FlagSeverity(val_name)
    flag_severity_old = p.FlagSeverity.from_db(val_flag_severity)
    flag_severity_old.replace(flag_severity_new, permissions=session.get('perms'))

    return {'result': True}


@app.route("/api/set_flag", methods=['POST'])
def set_flag():
    """Given the flag name,start_time,uid,start_comments,flag_severity,flag_type
    and flag_components, set a flag to the serverside.

    The URL parameters are:

    name - The name of the flag.

    uid - The ID of the user adding the new flag.

    start_time - The start time of the flag.

    comments - The comments relating to the flag.

    flag_severity - The FlagSeverity instance representing the severity of the
    flag.

    flag_type - The FlagType instance representing the type of the flag.

    flag_components - A list of Component instances related to the flag.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:

        val_name = escape(request.args.get('name'))
        val_uid = escape(request.args.get('uid'))
        val_start_time = escape(request.args.get('start_time'))
        val_end_time = escape(request.args.get('end_time'))
        val_start_comments = escape(request.args.get('start_comments'))
        val_comments = escape(request.args.get('comments'))
        val_severity = escape(request.args.get('severity'))
        val_type = escape(request.args.get('type'))
        val_components = escape(
            request.args.get('components')).split(';')

        severity = p.FlagSeverity.from_db(val_severity)
        type = p.FlagType.from_db(val_type)

        allowed_list = []
        # Query the database and return a list of Component instances based on
        # component name.
        if val_components != ['Global']:
            for name in val_components:
                allowed_list.append(p.Component.from_db(name))

        # Need to initialize an instance of Flag first.
        start = tmp_timestamp(val_start_time, val_uid, val_start_comments)
        print(start)
        if val_end_time != str(0):
            end = tmp_timestamp(val_end_time, val_uid, val_start_comments)
        else:
            end = None
        flag = p.Flag(val_name, start, severity, type, 
                      comments=val_comments, end=end,
                      components=allowed_list)
        flag.add(permissions=session.get('perms'))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}

@app.route("/api/unset_flag", methods=['POST'])
def unset_flag():
    """Given the flag name,end_time,end_uid and end_comments
    set 'end' attributes to an existing flag.

    The URL parameters are:

    name - The name of the flag.

    uid - The ID of the user ending the flag.

    end_time - The end time of the flag.

    comments - The comments related to ending the flag.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    val_name = escape(request.args.get('name'))
    val_uid = escape(request.args.get('uid'))
    val_end_time = escape(request.args.get('end_time'))
    val_comments = escape(request.args.get('comments'))

    # Need to initialize an instance of Flag first.
    flag = p.Flag.from_db(val_name)
    t = tmp_timestamp(val_end_time, val_uid, val_comments)
    flag.end_flag(end, permissions=session.get('perms'))

    return {'result': True}


@app.route("/api/replace_flag", methods=['POST'])
def replace_flag():
    """Given the new flag name, start_time, uid, start_comments, flag_severity,
    flag_type and flag_components, replace the old flag from the serverside.

    The URL parameters are:

    name - The name of the flag.

    uid - The ID of the user adding the new flag.

    start_time - The start time of the new flag.

    comments - The comments related to the new flag.

    flag_severity - The FlagSeverity instance representing the severity of the
    flag.

    flag_type - The FlagType instance representing the type of the flag.

    flag_components - A list of Component instances related to the flag.

    flag - the name of the old flag being replaced.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:

        val_name = escape(request.args.get('name'))
        val_uid = escape(request.args.get('uid'))
        val_start_time = escape(request.args.get('start_time'))
        val_end_time = escape(request.args.get('end_time'))
        val_start_comments = escape(request.args.get('start_comments'))
        val_comments = escape(request.args.get('comments'))
        val_flag_severity = escape(request.args.get('flag_severity'))
        val_flag_type = escape(request.args.get('flag_type'))
        val_flag_components = escape(
            request.args.get('flag_components')).split(';')

        flag_severity = p.FlagSeverity.from_db(val_flag_severity)
        flag_type = p.FlagType.from_db(val_flag_type)

        val_flag = escape(request.args.get('flag'))

        allowed_list = []
        # Query the database and return a list of Component instances based on
        # component name.
        if val_flag_components != ['Global']:
            for name in val_flag_components:
                allowed_list.append(p.Component.from_db(name))

        flag_old = p.Flag.from_db(val_flag)
        
        start = tmp_timestamp(val_start_time, val_uid, val_start_comments)
        if val_end_time != str(0):
            end = tmp_timestamp(val_end_time, val_uid, val_start_comments)
        else:
            end = None
        flag_new = Flag(val_name, start, flag_severity, flag_type, 
                        comments=val_comments, end=end, 
                        components=allowed_list)
        flag_old.replace(flag_new, permissions=session.get('perms'))

        return {'result': True}

    except Exception as e:

        print(e)

        return {'error': json.dumps(e, default=str)}

@app.route("/api/disable_flag")
def disable_flag():
    """Given the flag name, disable the flag from the serverside.

    The URL parameters are:

    name - the name of the flag.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    val_name = escape(request.args.get('name'))

    # Need to initialize an instance of a flag first.
    flag = p.Flag.from_db(val_name)

    flag.disable()

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
        'result': p.Flag.get_count(filters=filter_triples)
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

    filters - of the form "<str>,<str>,<int>;...;<str>,<str>,<int>", consisting
    of three-tuples of strings with the tuples separated by semicolons and the
    tuples' contents separated by commas.

    :return: A dictionary containing a key 'result' with its corresponding value
    being an array of dictionary representations of each flag
    in the desired list.
    :rtype: dict

    """
    raise RuntimeError("Flags have not been properly implemented in the "\
                       "web interface.")
    return
    list_range = escape(request.args.get('range'))
    order_by = escape(request.args.get('orderBy'))
    order_direction = escape(request.args.get('orderDirection'))

    filters = request.args.get('filters')
    filt = parse_filters(filters, ["type", "severity"],
                         [lambda x: x, lambda x: x])

    range_bounds = tuple(map(int, list_range.split(';')))

    # A bunch of assertions to make sure everything is as intended.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    # query to padloper
    flags = p.Flag.get_list(
        range=range_bounds,
        order_by=[(order_by, order_direction)],
        filters=filt
    )

    return {"result": [f.as_dict() for f in flags]}


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
    flag_types = p.FlagType.get_list(
        range=range_bounds,
        order_by=[(order_by, order_direction)],
        filters=[{"name": TextP.containing(name_substring)}]
    )

    return {"result": [ft.as_dict() for ft in flag_types]}

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

    return {'result': p.FlagType.get_count(
            filters=[{"name": TextP.containing(name_substring)}]
)}


@app.route("/api/flag_severity_list")
def get_flag_severity_list():
    """Given three URL parameters 'range', 'orderBy', 'orderDirection', return a
    dictionary containing a key 'result' with its corresponding value being an
    array of dictionary representations of each flag severity in the desired
    list.

    range - of the form "<int>;<int>" -- two integers split by a semicolon,
    where the first integer denotes the index first component type to be 
    considered in the list and the second integer denotes the last flag severity
    to be shown in the list.

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
    flag_severities = p.FlagSeverity.get_list(range=range_bounds,
            order_by=[(order_by, order_direction)])

    return {"result": [fs.as_dict() for fs in flag_severities]}


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
    # val_name = escape(request.args.get('name'))
    # val_comment = escape(request.args.get('comment'))

    val_name = request.form.get('name')
    val_comment = request.form.get('comment')

    # Need to initialize an instance of a component first.
    permission = p.Permission(val_name, val_comment)

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

    # val_name = escape(request.args.get('name'))
    # val_comment = escape(request.args.get('comment'))
    val_name = request.form.get('name')
    val_comment = request.form.get('comment')
    # A list of allowed permissions.
    # val_permission = escape(request.args.get('permission')).split(';')
    val_permission = request.form.get('permission').split(';')

    allowed_list = []
    # Query the database and return a list of Permission instances based on
    # permission name.
    for name in val_permission:
        allowed_list.append(p.Permission.from_db(name))

    user_group = p.UserGroup(val_name, val_comment, allowed_list)

    # print(f"user_group: {user_group}")

    user_group.add()

    return {'result': True}


@app.route("/api/set_user", methods=['POST'])
def set_user():
    """Given username, password, institution and the list of allowed user
    group,set a user to the serverside.

    The URL parameters are:

    uname - The username associated with the user.

    pwd_hash - The hashed and salted password.

    institution - Name of the institution.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """

    # val_uname = escape(request.args.get('uname'))
    # val_pwd_hash = escape(request.args.get('pwd'))
    # val_institution = escape(request.args.get('institution'))
    # val_user_group = ['']
    # print(escape(request.args.get('user_group')))
    # if escape(request.args.get('user_group')) != None:
    #     val_user_group = escape(request.args.get('user_group')).split(';')
    val_uname = request.form.get('uname')
    val_pwd_hash = request.form.get('pwd')
    val_institution = request.form.get('institution')
    if request.form.get('user_group'):
        val_user_group = request.form.get('user_group').split(';')
    else:
        val_user_group = ['']
        
    print(val_user_group)

    allowed_list = []

    if val_user_group != ['']:
        for name in val_user_group:
            allowed_list.append(p.UserGroup.from_db(name))
        user = p.User(val_uname, val_pwd_hash, val_institution, allowed_list)
    else:
        user = p.User(val_uname, val_pwd_hash, val_institution)

    user.add()

    return {'result': True}

@app.route("/api/new_user", methods=['POST'])
def new_user():
    val_username = request.form.get('username')
    val_institution = request.form.get('institution')
    user = p.User(val_username, val_institution)
    user.add()
    # print(user)
    return {'result': True}

@app.route("/api/new_usergroup", methods=['POST'])
def new_user_group():
    val_name = request.form.get('name')
    # val_values = escape(request.args.get('values'))
    # values = val_values.split(';')
    val_permissions = escape(request.form.get('permissions'))
    permissions = val_permissions.split(';')
    # print(val_permissions)
    group = p.UserGroup(val_name, permissions)
    group._add()
    # print(a.name)
    # print(a.permissions)
    return {'result': True}

@app.route("/api/new_set_usergroup", methods=['POST'])
def new_set_user_group():
    """Given the names of the two components to connect, the time to make the
    connection, the ID of the user making this connection, and the comments
    associated with the connection, connect the two components.

    The URL parameters are:

    user - the name of the user

    group - the name of the group

    :return: Return a dictionary with a key 'result' and value being a boolean
    that is True if and only if the components were not already connected
    beforehand, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.  
    :rtype: dict
    """
    try:

        val_user = escape(request.form.get('user'))
        val_group = escape(request.form.get('group'))
        groups = val_group.split(';')
        
        user = p.User.from_db(val_user)
        # user, group = p.User.from_db(val_user), p.UserGroup.from_db(val_group)
        for gr in groups:
            group = p.UserGroup.from_db(gr)
            user.set_user_group(group)

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}
    
@app.route("/api/get_permissions", methods=['GET'])
def get_permissions():
    val_username = request.args.get('username')
    user = p.User.from_db(val_username)
    perms = user.get_permissions()
    print(perms)
    return {'result': perms}


@app.route("/api/get_user_list", methods=["GET"])
def get_user_list():
    # pass
    users = p.User.get_list()
    # return {"result": [c.as_dict(bare=True) for c in components]}
    # return {'result': [p.User.as_dict(u) for u in users]}
    return {'result': [p.User.as_dict(u) for u in users]} 

@app.route("/api/get_user_groups", methods=["GET"])
def get_user_groups():
    val_username = request.args.get('username')
    user = p.User.from_db(val_username)
    groups = user.get_user_groups()
    return {'result': [gr[0].as_dict() for gr in groups]}

@app.route("/api/get_user_group_list", methods=["GET"])
def get_user_group_list():
    groups = p.UserGroup.get_list()
    return {'result': [p.UserGroup.as_dict(gr) for gr in groups]}

@app.route("/api/get_all_permissions", methods=["GET"])
def get_all_permissions():
    return {'result': list(p.permissions_set)}
