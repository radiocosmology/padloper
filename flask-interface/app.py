# https://flask.palletsprojects.com/en/2.0.x/quickstart/

#from crypt import methods
from copy import deepcopy
from functools import partial
import re
from typing import Any, Callable, Dict, List, Tuple
from flask import Flask, request, session, Response
from flask_session import Session
import requests
#from flask.scaffold import F
from gremlin_python.process.traversal import TextP
from gremlin_python.process.graph_traversal import __
from markupsafe import escape
import time
import padloper as p
# NB: must be `import _global`, not `from padloper import _global`. The latter
# creates a second copy of the module (padloper._global) with its own
# connection, user and vertex cache, distinct from the one padloper's
# classes actually use.
import _global as p_global
import json
import os
from datetime import datetime, timedelta
from urllib.parse import unquote
from dotenv import load_dotenv

load_dotenv()

# The flask application
app = Flask(__name__)

# Read configuration from environment, with sensible defaults for local dev
PROXY_SERVER_URL = os.getenv('PROXY_SERVER_URL', 'http://oauth-proxy-server:4000/')

# Set up session: we use flask_session because the default Flask session is
# client size and we don't want to expose permissions there; here we use a
# server-side configuration.
app.config["SESSION_TYPE"] = "filesystem"
# Prefer SECRET_KEY, fallback to FLASK_SECRET_KEY, finally a dev default
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", os.getenv("FLASK_SECRET_KEY", "change-me"))

# Session cookie hardening. The app is served over HTTPS at the reverse proxy,
# so the cookie is marked Secure; set SESSION_COOKIE_SECURE=false for a
# plain-HTTP development setup (browsers exempt http://localhost anyway).
# SameSite=Lax stops cross-site POSTs from carrying the session (CSRF) while
# still allowing the OAuth redirect back into the app.
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv(
    "SESSION_COOKIE_SECURE", "true").lower() in ("1", "true", "yes")
app.config["SESSION_COOKIE_HTTPONLY"] = True
# A signed session cookie is rejected this long after it was last written.
# (The UI re-establishes the session from the stored GitHub token on load.)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)

#CONTINUE HERE: test user authentication.
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
# @app.route("/api/s_id/<id>")
# def get_component_by_id(id):
#     return str(Component.from_id(escape(id)))

def _user_is_deactivated(name):
    """Whether a user vertex with this name exists but has been disabled."""
    try:
        return p_global.t.V().has('category', p.User.category) \
            .has('name', name).has('active', False).count().next() > 0
    except Exception:
        return False


def set_perms(username):
    """ Get user permissions from the database, and set as a sessions variable.
    """
    # Cache user in session and compute permissions from DB
    session['user'] = username
    user = p.User.from_db(username)
    perms = user.get_permissions()
    print(">>> ", perms)
    if perms:
        session['perms'] = perms
    else:
        session['perms'] = []


@app.before_request
def _ensure_padloper_user():
    """Require a logged-in session for an active user on all routes except
    login."""
    # Allow the login endpoint without a session
    if request.path == '/api/login':
        return

    # padloper keeps the acting user in a module global; never let the
    # previous request's identity carry over into this one.
    p_global._user = None

    uname = session.get('user')
    if not uname:
        return ({'error': 'Authentication required'}), 401

    try:
        p.set_user(uname)
    except Exception:
        # The account has been deactivated or removed since login: end the
        # session rather than proceeding with a stale identity.
        session.clear()
        return ({'error': 'Your account has been deactivated or removed. '
                          'Please contact an administrator.'}), 401

    # Refresh the cached permissions from the DB so that edits to a user's
    # groups, or to a group's permissions, take effect without a re-login.
    perms = p_global._user.get_permissions()
    if sorted(perms) != sorted(session.get('perms') or []):
        session['perms'] = perms


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
                # Look up existing user, or bootstrap if this is the very
                # first user in the system (empty database).
                try:
                    user_obj = p.User.from_db(username)
                except Exception:
                    if _user_is_deactivated(username):
                        return ({'error': 'This account has been deactivated. '
                                          'Please contact an administrator.'}), 403
                    # Only allow auto-creation when no users exist yet.
                    existing_users = p.User.get_list()
                    if len(existing_users) > 0:
                        return ({'error': 'User not found. '
                                 'Please contact an administrator to create your account.'}), 403
                    try:
                        # Minimal stub for uid stamping during creation
                        p_global._user = type("_LoginStub", (), {
                            "name": username,
                            # check_permission() treats an empty permission
                            # list as "look up the acting user's permissions",
                            # so the stub must be able to answer.
                            "get_permissions": lambda self: list(p.permissions_set),
                        })()
                        user_obj = p.User(name=username, groups=[])
                        user_obj.add(permissions=[])

                        # Ensure a 'readonly' group (no permissions) exists,
                        # then add the new user to it.
                        try:
                            default_group = p.UserGroup.from_db('readonly')
                        except Exception:
                            default_group = p.UserGroup(name='readonly', permissions=[])
                            default_group.add(permissions=[])
                        try:
                            user_obj.add_group(default_group)
                        except Exception:
                            pass
                    finally:
                        p_global._user = None

                # Establish session perms and set current user for this process
                set_perms(username)
                try:
                    p.set_user(username)
                except Exception:
                    pass
                return ({'message': f'Logged in as {username}'}), 200
            else:
                return ({'error': 'Username does not match'}), 401



        return ({'error': 'Failed to retrieve user data from proxy server'}), 500
    # TODO: make more specific
    except Exception as e:

        # For printing the exception in the terminal.
        print(e)

        return {'error': json.dumps(e, default=str)}, 401


@app.route("/api/logout", methods=['POST'])
def logout():
    """Handle user logout.

    This function handles the logout process for users. It clears the session data,
    effectively logging the user out.
    """
    session.clear()
    # Clear padloper user so subsequent requests don’t inherit stale identity
    try:
        p_global._user = None
    except Exception:
        pass

    return ({'message': 'Logged out successfully'}), 200


@app.route("/api/components_name/<path:name>")
def get_component_by_name(name):
    """Given a name of a component, return its dictionary representation.

    Returns {'result': {...}} on success or {'error': '...'} on failure
    instead of a 500, so clients can handle gracefully (e.g., when the
    component is not found).
    """
    try:
        comp = p.Component.from_db(str(escape(name)))
        data = comp.as_dict(permissions=session.get('perms', []))

        # Normalize embedded Flag objects for UI compatibility
        flags = data.get('flags', []) or []
        for f in flags:
            # Ensure 'name' and 'comments' exist; map from 'notes'
            if 'name' not in f and 'notes' in f:
                f['name'] = f['notes']
            if 'comments' not in f:
                f['comments'] = f.get('notes', '')

            # Flatten start/end Timestamp convenience fields expected by UI
            s = f.get('start')
            if s is not None:
                try:
                    f['start_time'] = s.get('time') if isinstance(s, dict) else s.time
                    f['start_uid'] = s.get('uid') if isinstance(s, dict) else s.uid
                    f['start_edit_time'] = s.get('edit_time') if isinstance(s, dict) else s.edit_time
                    f['start_comments'] = s.get('comments') if isinstance(s, dict) else s.comments
                except Exception:
                    pass
            e = f.get('end')
            if e is not None:
                try:
                    f['end_time'] = e.get('time') if isinstance(e, dict) else e.time
                    f['end_uid'] = e.get('uid') if isinstance(e, dict) else e.uid
                    f['end_edit_time'] = e.get('edit_time') if isinstance(e, dict) else e.edit_time
                    f['end_comments'] = e.get('comments') if isinstance(e, dict) else e.comments
                except Exception:
                    pass

        return {'result': data}
    except Exception as e:
        print(e)
        # Distinguish not-found from other errors when possible
        try:
            from padloper._exceptions import NotInDatabase
            if isinstance(e, NotInDatabase):
                return {'error': json.dumps(e, default=str)}, 404
        except Exception:
            pass
        return {'error': json.dumps(e, default=str)}, 400


@app.route("/api/components_tree/<name>/<depth>/<time>")
def components_tree(name, depth, time):
    """Given a component name, time to check, and a depth, trace the graph
    and return nodes and edges within the given depth at the given time.

    :param name: The component name
    :type name: str
    :param depth: The search depth
    :type depth: int
    :param time: The unix timestamp in seconds
    :type time: int

    :return: Return a dictionary of 'result' with nodes and edges
    :rtype: dict
    """
    try:
        component = p.Component.from_db(str(escape(name)))
        res = {
            'result': component.get_network(int(depth), int(time), permissions=session.get('perms'))
        }
        return res
    except Exception as e:
        return {'error': json.dumps(e, default=str)}


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
    try:
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
        # TODO(case-insensitive search): the name filter below uses
        # TextP.containing, which is case-sensitive. A previous attempt used
        # TextP("regex", "(?i)...") but TinkerPop 3.5.x (shipped by
        # JanusGraph 0.6.2) doesn't support a regex predicate, so that
        # variant failed server-side with "Invalid OpProcessor [null]".
        # Restoring containing matches the pre-2026 behavior. To regain
        # case-insensitivity, options are: (a) upgrade JanusGraph to a
        # version with TinkerPop 3.6+ (where TextP.regex works), or
        # (b) add an indexed name_lower property and filter against that.
        # Same pattern is repeated below for property/version/flag filters.
        filt = parse_filters(filters, ["name", "type", "version"],
                            [lambda x: TextP.containing(x),
                             lambda x: x, lambda x: x])

        # make sure that the range bounds only consist of a min/max, and that
        # the order direction is either asc or desc.
        assert len(range_bounds) == 2
        assert order_direction in {'asc', 'desc'}

        components = p.Component.get_list(
            range=range_bounds,
            order_by=[(order_by, order_direction)],
            filters=filt,
        )

        return {'result': [c.as_dict(bare=True, permissions=session.get('perms')) for c in components]}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}



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


        component_type.add(permissions=session.get('perms'),
                           uid=session.get('user'))

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

        component_type_old.replace(component_type_new, permissions=session.get('perms', []))

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

        component_version.add(permissions=session.get('perms'),
                              uid=session.get('user'))

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

        component_version_old.replace(component_version_new, permissions=session.get('perms', []))

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

        component_type = p.ComponentType.from_db(primary_attr=val_type)

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
            component.add(permissions=session.get('perms'),
                          uid=session.get('user'))


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
        # component version name and component type name. The current API
        # accepts only a primary attribute; filter by type explicitly.
        if val_version:
            matches = p.ComponentVersion.get_list(
                filters={"name": val_version, "type": val_type}
            )
            if len(matches) == 0:
                raise Exception(
                    f"ComponentVersion not found for name '{val_version}' and type '{val_type}'."
                )
            if len(matches) > 1:
                raise Exception(
                    f"Multiple ComponentVersions found for name '{val_version}' and type '{val_type}'."
                )
            component_version = matches[0]
        else:
            component_version = None

        # Need to initialize an instance of a component first.
        component_new = p.Component(name=val_name, type=component_type,
                                    version=component_version)
        component_old = p.Component.from_db(val_component)
        component_old.replace(component_new, permissions=session.get('perms', []))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/disable_component", methods=['POST'])
def disable_component():
    """Given the component name, disable the component from the serverside.

    The URL parameters are:

    name - the name of the component.

    :return: A dictionary with a key 'result' of corresponding value True
    if the request was successful, otherwise, a dictionary with a key 'error'
    with the corresponding value of appropriate exception.
    :rtype: dict
    """
    try:
        val_name = escape(request.args.get('name'))

        # Need to initialize an instance of a component first.
        component = p.Component.from_db(val_name)
        component.disable(permissions=session.get('perms'))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


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
        property_type.add(permissions=session.get('perms'),
                          uid=session.get('user'))

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

        # throw errors if necessary
        if int(val_values) < 1:
            raise Exception(f"Values cannot be less than 1.")

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
        property_type_old.replace(property_type_new, permissions=session.get('perms', []))

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
    try:

        filters = request.args.get('filters')
        filt = parse_filters(filters, ["name", "type", "version"],
                            [lambda x: TextP.containing(x),
                             lambda x: x, lambda x: x])

        return {'result': p.Component.get_count(filters=filt)}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


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
    try:
        types = p.ComponentType.get_names_of_types_and_versions(permissions=session.get('perms', []))
        ret = {}
        for t in types:
            # Defensive: ensure expected keys exist and are JSON-serializable
            name = t.get("name") or t.get("type")
            versions = t.get("versions", [])
            if name is not None:
                ret[str(name)] = list(versions)
        return {'result': ret}
    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


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
    name_substring = escape(request.args.get('nameSubstring') or '')

    range_bounds = tuple(map(int, component_range.split(';')))

    # make sure that the range bounds only consist of a min/max, and that
    # the order direction is either asc or desc.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    types = p.ComponentType.get_list(
        range=range_bounds,
        order_by=[(order_by, order_direction)],
        filters=[{"name": TextP.containing(name_substring)}]
    )

    return {"result": [t.as_dict(permissions=session.get('perms')) for t in types]}


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

    name_substring = escape(request.args.get('nameSubstring') or '')

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
    filt = parse_filters(
        filters, ["name", "type"],
        [lambda x: TextP.containing(x), lambda x: x]
    )

    range_bounds = tuple(map(int, list_range.split(';')))

    # A bunch of assertions to make sure everything is as intended.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    vers = p.ComponentVersion.get_list(
        range=range_bounds,
        order_by=[(order_by, order_direction)],
        filters=filt
    )

    return {"result": [v.as_dict(permissions=session.get('perms')) for v in vers]}

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
    filt = parse_filters(
        filters, ["name", "type"],
        [lambda x: TextP.containing(x), lambda x: x]
    )

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
    filt = parse_filters(
        filters, ["name", "allowed_types"],
        [lambda x: TextP.containing(x), lambda x: x]
    )

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
    filt = parse_filters(
        filters, ["name", "allowed_types"],
        [lambda x: TextP.containing(x), lambda x: x]
    )

    range_bounds = tuple(map(int, list_range.split(';')))

    # A bunch of assertions to make sure everything is as intended.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    ptypes = p.PropertyType.get_list(
        range=range_bounds,
        order_by=[(order_by, order_direction)],
        filters=filt
    )

    return {"result": [pt.as_dict(permissions=session.get('perms')) \
                       for pt in ptypes]}


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
                               permissions=session.get('perms', []))

        return {'result': True}

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/component_end_property", methods=['POST'])
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
    try:
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

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/component_replace_property", methods=['POST'])
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

        property_new = p.Property(values=values, type=property_type)

        t = tmp_timestamp(val_time, val_uid, val_comments)

        component.replace_property(propertyTypeName=val_property_type,
                                property=property_new, at_time=val_time,
                                uid=val_uid, start=t, comments=val_comments,
                                permissions=session.get('perms', []))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/component_disable_property", methods=['POST'])
def disable_component_property():
    """Given the component name and the name of the property type, disable the
    property from the serverside.
    """
    try:
        raise Exception(f"disable property error")
        val_name = escape(request.args.get('name'))
        val_property_type = escape(request.args.get('propertyType'))

        component = p.Component.from_db(val_name)

        component.disable_property(
            propertyTypeName=val_property_type,
            permissions=session.get('perms', [])
        )

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


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

    replace_time - start timestamp of connection to replace, or none by default

    end_time - end timestamp of the new connection, or none by default

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
        val_replace_time = escape(request.args.get('replace_time'))
        val_end_time = escape(request.args.get('end_time'))

        c1, c2 = p.Component.from_db(val_name1), p.Component.from_db(val_name2)
        t = tmp_timestamp(val_time, val_uid, val_comments)

        if val_replace_time == 'None':
            c1.connect(c2, t, to_replace=None, permissions=session.get("perms", []))

        else:
            # get existing connection object
            connections = c1.get_connections(comp=c2, at_time=val_replace_time)

            if val_end_time == 'None':
                c1.connect(c2, t, to_replace=connections[0],
                           permissions=session.get("perms", []))
            else:
                end_t = tmp_timestamp(val_end_time, val_uid, val_comments)
                c1.connect(c2, t, end_t, to_replace=connections[0],
                           permissions=session.get("perms", []))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/component_end_connection", methods=['POST'])
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
    try:
        val_name1 = escape(request.args.get('name1'))
        val_name2 = escape(request.args.get('name2'))
        val_time = int(escape(request.args.get('time')))
        val_uid = escape(request.args.get('uid'))
        val_comments = escape(request.args.get('comments'))

        c1, c2 = p.Component.from_db(val_name1), p.Component.from_db(val_name2)

        already_disconnected = False

        try:
            t = tmp_timestamp(val_time, val_uid, val_comments)
            print("trying to disconnect....")
            c1.disconnect(c2, t, permissions=session.get('perms', []))
        except p.ComponentsAlreadyDisconnectedError:
            already_disconnected = True

        return {'result': not already_disconnected}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/component_disable_connection", methods=['POST'])
def disable_component_connection():
    """Given the names of the two components to disable the connection between,
    and the time at which the connection was created, disable the connection between
    the two components.

    The URL parameters are:

    name1 - the name of the first component

    name2 - the name of the second component

    start_time - the time at which the connection was started
    """
    try:
        val_name1 = escape(request.args.get('name1'))
        val_name2 = escape(request.args.get('name2'))
        time = escape(request.args.get('start_time'))

        c1, c2 = p.Component.from_db(val_name1), p.Component.from_db(val_name2)
        # Get the connection object, and then disable it.
        connections = c1.get_connections(comp=c2, at_time=time)
        if len(connections) > 1:        # this shouldn't happen
            # add to error message this is really broken
            raise Exception(f"Multiple connections exist between {val_name1} and {val_name2}"
                + f" at start time {datetime.fromtimestamp(int(time))}."
                + "Something went very wrong, please contact a maintainer!")

        # if it returns nothing
        if len(connections) == 0:
            raise Exception(f"No connections were found between {val_name1} and {val_name2}"
                + f" with start time {datetime.fromtimestamp(int(time))}."
                + "Something went very wrong, please contact a maintainer!")
        else:
            connections[0].disable(permissions=session.get('perms'))  # disable the connection

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


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

    connections = c.get_connections(at_time=val_time,
                                    permissions=session.get('perms'))

    return {
        'result': [
            {
                'inVertex': conn.inVertex.as_dict(permissions=session.get('perms')),
                'outVertex': conn.outVertex.as_dict(permissions=session.get('perms')),
                'subcomponent': isinstance(conn, p.RelationSubcomponent),
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
            c1.subcomponent_connect(c2, permissions=session.get('perms', []))
        except p.ComponentAlreadySubcomponentError:
            already_subcomponent = True

        return {'result': not already_subcomponent}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/component_disable_subcomponent", methods=['POST'])
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
    try:
        raise Exception(f"disable subcomponent error")
        val_name1 = escape(request.args.get('name1'))
        val_name2 = escape(request.args.get('name2'))

        c1, c2 = p.Component.from_db(val_name1), p.Component.from_db(val_name2)
        c1.disable_subcomponent(otherComponent=c2,
                                permissions=session.get('perms', []))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


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

        # Create a FlagType with proper keyword args
        flag_type = p.FlagType(name=val_name, comments=val_comments)
        flag_type.add(permissions=session.get('perms'),
                      uid=session.get('user'))

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
        flag_type_old.replace(flag_type_new, permissions=session.get('perms', []))
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
    try:
        val_name = escape(request.args.get('name'))

        # Create a FlagSeverity with proper keyword args
        flag_severity = p.FlagSeverity(name=val_name)
        flag_severity.add(permissions=session.get('perms'),
                          uid=session.get('user'))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


@app.route("/api/replace_flag_severity", methods=['POST'])
def replace_flag_severity():
    """Given the new flag severity name, replace the old flag severity from the
    serverside.

    The URL parameters are:

    name - name indicating the severity of a flag.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    try:
        val_name = escape(request.args.get('name'))
        val_flag_severity = escape(request.args.get('flag_severity'))

        # Need to initialize an instance of a flag severity first.
        flag_severity_new = p.FlagSeverity(val_name)
        flag_severity_old = p.FlagSeverity.from_db(val_flag_severity)
        flag_severity_old.replace(flag_severity_new,
                                  permissions=session.get('perms', []))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


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
        flag_type = p.FlagType.from_db(val_type)

        allowed_list = []
        # Query the database and return a list of Component instances based on
        # component name.
        if val_components != ['Global']:
            for name in val_components:
                allowed_list.append(p.Component.from_db(name))

        # Need to initialize an instance of Flag first.
        start = tmp_timestamp(val_start_time, val_uid, val_start_comments)
        if val_end_time != str(0):
            end = tmp_timestamp(val_end_time, val_uid, val_start_comments)
        else:
            end = None
        # Store the display name in 'notes' since Flag has no 'name' attr
        flag = p.Flag(type=flag_type,
                      severity=severity,
                      notes=val_name,
                      start=start,
                      end=end,
                      components=allowed_list)
        flag.add(permissions=session.get('perms'), uid=session.get('user'))

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
    try:
        val_name = escape(request.args.get('name'))
        val_uid = escape(request.args.get('uid'))
        val_end_time = escape(request.args.get('end_time'))
        val_comments = escape(request.args.get('comments'))

        # Lookup flag by its display name stored in notes
        matches = p.Flag.get_list(filters=[{"notes": val_name}], allow_disabled=True)
        if len(matches) == 0:
            raise Exception(f"Flag not found: {val_name}")
        if len(matches) > 1:
            raise Exception(f"Multiple flags found with name '{val_name}'. Please disambiguate.")
        flag = matches[0]
        t = tmp_timestamp(val_end_time, val_uid, val_comments)
        # Use the modern API method; end_flag() is deprecated
        flag.set_end(t, permissions=session.get('perms', []))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


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

        # Lookup existing flag by display name stored in notes
        matches = p.Flag.get_list(filters=[{"notes": val_flag}], allow_disabled=True)
        if len(matches) == 0:
            raise Exception(f"Flag to replace not found: {val_flag}")
        if len(matches) > 1:
            raise Exception(f"Multiple flags found with name '{val_flag}'. Please disambiguate.")
        flag_old = matches[0]

        start = tmp_timestamp(val_start_time, val_uid, val_start_comments)
        if val_end_time != str(0):
            end = tmp_timestamp(val_end_time, val_uid, val_start_comments)
        else:
            end = None
        # Note: Flag does not have a 'name' attribute in the data model.
        # We store the display name in 'notes' to preserve UI behaviour.
        flag_new = p.Flag(type=flag_type,
                          severity=flag_severity,
                          notes=val_name,
                          start=start,
                          end=end,
                          components=allowed_list)
        flag_old.replace(flag_new, permissions=session.get('perms', []))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}

@app.route("/api/disable_flag", methods=['POST'])
def disable_flag():
    """Given the flag name, disable the flag from the serverside.

    The URL parameters are:

    name - the name of the flag.

    :return: A dictionary with a key 'result' of corresponding value True
    :rtype: dict
    """
    try:
        val_name = escape(request.args.get('name'))

        # Lookup flag by its display name stored in notes
        matches = p.Flag.get_list(filters=[{"notes": val_name}], allow_disabled=True)
        if len(matches) == 0:
            raise Exception(f"Flag not found: {val_name}")
        if len(matches) > 1:
            raise Exception(f"Multiple flags found with name '{val_name}'. Please disambiguate.")
        flag = matches[0]
        flag.disable(permissions=session.get('perms'))

        return {'result': True}

    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


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
    try:
        filters_str = request.args.get('filters')

        # Flags filter format from UI: "name,type,severity;..."
        # Only type and severity apply to Flag attributes; ignore the leading name.
        filt = []
        if filters_str:
            for triple in filters_str.split(';'):
                if triple == "":
                    continue
                parts = triple.split(',')
                # parts[0] is a free-text name filter not used by backend
                if len(parts) >= 2 and parts[1]:
                    d = {"type": parts[1]}
                    if len(parts) >= 3 and parts[2]:
                        d["severity"] = parts[2]
                    filt.append(d)

        return {
            'result': p.Flag.get_count(filters=filt)
        }
    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


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
    try:
        list_range = escape(request.args.get('range')) or "0;-1"
        order_by = escape(request.args.get('orderBy')) or "type"
        order_direction = escape(request.args.get('orderDirection')) or "asc"

        filters_str = request.args.get('filters')

        # Parse filters from UI: "name,type,severity;..." — ignore the leading name.
        filt = []
        if filters_str:
            for triple in filters_str.split(';'):
                if triple == "":
                    continue
                parts = triple.split(',')
                if len(parts) >= 2 and parts[1]:
                    d = {"type": parts[1]}
                    if len(parts) >= 3 and parts[2]:
                        d["severity"] = parts[2]
                    filt.append(d)

        # Normalize and validate ordering
        valid_order_fields = {"type", "severity", "notes"}
        if order_by not in valid_order_fields:
            order_by = "type"
        if order_direction not in {"asc", "desc"}:
            order_direction = "asc"

        range_bounds = tuple(map(int, list_range.split(';')))
        assert len(range_bounds) == 2

        flags = p.Flag.get_list(
            range=range_bounds,
            order_by=[(order_by, order_direction)],
            filters=filt
        )
        result = []
        for f in flags:
            d = f.as_dict(permissions=session.get('perms'))
            # Ensure UI gets a 'name' and 'comments' field; Flag stores 'notes'
            if 'notes' in d and 'name' not in d:
                d['name'] = d['notes']
            if 'comments' not in d:
                d['comments'] = d.get('notes', '')
            result.append(d)
        return {"result": result}
    except Exception as e:
        print(e)
        return {'error': json.dumps(e, default=str)}


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
    name_substring = escape(request.args.get('nameSubstring') or '')

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

    return {"result": [ft.as_dict(permissions=session.get('perms')) \
                       for ft in flag_types]}

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

    name_substring = escape(request.args.get('nameSubstring') or '')

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

    return {"result": [fs.as_dict(permissions=session.get('perms')) \
                       for fs in flag_severities]}


@app.route("/api/new_user", methods=['POST'])
def new_user():
    val_username = request.form.get('username')
    _val_institution = request.form.get('institution')
    # Create user with no groups, then ensure 'readonly' group and assign.
    user = p.User(name=val_username, groups=[])
    user.add(permissions=session.get('perms'),
             uid=session.get('user'))
    try:
        default_group = p.UserGroup.from_db('readonly')
    except Exception:
        default_group = p.UserGroup(name='readonly', permissions=[])
        default_group.add(permissions=session.get('perms'),
                          uid=session.get('user'))
    try:
        user.add_group(default_group, permissions=session.get('perms'))
    except Exception:
        pass
    return {'result': True}


@app.route("/api/new_usergroup", methods=['POST'])
def new_user_group():
    """Create a user group.

    Form fields:

    name - the name of the new group

    permissions - the group's permissions separated by ','. (Permission names
    themselves contain ';', e.g. "Component;add", so ';' cannot be the
    separator.)

    :return: {'result': True}, or {'error': message} with a 4xx status.
    """
    val_name = (request.form.get('name') or '').strip()
    raw = request.form.get('permissions') or ''
    permissions = [x.strip() for x in raw.split(',') if x.strip()]
    if not val_name:
        return ({'error': 'Group name is required'}), 400
    try:
        group = p.UserGroup(name=val_name, permissions=permissions)
    except ValueError as e:
        return ({'error': str(e)}), 400
    if group.in_db():
        return ({'error': f'A group named "{val_name}" already exists'}), 409
    group.add(permissions=session.get('perms'),
              uid=session.get('user'))
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
        # Require admin membership to assign users to groups
        acting = session.get('user')
        if not acting:
            return ({'error': 'Unauthorized'}), 401
        try:
            acting_user = p.User.from_db(acting)
            acting_groups = acting_user.get_groups()
            is_admin = any(getattr(gr, 'name', '') == 'admin' for gr in acting_groups)
        except Exception:
            is_admin = False
        if not is_admin:
            return ({'error': 'Forbidden: admin required to modify user groups'}), 403

        val_user = escape(request.form.get('user'))
        val_group = escape(request.form.get('group'))
        groups = val_group.split(';')

        user = p.User.from_db(val_user)
        # user, group = p.User.from_db(val_user), p.UserGroup.from_db(val_group)
        for gr in groups:
            group = p.UserGroup.from_db(gr)
            user.add_group(group, permissions=session.get('perms'))

        return {'result': True}

    except p.NotInDatabase as e:
        return ({'error': str(e)}), 404
    except Exception as e:
        print(e)
        return ({'error': str(e)}), 400


def _require_admin():
    """Return None if the session user is an active member of the 'admin'
    group; otherwise return the (response, status) tuple the route should
    send back."""
    acting = session.get('user')
    if not acting:
        return ({'error': 'Unauthorized'}, 401)
    try:
        acting_user = p.User.from_db(acting)
        is_admin = any(getattr(gr, 'name', '') == 'admin'
                       for gr in acting_user.get_groups())
    except Exception:
        is_admin = False
    if not is_admin:
        return ({'error': 'Forbidden: admin required to manage users '
                          'and groups'}, 403)
    return None


def _active_member_count(group):
    """Number of active users with an active membership edge to `group`."""
    return p_global.t.V(group.id()) \
        .bothE(p.RelationUserGroup.category).has('active', True) \
        .otherV().has('active', True).count().next()


@app.route("/api/remove_user_group", methods=['POST'])
def remove_user_group():
    """Remove a user from a user group (admin only).

    Form fields:

    user - the name of the user

    group - the name of the group

    The last remaining member of the 'admin' group cannot be removed, so that
    the system can never be left without an administrator.

    :return: {'result': True}, or {'error': message} with a 4xx/5xx status.
    """
    denied = _require_admin()
    if denied:
        return denied

    val_user = (request.form.get('user') or '').strip()
    val_group = (request.form.get('group') or '').strip()
    if not val_user or not val_group:
        return ({'error': 'Both user and group are required'}), 400

    try:
        user = p.User.from_db(val_user)
        group = p.UserGroup.from_db(val_group)
    except p.NotInDatabase as e:
        return ({'error': str(e)}), 404

    if not any(gr.id() == group.id() for gr in user.get_groups()):
        return ({'error': f'User {val_user} is not in group '
                          f'{val_group}'}), 404

    if group.name == 'admin' and _active_member_count(group) <= 1:
        return ({'error': 'Cannot remove the last member of the admin '
                          'group'}), 400

    try:
        user.remove_group(group, permissions=session.get('perms'),
                          uid=session.get('user'))
    except p.NotInDatabase as e:
        return ({'error': str(e)}), 404
    except Exception as e:
        print(e)
        return ({'error': str(e)}), 500

    return {'result': True}


@app.route("/api/set_usergroup_permissions", methods=['POST'])
def set_usergroup_permissions():
    """Replace the permissions of a user group (admin only).

    Form fields:

    name - the name of the group

    permissions - the complete new list of permissions, separated by ','
    (permission names themselves contain ';'). An empty string removes all
    permissions from the group.

    :return: {'result': True, 'permissions': [...]}, or {'error': message}
    with a 4xx/5xx status.
    """
    denied = _require_admin()
    if denied:
        return denied

    val_name = (request.form.get('name') or '').strip()
    raw = request.form.get('permissions') or ''
    new_perms = [x.strip() for x in raw.split(',') if x.strip()]
    if not val_name:
        return ({'error': 'Group name is required'}), 400

    try:
        group = p.UserGroup.from_db(val_name)
    except p.NotInDatabase as e:
        return ({'error': str(e)}), 404

    try:
        group.replace_permissions(new_perms, permissions=session.get('perms'))
    except ValueError as e:
        return ({'error': str(e)}), 400
    except Exception as e:
        print(e)
        return ({'error': str(e)}), 500

    return {'result': True, 'permissions': group.permissions}


@app.route("/api/disable_usergroup", methods=['POST'])
def disable_usergroup():
    """Delete a user group (admin only). The group vertex and all of its
    membership edges are disabled, not dropped, so the history is kept.

    Form fields:

    name - the name of the group. The 'admin' group cannot be deleted.

    :return: {'result': True}, or {'error': message} with a 4xx/5xx status.
    """
    denied = _require_admin()
    if denied:
        return denied

    val_name = (request.form.get('name') or '').strip()
    if not val_name:
        return ({'error': 'Group name is required'}), 400
    if val_name == 'admin':
        return ({'error': 'The admin group cannot be deleted'}), 400

    try:
        group = p.UserGroup.from_db(val_name)
    except p.NotInDatabase as e:
        return ({'error': str(e)}), 404

    try:
        group.disable(permissions=session.get('perms'),
                      uid=session.get('user'))
    except Exception as e:
        print(e)
        return ({'error': str(e)}), 500

    # Drop the disabled group from padloper's in-process vertex cache so that
    # later lookups by ID do not resurrect it.
    p_global._vertex_cache.pop(group.id(), None)

    return {'result': True}


@app.route("/api/disable_user", methods=['POST'])
def disable_user():
    """Deactivate a user (admin only). Form field: username.

    The user vertex and all of its membership edges are disabled (kept for
    history). Their next request ends their session, and they can no longer
    log in until reactivated. You cannot deactivate yourself, nor the last
    member of the admin group.
    """
    denied = _require_admin()
    if denied:
        return denied

    val_name = (request.form.get('username') or '').strip()
    if not val_name:
        return ({'error': 'Username is required'}), 400
    if val_name == session.get('user'):
        return ({'error': 'You cannot deactivate your own account'}), 400

    try:
        user = p.User.from_db(val_name)
    except p.NotInDatabase as e:
        return ({'error': str(e)}), 404

    admin_groups = [gr for gr in user.get_groups() if gr.name == 'admin']
    if admin_groups and _active_member_count(admin_groups[0]) <= 1:
        return ({'error': 'Cannot deactivate the last member of the admin '
                          'group'}), 400

    try:
        user.disable(permissions=session.get('perms'),
                     uid=session.get('user'))
    except Exception as e:
        print(e)
        return ({'error': str(e)}), 500

    p_global._vertex_cache.pop(user.id(), None)
    return {'result': True}


@app.route("/api/enable_user", methods=['POST'])
def enable_user():
    """Reactivate a deactivated user (admin only). Form field: username.

    Memberships ended by the deactivation stay ended; the user comes back in
    the default `readonly` group, like a newly created user.
    """
    denied = _require_admin()
    if denied:
        return denied

    val_name = (request.form.get('username') or '').strip()
    if not val_name:
        return ({'error': 'Username is required'}), 400

    try:
        user = p.User.reactivate(val_name)
    except p.AlreadyInDatabase as e:
        return ({'error': str(e)}), 409
    except p.NotInDatabase as e:
        return ({'error': str(e)}), 404
    except Exception as e:
        print(e)
        return ({'error': str(e)}), 500

    try:
        default_group = p.UserGroup.from_db('readonly')
    except p.NotInDatabase:
        default_group = p.UserGroup(name='readonly', permissions=[])
        default_group.add(permissions=session.get('perms'),
                          uid=session.get('user'))
    try:
        user.add_group(default_group, permissions=session.get('perms'))
    except Exception as e:
        print(e)
        return ({'error': f'User reactivated but could not be added to '
                          f'the readonly group: {e}'}), 500

    return {'result': True}


@app.route("/api/get_permissions", methods=['GET'])
def get_permissions():
    val_username = request.args.get('username')
    print(val_username)
    user = p.User.from_db(val_username)
    perms = user.get_permissions()
    print(perms)
    return {'result': perms}


@app.route("/api/get_user_list", methods=["GET"])
def get_user_list():
    """List active users; with `include_disabled=1`, deactivated users are
    appended with `active: false` and their former groups omitted."""
    users = p.User.get_list()
    result = [p.User.as_dict(u, permissions=session.get('perms'))
              for u in users]
    if request.args.get('include_disabled') in ('1', 'true'):
        seen = {u['name'] for u in result}
        rows = p_global.t.V().has('category', p.User.category) \
            .has('active', False) \
            .project('name', 'time_added', 'uid_added', 'time_disabled',
                     'uid_disabled') \
            .by('name').by('time_added').by('uid_added').by('time_disabled') \
            .by(__.coalesce(__.values('uid_disabled'), __.constant(''))) \
            .toList()
        for r in rows:
            if r['name'] in seen:
                continue
            seen.add(r['name'])
            r.update({'active': False, 'groups': [], 'replacement': 0})
            result.append(r)
    return {'result': result}

@app.route("/api/get_user_groups", methods=["GET"])
def get_user_groups():
    val_username = request.args.get('username')
    try:
        user = p.User.from_db(val_username)
    except p.NotInDatabase as e:
        return ({'error': str(e)}), 404
    groups = user.get_groups()
    return {'result': [gr.as_dict(permissions=session.get('perms')) for gr in groups]}

@app.route("/api/get_user_group_list", methods=["GET"])
def get_user_group_list():
    groups = p.UserGroup.get_list()
    return {'result': [p.UserGroup.as_dict(gr, 
                                           permissions=session.get('perms')) \
                       for gr in groups]}


@app.route("/api/get_all_permissions", methods=["GET"])
def get_all_permissions():
    return {'result': list(p.permissions_set)}


@app.route("/api/system_diagram.<fmt>", methods=["GET"])
def system_diagram(fmt):
    """The whole inventory as a Graphviz graph (see padloper.system_dot).

    `system_diagram.dot` returns the DOT source, `system_diagram.svg` the image
    rendered with Graphviz on the server, and `system_diagram.json` the legend
    (types with colours and counts, totals). Optional query parameter `time`
    (UNIX seconds) selects the connections in force at that moment (default:
    now).
    """
    if fmt not in ("dot", "svg", "json"):
        return ({'error': 'Format must be dot, svg or json'}), 404
    at_time = request.args.get("time", type=int)
    inventory = p.system_inventory(at_time)
    if fmt == "json":
        return p.system_summary(inventory)
    dot_source = p.system_dot(inventory)
    if fmt == "dot":
        return Response(dot_source, mimetype="text/vnd.graphviz")
    try:
        svg = p.render_dot(dot_source, "svg")
    except RuntimeError as e:
        return ({'error': str(e)}), 503
    return Response(svg, mimetype="image/svg+xml")


@app.route("/api/component_sequence_list", methods=["GET"])
def get_component_sequence_list():
    component_range = escape(request.args.get('range'))
    order_by = escape(request.args.get('orderBy'))
    order_direction = escape(request.args.get('orderDirection'))
    # name_substring = escape(request.args.get('nameSubstring'))

    range_bounds = tuple(map(int, component_range.split(';')))

    # make sure that the range bounds only consist of a min/max, and that
    # the order direction is either asc or desc.
    assert len(range_bounds) == 2
    assert order_direction in {'asc', 'desc'}

    sequences = p.ComponentSequence.get_list(
        range=range_bounds,
        order_by=[(order_by, order_direction)],
        # filters=[{"name": TextP.containing(name_substring)}]
    )

    return {"result": [s.as_dict(permissions=session.get('perms')) for s in sequences]}


@app.route("/api/set_sequence", methods=['POST'])
def set_sequence():
    try:
        name = escape(request.args.get('name'))
        component_type = escape(request.args.get('component_type'))
        format_ = escape(request.args.get('format'))
        increment = request.args.get('increment', 'false') == 'true'
        next_seq = int(request.args.get('next_seq', 0))

        # Query the database and return the ComponentType instance based on the
        # component type name.
        component_type = p.ComponentType.from_db(primary_attr=component_type)

        component = p.ComponentSequence(
            name=name, component_type=component_type, format=format_,
            increment=increment, next_seq=next_seq,
        )
        component.add(permissions=session.get('perms'),
                      uid=session.get('user'))
        return {'result': True}
    except Exception as e:
        return {'error': json.dumps(e, default=str)}


@app.route("/api/update_sequence/<name>", methods=['POST'])
def update_sequence(name):
    try:
        new_name = escape(request.args.get('name'))
        component_type = escape(request.args.get('component_type'))
        format_ = escape(request.args.get('format'))
        increment = request.args.get('increment', 'false') == 'true'
        next_seq = request.args.get('next_seq', 0, type=int)

        # query the database to get the existing sequence and component type
        sequence = p.ComponentSequence.from_db(primary_attr=name)
        component_type = p.ComponentType.from_db(primary_attr=component_type)

        vals = {
            'increment': increment,
            'next_seq': next_seq,
        }
        if new_name:
            vals['name'] = new_name
        if component_type:
            vals['component_type'] = component_type
        if format_:
            vals['format'] = format_

        sequence.update(**vals, permissions=session.get('perms'))
        return {'result': True}
    except Exception as e:
        return {'error': json.dumps(e, default=str)}


@app.route("/api/delete_sequence/<name>", methods=['POST'])
def delete_sequence(name):
    try:
        sequence = p.ComponentSequence.from_db(primary_attr=name)
        sequence.delete(permissions=session.get('perms'))
        return {'result': True}
    except Exception as e:
        return {'error': json.dumps(e, default=str)}


@app.route("/api/bulk_input", methods=['POST'])
def bulk_input():
    payload = request.json

    ltf = payload.get('ltf', '')
    timestamp = payload.get('time')
    comments = payload.get('comments', '')

    op_chars = {
        '|': 'merge',
        '>': 'connect',
        '<>': 'replace',
        '//': 'disconnect',
        '<<': 'supercomponent',
        '>>': 'subcomponent',
    }
    op_template = {
        'component1': {
            'name': '',
            'attrs': [],
        },
        'operation': '',
        'component2': {
            'name': '',
            'attrs': [],
        },
    }

    # pre-process the LTF entry
    ltf += '\n' # add a newline to ensure all regex commands work properly
    ltf = re.sub(r"(?<![\w\.])[ \t]*#.*[\r\n]", "", ltf) # remove comments
    ltf = re.sub(r"(?<![\w\.])[ \t]*\$\$.*", "", ltf) # $$ lines -> blank lines
    ltf = re.sub(r"(?<=[\w\.])(?<!;)[ \t]*[\r\n][ \t]*(?=[\.\+])", " | ", ltf)
    ltf = re.sub(r"(?<=[\w\.])(?<!;)[ \t]*[\r\n][ \t]*(?=\w)", " > ", ltf)
    ltf = re.sub(r"(?<=[\w\.])[ \t]*[\r\n]?\/\/[ \t]*[\r\n]?(?=\w)", " // ", ltf)
    ltf = re.sub(r"(?<=[\w\.])[ \t]*[\r\n]?<>[ \t]*[\r\n]?(?=\w)", " <> ", ltf)
    ltf = re.sub(r"(?<=[\w\.])[ \t]*[\r\n]?>>[ \t]*[\r\n]?(?=\w)", " >> ", ltf)
    ltf = re.sub(r"(?<=[\w\.])[ \t]*[\r\n]?<<[ \t]*[\r\n]?(?=\w)", " << ", ltf)
    ltf = re.sub(r"(?<=[\w\.])[ \t]*[\r\n]?>[ \t]*[\r\n]?(?=\w)", " > ", ltf)
    ltf = re.sub(r"(?<=[\w\.])(?<!;)[ \t]*(?=[\r\n][ \t]*)(?!\w)", ";", ltf)
    ltf = re.sub(r"(?<=[\w\.]);[ \t]*(?=\w)", ";\n", ltf)
    ltf = re.sub(r"[ \t]+", " ", ltf) # replace all multi-spaces with a single
    ltf = ltf.replace(" ;", ";") # ensure no space before semicolons
    ltf = re.sub(r"(?<=[\w\.]);[ \t]*[\r\n][ \t]*(?!\w)", ";", ltf)

    # process the ltf into operations
    operations = []
    operations : List[Dict[str, Dict[str, List[Tuple[str, str]] | str] | str]]
    for i, line in enumerate(ltf.split('\n')):
        line = line.strip()
        if not line:
            continue
        if not line.endswith(';'):
            return {'error': (f"No semicolon in line {i} of ltf:\n{ltf}\n"
                              f"This usually indicates a syntax format of "
                              f"some kind, e.g. ending a line with an "
                              f"operator like '>'.")}

        elements = line.removesuffix(';').split(' ')
        if elements[0] in op_chars:
            return {'error': (f"Operations cannot begin with an operator! "
                              f"Line {i} of ltf:\n{ltf}")}
        if elements[-1] in op_chars:
            return {'error': (f"Operations cannot end with an operator! "
                              f"Line {i} of ltf:\n{ltf}")}
        if '=' in elements[0]:
            return {'error': (f"Operations cannot begin with an attribute! "
                              f"Line {i} of ltf:\n{ltf}")}
        if elements[0].startswith('.') or elements[0].startswith('+'):
            return {'error': (f"The first element of multi-line entries "
                              f"cannot begin with a wildcard. Line {i} of "
                              f"ltf:\n{ltf}")}

        op = deepcopy(op_template)
        for j, el in enumerate(elements):
            if el in op_chars and op['operation'] and op['component2']['name']:
                # we've completed an operation so start a continuation op
                operations.append(op)
                new_op = deepcopy(op_template)
                new_op['component1'] = op['component2']
                op = new_op
            if el in op_chars and op['operation']:
                # this is back-to-back operations, so it's invalid
                return {'error': (f"Cannot have two operators back-to-back! "
                                  f"Line {i}, element {j} of ltf:\n{ltf}")}
            elif el in op_chars:
                # this is the operation type
                op['operation'] = op_chars[el]
            elif '=' in el:
                # if there is an equal sign, this is an attribute
                el = el.replace("+", " ") # spaces are encoded as + characters
                if op['operation']:
                    # we're on the second component if there's an operation
                    if not op['component2']['name']:
                        return {'error': (f"A component must be defined "
                                          f"before attributes! Line {i}, "
                                          f"element {j} of ltf:\n{ltf}")}
                    op['component2']['attrs'].append(tuple(el.split('=')))
                else:
                    # if there's not yet an operation, we've already verified
                    # that the line does not begin with an attribute
                    op['component1']['attrs'].append(tuple(el.split('=')))
            else:
                # if not an operation or an attribute it should be a component
                if op['operation'] and not op['component2']['name']:
                    # just after the op, so this should be the 2nd component
                    op['component2']['name'] = el
                elif op['operation'] or op['component1']['name']:
                    # e.g. ANT0000A > LNA0000A CXC0000A or ANT0000A LNA0000A
                    # missing operator between two components
                    return {'error': (f"Missing an operator between "
                                      f"components! Line {i}, element {j} "
                                      f"of ltf:\n{ltf}")}
                else:
                    # this should be the first component at this point
                    op['component1']['name'] = el
        operations.append(op)

    # create a standard timestamp for all operations to use
    tstamp = p.Timestamp(int(time.time()))

    # permissions to use for all ops
    perms = session.get('perms', [])

    # process the operations with padloper
    # Operations will be queued and run sequentially, with each operation
    # consisting of component, a method to run on that component with getattr,
    # and optional args/kwargs. The component can either be an instance of the
    # Component class or the name of the component if it will be created in a
    # previous step.
    op_seq : List[Tuple[p.Component | str, str, List, Dict]] = []
    for o, op in enumerate(operations):
        # handle the merge operation first since we're not creating anything
        if op['operation'] == 'merge':
            c1 = op['component1']['name']
            c2 = op['component2']['name']
            if c2.startswith('+'):
                # expand out the + to dots
                for i in range(1, len(c1)-len(c2)+2):
                    test = c2.replace('+', '.'*i)
                    if all((ch1=='.')or(ch2=='.') for ch1,ch2 in zip(c1,test)):
                        c2 = test
                        break
            if all((ch1 == '.') or (ch2 == '.') for ch1, ch2 in zip(c1, c2)):
                # we have compatible merge strings
                res = ''
                for i in range(max(len(c1), len(c2))):
                    if i < len(c1) and c1[i] != '.':
                        res += c1[i]
                    elif i < len(c2) and c2[i] != '.':
                        res += c2[i]
                    elif i < len(c1):
                        res += c1[i]
                    else:
                        res += c2[i]
            if not res:
                return {'error': (f"Could not merge elements {c1} and "
                                  f"{op['component2']['name']}!")}
            if o+1 < len(operations):
                operations[o+1]['component1']['name'] = res
                c1_attrs = op['component1']['attrs']
                new_attrs = operations[o+1]['component1']['attrs']
                operations[o+1]['component1'].update({
                    'attrs': c1_attrs + new_attrs
                })
            continue

        # fetch or create operation's first component
        c1, c1_exists = p.Component.fetch_or_create(op['component1']['name'],
                                                    op['component1']['attrs'])
        if c1 is None:
            return {'error': (f"Component {op['component1']['name']} does not "
                              f"yet exist in the database, and its component "
                              f"type could not be identified! Please ensure "
                              f"there is a valid sequence matching the "
                              f"component or specify type=<some_type> as an "
                              f"attribute on the component.")}

        # queue the addition of the first component if we need to create it
        if not c1_exists:
            op_seq.append((c1, 'add', [], {'permissions': perms}))

        # format properties as dictionary and remove component attributes
        c1_props = dict(op['component1']['attrs'])
        c1_props.pop('name', None)
        c1_props.pop('type', None)
        c1_props.pop('version', None)

        if not op['operation']:
            # i.e. we're just creating a component and/or adding props
            continue

        # fetch or create second component
        c2, c2_exists = p.Component.fetch_or_create(op['component2']['name'],
                                                    op['component2']['attrs'])
        if c2 is None:
            return {'error': (f"Component {op['component2']['name']} does not "
                              f"yet exist in the database, and its component "
                              f"type could not be identified! Please ensure "
                              f"there is a valid sequence matching the "
                              f"component or specify type=<some_type> as an "
                              f"attribute on the component.")}

        # queue the addition of the second component if we need to create it
        if not c2_exists:
            op_seq.append((c2, 'add', [], {'permissions': perms}))

        # format properties as dictionary and remove component attributes
        c2_props = dict(op['component2']['attrs'])
        c2_props.pop('name', None)
        c2_props.pop('type', None)
        c2_props.pop('version', None)

        # prep the component variables for addition to the operation sequence
        # we'll use the Component objects if they exist, otherwise the names
        comp1 = c1 if c1_exists else op['component1']['name']
        comp2 = c2 if c2_exists else op['component2']['name']

        # queue the addition of properties to component 1
        # @TODO: add properties to nodes

        # queue the addition of properties to component 2
        # @TODO: add properties to nodes

        # handle connection operation
        if op['operation'] == 'connect':
            op_seq.append((comp1, 'connect', [comp2, tstamp],
                           {'permissions': perms}))
            continue

        # handle disconnect operation
        if op['operation'] == 'disconnect':
            op_seq.append((comp1, 'disconnect', [comp2, tstamp],
                           {'permissions': perms}))
            continue

        # handle subcomponent (>>) operation
        if op['operation'] == 'subcomponent':
            op_seq.append((comp2, 'subcomponent_connect', [comp1],
                           {'permissions': perms}))
            continue

        # handle supercomponent (<<) operation
        if op['operation'] == 'supercomponent':
            op_seq.append((comp1, 'subcomponent_connect', [comp2],
                           {'permissions': perms}))
            continue

        # handle replace (<>) operation
        if op['operation'] == 'replace':
            op_seq.append((comp1, 'replace', [comp2],
                           {'disable_time': tstamp, 'permissions': perms}))
            continue

    # execute the operations in sequence
    created_components : Dict[str, p.Component] = {}
    for comp, method, args, kwargs in op_seq:
        if isinstance(comp, p.Component):
            # this is the case if the component already exists in the database
            component = comp
        else:
            # component was created in a previous step, so we need to fetch it
            component = created_components.get(comp)

        # replace component strings in the args
        parsed_args = []
        for arg in args:
            if isinstance(arg, str) and arg in created_components:
                parsed_args.append(created_components[arg])
            else:
                parsed_args.append(arg)

        # fetch the operation on the component
        operation = getattr(component, method)
        operation : Callable[..., p.Component | None]

        # execute the operation with the passed args and kwargs
        res = operation(*parsed_args, **kwargs)
        if isinstance(comp, str) and isinstance(res, p.Component):
            created_components.update({comp: res})
        elif isinstance(comp, p.Component) and isinstance(res, p.Component):
            created_components.update({comp.name: res})

    return {'result': True}
