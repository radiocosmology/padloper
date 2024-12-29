"""
padloper.py

Padloper module. Since it has so much stuff, this contains mainly base classes
and the module variables; derived classes are put in other files that are
imported at the end of this file.

NO: we still need a _base.py class: see below. But we can put the global
variables in *this* file.
https://stackoverflow.com/questions/7799286/how-to-split-a-python-module-into-multiple-files
"""
import datetime
from functools import wraps
from gremlin_python.process.graph_traversal import __, constant
from gremlin_python.process.traversal import Order, P, TextP
import time
import _global as g
from _exceptions import *

permissions_set = {
    # Component:
    # protected
    'Component;add',
    'Component;replace',
    'Component;unset_property',
    'Component;replace_property',
    'Component;disable_property',
    'Component;disconnect',
    'Component;disable_connection',
    'Component;disable_subcomponent',
    'Component;subcomponent_connect',

    # general
    'Component;connect',
    'Component;set_property',

    # unprotected
    # 'Component;get_property',
    # 'Component;get_all_properties',
    # 'Component;get_all_properties_of_type',
    # 'Component;get_connections',
    # 'Component;get_list',
    # 'Component;get_count',
    # 'Component;get_all_flags',
    # 'Component;get_subcomponents',
    # 'Component;get_subcomponent',
    # 'Component;get_supercomponents',
    # 'Component;added_to_db',
    # 'Component;from_db',
    # 'Component;from_id',
    # 'Component;as_dict',

    # Component types:
    # protected
    'ComponentType;add',
    'ComponentType;replace',

    # unprotected
    # 'ComponentType;as_dict',
    # 'ComponentType;added_to_db',
    # 'ComponentType;from_db',
    # 'ComponentType;from_id',
    # 'ComponentType;get_names_of_types_and_versions',
    # 'ComponentType;get_list',
    # 'ComponentType;get_count',

    # Component version:
    # protected
    'ComponentVersion;add',
    'ComponentVersion;replace',

    # unprotected
#     'ComponentVersion;as_dict',
#     'ComponentVersion;added_to_db',
#     'ComponentVersion;from_db',
#     'ComponentVersion;from_id',
#     'ComponentVersion;get_list',
#     'ComponentVersion;get_count',

    # PropertyType:
    # protected
    'PropertyType;add',
    'PropertyType;replace',

    # Property:
    # protected
    'Property;_add',

    # FlagType:
    # protected
    'FlagType;add',
    'FlagType;replace',

    # FlagSeverity:
    # protected
    'FlagSeverity;add',
    'FlagSeverity;replace',

    # Flag:
    # protected
    'Flag;replace',

    # general
    'Flag;add',
    'Flag;end_flag',
}

CONTINUE HERE: format the following and copy the rest from _permissions. Also go
through and check that permissions are part of everything …

def check_permission(permission, class_name, method_name):
    """Called by the @authenticated decorator."""
    print(f"{class_name};{method_name}")
    if permission is None:
        # Check for global variable.
        # If user is a string:
            # user = User.from_db(name=user)

        # User to be stored as a user vertex.
        try:
            user = g._user['id']
        except Exception as e:
            raise NoPermissionsError("User not set.")

        if isinstance(user, str):
            user = User.from_db(name=user)
        permission = user.get_permissions()

    # Raise error if user does not have all required permissions.
    #
    # Check default permissions (logged in as a valid user).
    # If not '*' in permission:
    # raise NoPermissionsError("Invalid user. Account must be validated by "\
    #                          "an admin.")

    if f"{class_name};{method_name}" in permissions_set and \
        f"{class_name};{method_name}" not in permission:
        raise NoPermissionsError("User does not have the required " +\
                                 "permissions to perform this action.")


def authenticated(func):
    """A custom decorator for authentication of methods."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # get the class name
        class_name = func.__qualname__.split('.')[0]

        # get the method name
        method_name = func.__name__

        # get the permissions
        kw_permissions = kwargs.get('permissions')
        check_permission(kw_permissions, class_name, method_name)
        return func(*args, **kwargs)
    return wrapper

# Hack because we use this built-in function name for a variable at points …
_range = range

def strictraise(strict, err, msg):
    if strict:
        raise err(msg)
    else:
        print(msg)

def set_user(uid):
    """Identify yourself as a user, for when users are recorded.

    Many alterations to the DB are associated with a user. You must call this
    method before making any such changes to the user. Additionally, not all
    users have permission to do all operations (but this is not yet
    implemented).

    This method will need to get more complicated when we use an external
    authentication method ...

    :param uid: The user ID.
    :type attributes: string
    """
    # TODO: get user from db

    g._user = dict()
    g._user["id"] = uid

def _get_user():
    try:
        return g._user["id"]
    except TypeError:
        raise RuntimeError(
            "You must call padloper.set_user() before performing this "\
            "operation."
        )

def _parse_time(t):
    try:
        return int(t.timestamp())
    except AttributeError:
        try:
            return t.time
        except AttributeError:
            return t
    raise RuntimeError("Should not have reached here!")

class Element(object):
    """
    The simplest element. Contains an ID.
    :ivar id: The unique identifier of the element. 

    If id is _VIRTUAL_ID_PLACEHOLDER, then the 
    element is not in the actual graph and only exists client side.
    """

    _id: int

    def __init__(self, id: int):
        """
        Initialize the Element.

        :param id: ID of the element.
        :type id: int
        """

        self._set_id(id)

    def _set_id(self, id: int):
        """Set the _id attribute of this Element to :param id:.

        :param id: ID of the element.
        :type id: int
        """

        self._id = id

    def id(self):
        """Return the ID of the element.
        """

        return self._id

    def __repr__(self):
        return str(self._id)
        

class VertexAttr(object):
    def __init__(self, name, type, edge_class=None, optional=False,
                 default=None, is_list=False, list_len=(0, int(1e10))):
        """A class for describing an attribute of a Vertex, or a connection to 
        another Vertex that classifies the Vertex.

        :param name: The key name of the attribute.
        :type name: str
        :param type: The data type of the attribute. If a subclass of Vertex is
            included, it is understood that this Vertex should be connected to
            one or more vertices of this type, and the edge_class must be set.
        :type type: variable
        :param edge_class: The category of edge by which it is connected to the
            `type` vertex.
        :type edge_class: subclass of Edge
        :param optional: Whether this attribute is required.
        :type optional: bool
        :param default: The default value, for optional attributes.
        :type default: same as `type`
        :param is_list: Whether the attribute takes a list of values (True) or
           just a single value (False).
        :type is_list: bool
        :param list_len: If the values are in a list, you can define a
            (min_length, max_length) here.
        :type list_len: Tuple of two ints/None
        """
        self.name = name
        self.type = type
        self.edge_class = edge_class
        self.optional = optional
        self.default = default
        self.is_list = is_list
        self.list_len = list_len

class Vertex(Element):
    """
    The representation of a vertex. The attributes common to all vertices in
    Padloper are defined by default, while subclasses can customise attributes
    via a list of VertexAttributes in `vertex_attrs`.

    Note that the attribute `category` plays the role of the vertex label, but
    because JanusGraph does not index labels for some reason (at least as of
    April 2024, as far as I am aware), we use a property instead.

    :ivar category: The category of the Vertex.
    :ivar time_added: When this vertex was added to the database (UNIX time).
    :ivar time_disabled: When this vertex was disabled in the database (UNIX 
          time).
    :ivar active: Whether the vertex is disabled or not.
    :ivar replacement: If the vertex has been replaced, then this property
          points towards the vertex that replaced it.
    """

    category: str = None
    primary_attr: str = None
    _vertex_attrs: list = []

    time_added: int
    uid_added: str
    time_disabled: int
    uid_disabled: str
    active: bool
    replacement: int

    def __new__(cls, _id: int = g._VIRTUAL_ID_PLACEHOLDER, 
                 _time_added: int = g._TIMESTAMP_NO_EDITTIME_VALUE,
                 _uid_added: str = None, **kwargs):
        if _id is not g._VIRTUAL_ID_PLACEHOLDER and _id in g._vertex_cache:
            return g._vertex_cache[_id]
        else:
            return object.__new__(cls)

    def __init__(self, _id: int = g._VIRTUAL_ID_PLACEHOLDER, 
                 _time_added: int = g._TIMESTAMP_NO_EDITTIME_VALUE,
                 _uid_added: str = None, **kwargs):
        """
        Initialize the Vertex.

        :param id: ID of the Vertex.
        :type id: int
        """
        self._validate(**kwargs)

        # Create the vertex attributes. Do type checking for DB integrity.
        for va in self._vertex_attrs:
            if va.name in kwargs:
                val = kwargs[va.name]
                if va.is_list:
                    if not isinstance(val, list):
                        val = [val]
                    if len(val) < va.list_len[0] or len(val) > va.list_len[1]:
                        raise TypeError("List length must be in the range "\
                                        "[%d, %d]\n." % (va.list_len[0],
                                                         va.list_len[1]))
                    for v in val:
                        if not isinstance(v, va.type):
                            raise TypeError("Keyword \"%s\" should contain "\
                                            "only type %s." %\
                                            (va.name, va.type))
                else:
                    if not isinstance(val, va.type) and val is not None and \
                       not va.optional:
                        raise TypeError("Keyword \"%s\" should be of type %s."%\
                                        (va.name, va.type))
            else:
                if va.optional:
                    val = va.default
                else:
                    raise TypeError("%s() missing required keyword \"%s\"." %\
                                    (self.__class__.__name__, va.name))
            setattr(self, va.name, val)

        # Check to see that there are no extraneous keywords.
        for k in kwargs.keys():
            if not hasattr(self, k):
                raise TypeError("Unknown keyword %s." % k)

        self.time_added = _time_added
        self.uid_added = _uid_added
        self.time_disabled = g._TIMESTAMP_NO_EDITTIME_VALUE
        self.uid_disabled = None
        self.replacement = 0
        self.active = True
        Element.__init__(self, _id)

    def _validate(self, **kwargs):
        """This method gets called at the beginning of __init__(); overload it
        in a subclass if you want to make use of it."""
        pass

    @classmethod
    def _attrs_query(cls, d, allow_disabled):
        """Helper class for from_db() and from_id()."""
        projector = []
        for a in cls._vertex_attrs:
            if issubclass(a.type, Timestamp):
                projector.extend(["%s_time" % a.name,
                                  "%s_uid" % a.name,
                                  "%s_edit_time" % a.name,
                                  "%s_comments" % a.name])
            else:
                projector.append(a.name)

        if not allow_disabled:
            d = d.has("active", True)
        d = d.project("id", "time_added", "uid_added", "time_disabled",
                      "uid_disabled", *projector)\
             .by(__.id_())\
             .by(__.values("time_added"))\
             .by(__.values("uid_added"))\
             .by(__.values("time_disabled"))\
             .by(__.values("uid_disabled"))
        for a in cls._vertex_attrs:
            if issubclass(a.type, Vertex):
                if allow_disabled:
                    d = d.by(__.both(a.edge_class.category).id_().fold())
                else:
                    d = d.by(__.both(a.edge_class.category) \
                         .has("active", True).id_().fold())
            elif issubclass(a.type, Timestamp):
                d = d.by(__.values("%s_time" % a.name))\
                     .by(__.values("%s_uid" % a.name))\
                     .by(__.values("%s_edit_time" % a.name))\
                     .by(__.values("%s_comments" % a.name))
            else:
                if a.is_list:
                    d = d.by(__.values(a.name).fold())
                else:
                    d = d.by(__.values(a.name))
        return d

    @classmethod
    def from_db(cls, primary_attr: str, allow_disabled: bool = False):
        """Query the database and return an instance of the Vertex by searching
        for its primary attribute (typically "name").
        
        :param primary_attr: The primary attribute name of the component 
            serverside.
        :type primary_attr: str
        :param allow_disabled: Whether to only select vertices with active=True.
        :type allow_disabled: bool

        :return: The vertex.
        :rtype: Vertex subclass.

        """
        d = g.t.V()\
             .has("category", cls.category)\
             .has(cls.primary_attr, primary_attr)
        d = cls._attrs_query(d, allow_disabled)
        try:
            d = d.next()
        except StopIteration:
            raise NotInDatabase("Could not find %s in the DB." %\
                                primary_attr)

        return cls._from_attrs(d) 

    @classmethod
    def from_id(cls, id: int, allow_disabled: bool = False):
        """Query the database and return a Vertex subclass instance based on
        the ID.

        :param id: The serverside ID of the vertex.
        :type id: int
        :return: Return a Vertex subclass instance from that ID.
        :param allow_disabled: Whether to only select vertices with active=True.
        :type allow_disabled: bool

        :rtype: Vertex subclass
        """
        if id not in g._vertex_cache:
            d = g.t.V(id)
            d = cls._attrs_query(d, allow_disabled)
            try:
                d = d.next()
            except StopIteration:
                raise NotInDatabase

            return cls._from_attrs(d)
        else:
            return g._vertex_cache[id]

    @classmethod
    def _from_attrs(cls, attrs):
        """Create the Vertex from its vertex attributes and edge IDs.

        :param attrs: The attributes as stored in the database, together with
            IDs of the vertices connected to it.
        :type attrs: dict

        :return: The vertex
        :rtype: Vertex or one of its subclasses.
        """
        arg = {"_id": attrs["id"],
               "_time_added": attrs["time_added"],
               "_uid_added": attrs["uid_added"]}
        for a in cls._vertex_attrs:
            if issubclass(a.type, Vertex):
                len_a = len(attrs[a.name])
                if a.is_list:
                    if len_a < a.list_len[0] or len_a > a.list_len[1]:
                        raise ValueError("Number of %s connexions (%d) is "\
                                         "outside allowed range (%d, %d)." %\
                                         (a.type.__class__.__name__,
                                          len_a, a.list_len[0], a.list_len[1]))
                    val = [Vertex._cache_vertex(a.type.from_id(i_attr)) \
                           for i_attr in attrs[a.name]]
                elif len_a > 1:
                    raise ValueError("Only one %s should exist for %s." %
                                     (a.type.__class__.__name__, a.name))
                elif len_a == 1:
                    val = Vertex._cache_vertex(a.type.from_id(attrs[a.name][0]))
                else:
                    if a.optional:
                        val = None
                    else:
                        raise ValueError("A %s is required for %s." %
                                         (a.type.__class__.__name__, a.name))
                arg[a.name] = val
            elif issubclass(a.type, Timestamp):
                arg[a.name] = Timestamp._from_dict(attrs, "%s_" % a.name)
            else:
                arg[a.name] = attrs[a.name]

        return Vertex._cache_vertex(cls(**arg))

    @classmethod
    def _cache_vertex(cls, vertex):
        """Add a vertex and its ID to the vertex cache if not already added,
        and return this new cached vertex. 

        TODO: Raise an error if already cached, because that'd mean there's
        an implementation error with the caching.
        """
        if vertex.id() not in g._vertex_cache:
            if not vertex.in_db():
                raise NotInDatabase("Was expecting Vertex ID to be in the "\
                                    "database since it has an ID.")
            g._vertex_cache[vertex.id()] = vertex
        return g._vertex_cache[vertex.id()]


    @authenticated
    def add(self, strict_add=False, permissions=None):
        """Add the vertex to the Janusgraph DB.

        :param strict_add: If False, then do not throw an error if the vertex
            already exists.
        :type strict_add: bool

        :return: self
        :rtype: self
        """
        if self.in_db():
            strictraise(strict_add, VertexAlreadyAddedError,
                        f"Vertex already exists in the database.")
            return self.__class__.from_db(self.name)
        else:
            self.uid_added = _get_user()
            self.time_added = int(time.time())
            self.active = True
            self.replacement = 0
            self.time_disabled = g._TIMESTAMP_NO_EDITTIME_VALUE

            t = g.t.addV().property('category', self.category) \
                   .property('time_added', self.time_added) \
                   .property('uid_added', self.uid_added) \
                   .property('time_disabled', self.time_disabled) \
                   .property('uid_disabled', self.uid_disabled) \
                   .property('active', self.active) \
                   .property('replacement', self.replacement)

            edges = []
            for a in self._vertex_attrs:
                if issubclass(a.type, Vertex):
                    # If the "attribute" is a connexion to another vertex, then
                    # create the edge; also create the vertex if it does not
                    # exist.
                    if getattr(self, a.name) is not None:
                        if a.is_list:
                            attr_list = getattr(self, a.name)
                        else:
                            attr_list = [getattr(self, a.name)]
                        for attr in attr_list:
                            if not attr.in_db():
                                attr.add()
                            edges.append(
                                a.edge_class(inVertex=attr, outVertex=self))
                    elif not a.optional:
                        raise ValueError("%s should not be None!" % a.name)
                elif issubclass(a.type, Timestamp):
                    if a.is_list:
                        raise NotImplementedError("Lists of Timestamps are "\
                                                  "not yet supported.")
                    val = getattr(self, a.name)
                    t = t.property("%s_time" % a.name, val.time)\
                         .property("%s_uid" % a.name, val.uid)\
                         .property("%s_edit_time" % a.name, val.edit_time)\
                         .property("%s_comments" % a.name, val.comments)
                elif a.is_list:
                    for val in getattr(self, a.name):
                        t = t.property(a.name, val)
                else:
                    t = t.property(a.name, getattr(self, a.name))
            v = t.next()

            # this is NOT the id of a Vertex instance,
            # but rather the id of the GremlinPython vertex returned
            # by the traversal.
            self._set_id(v.id)

            # Add any edges.
            for e in edges:
                e.add()

            Vertex._cache_vertex(self)

            return self

    #@authenticated
    def in_db(self, strict_check=True, allow_removed=False,
              permissions=None) -> bool:
        """Return whether this Vertex has been added to the database.

        :param strict_check: If True, then check whether a vertex exists in the
            database with the same name and category.
        :type strict_check: bool

        :param allow_removed: If False, then vertexes with the "active" property
           set to True in the database are ignored; otherwise they are
           considered to be "in" the DB.
        :type allowed_removed: bool
            
        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """
        if strict_check:
            if self.id() != g._VIRTUAL_ID_PLACEHOLDER:
                q = g.t.V(self.id())
                if not allow_removed:
                    q = q.has("active", True)
                n = q.count().next()
                assert(n == 0 or n == 1)
                if n == 1:
                    return True

            q = g.t.V().has("category", self.__class__.category)
            if not allow_removed:
                q = q.has("active", True)
            if self.primary_attr is not None:
                q = q.has(self.primary_attr, getattr(self, self.primary_attr))
            else:
                # If there is no primary attribute, then we have to check
                # everything …
                q = q.as_("v")
                for va in self._vertex_attrs:
                    if issubclass(va.type, Vertex):
                        # N.B. Todo: need to ensure that the connecting vertex
                        # has a primary_attr … Otherwise it becomes way too
                        # complicated.
                        q = q.bothE(va.edge_class.category)
                        if not allow_removed:
                            q = q.has("active", True)
                        q = q.otherV()
                        pa = va.type.primary_attr
                        if va.is_list:
                            q = q.not_( \
                                  __.has(pa,
                                         P.without(getattr(self, va.name, pa))))
                        else:
                            q = q.has(pa, getattr(getattr(self, va.name), pa))
                        q = q.select("v")
                    elif issubclass(va.type, Timestamp):
                        tt = getattr(self, va.name)
                        if tt is not None:
                            q = q.has("%s_time" % va.name, tt.time)\
                                 .has("%s_uid" % va.name, tt.uid)\
                                 .has("%s_edit_time" % va.name, tt.edit_time)\
                                 .has("%s_comments" % va.name, tt.comments)
                        else:
                            if not va.optional:
                                raise TypeError(
                                    "Was expecting something for "\
                                    "%s since it is not optional." % va.name)
                    else:
                        if va.is_list:
                            q = q.not_( \
                                  __.has(va.name, 
                                         P.without(getattr(self, va.name))))
                        else:
                            q = q.has(va.name, getattr(self, va.name))
            n = q.count().next()
            assert(n == 0 or n == 1)
            if n == 0:
                return False
        elif self.id() == g._VIRTUAL_ID_PLACEHOLDER:
            return False
        return True

    @authenticated
    def replace(self, newVertex, disable_time: int = int(time.time()),
                permissions=None):
        """Replaces the vertex in the JanusGraph DB with the new vertex by
        changing its property 'active' from true to false and transfering
        all the edges to the new vertex. The old vertex contains the ID of
        the new vertex as an attribute.

        :param newVertex: The new vertex that is replacing this vertex.
        :type newVertex: Component

        :param disable_time: When this vertex was disabled in the database (UNIX
            time).
        :type disable_time: int

        :return: newVertex
        :rtype: Vertex
        """
        from _edges import RelationVersionAllowedType, \
                           RelationPropertyAllowedType, RelationFlagSeverity, \
                           RelationFlagType, RelationComponentType, \
                           RelationVersion

        if newVertex.category != self.category:
            raise TypeError("The newVertex must be of the same category as "\
                            "the vertex it is replacing.")

        if not newVertex.in_db(strict_check=False):
            newVertex.add(strict_add=True)

        # The 'replacement' property now points to the new vertex that replaced
        # the self vertex, and it needs to be disabled.
        g.t.V(self.id()).property('replacement', newVertex.id()) \
                        .property('active', False) \
                        .property('time_disabled', disable_time) \
                        .property('uid_disabled', _get_user()).iterate()

        # List of all the properties of the outgoing edges from the self vertex.
        o_edges_values_list = g.t.V(self.id()).bothE().valueMap().toList()

        # List of all the outgoing vertices connected to the self vertex.
        o_vertices_list = g.t.V(self.id()).out().id_().toList()

        # These edges are not copied when replacing a vertex because these edges
        # are selected by the user while adding a new component version, or a
        # new property type, or a new flag or a new component respectively.
        for i in range(len(o_vertices_list)):

            if o_edges_values_list[i]['category'] == \
                RelationVersionAllowedType.category:
                continue
            if o_edges_values_list[i]['category'] == \
                RelationPropertyAllowedType.category:
                continue
            if o_edges_values_list[i]['category'] == \
                RelationFlagSeverity.category:
                continue
            if o_edges_values_list[i]['category'] == \
                RelationFlagType.category:
                continue
            if o_edges_values_list[i]['category'] == \
                RelationComponentType.category:
                continue
            if o_edges_values_list[i]['category'] == \
                RelationVersion.category:
                continue

            # Adds an outgoing edge from the new vertex to the vertices in the
            # list o_vertices_list.
            add_edge_1 = g.t.V(newVertex.id()) \
                            .addE(o_edges_values_list[i]['category'])\
                            .to(__.V().hasId(o_vertices_list[i])).as_('e1')\
                            .select('e1')

            # Copies all the properties of an outgoing edge and stores them in a
            # list.
            traversal = g.t.V(self.id()).outE()[i].properties().toList()

            for i2 in range(len(traversal)):
                add_edge_1 = add_edge_1.property(
                    traversal[i2].key, traversal[i2].value)

                if i2 == (len(traversal)-1):
                    add_edge_1 = add_edge_1.next()

            # After all the properties have been copied from all the edges, the
            # edges of the self vertex are dropped.
            if i == (len(o_vertices_list)-1):
                g.t.V(self.id()).outE().drop().iterate()

        i_edges_values_list = g.t.V(self.id()).inE().valueMap().toList()
        i_vertices_list = g.t.V(self.id()).in_().id_().toList()

        for j in range(len(i_vertices_list)):

            add_edge_2 = g.t.V(newVertex.id()) \
                            .addE(i_edges_values_list[j]['category'])\
                            .from_(__.V().hasId(i_vertices_list[j])).as_('e2')\
                            .select('e2')

            traversal = g.t.V(self.id()).inE()[j].properties().toList()

            for j2 in range(len(traversal)):
                add_edge_2 = add_edge_2.property(
                    traversal[j2].key, traversal[j2].value)

                if j2 == (len(traversal)-1):
                    add_edge_2 = add_edge_2.next()

            if j == (len(i_vertices_list)-1):
                g.t.V(self.id()).inE().drop().iterate()

        return newVertex

    @authenticated
    def disable(self, disable_time: int = int(time.time()), permissions=None):
        """Disables the vertex as well all the edges connected to the vertex by
            setting the property from 'active' from true to false.

        :ivar disable_time: When this vertex was disabled in the database (UNIX
            time).

        """

        # Sets the active property from true to false and registers the time
        # when this self vertex was disabled.
        g.t.V(self.id()).property(
            'active', False).property('time_disabled', disable_time).iterate()

        # Counts the total number of edges connected to this vertex.
        edge_count = g.t.V(self.id()).bothE().toList()

        # Disables all the connnected edges.
        for i in range(len(edge_count)):
            g.t.V(self.id()).bothE()[i].property('active', False).property(
                'time_disabled', disable_time).next()

    def as_dict(self):
        ret = {}
        for a in self._vertex_attrs:
            if issubclass(a.type, Vertex):
                if a.is_list:
                    ret[a.name] = [x.as_dict() for x in getattr(self, a.name)]
                else:
                    if getattr(self, a.name) is not None:
                        ret[a.name] = getattr(self, a.name).as_dict()
            else:
                ret[a.name] = getattr(self, a.name)
        for x in ["time_added", "uid_added", "time_disabled", "uid_disabled",
                  "active", "replacement"]:
            ret[x] = getattr(self, x)
        return ret

    def _in_vertex_cache(self) -> bool:
        """Return whether this vertex ID is in the vertex cache.

        :return: True if vertex ID is in _vertex_cache, false otherwise.
        :rtype: bool
        """

        return self.id() in g._vertex_cache

    @classmethod
    def _list_filter_traversal(cls, filters):
        """Helper class for get_count() and get_list() with common code needed
        by both.
        """
        t = g.t.V().has("category", cls.category)
        ands = []
        for f_or in filters:
            contents = []
            for and_key, and_val in f_or.items():
                # The following is inefficient … But hopefully not limiting.
                va = None
                for va in cls._vertex_attrs:
                    if va.name == and_key:
                        break
                if va is None:
                    raise TypeError("Filter key %s not in Vertex." % and_key)
                if issubclass(va.type, Vertex):
                    contents.append(__.both(va.edge_class.category)\
                                      .has(va.type.primary_attr, and_val))
                else:
                    contents.append(__.has(and_key, and_val))
            if len(contents) > 0:
                ands.append(__.and_(*contents))
        if len(ands) > 0:
            t = t.or_(*ands)
        return t

    @classmethod
    def get_count(cls, filters: list = [], allow_disabled: bool = False):
        """
        Return the number of vertices in the DB of this type, subject to
        provided filters. See docstring for `Vertex.get_list()` for more on 
        filters.
        
        :param filters: See `Vertex.get_list()` documentation.
        :type filters: A list of dictionaries; if a single dictionary is passed
            it is automatically treated as list of length one.

        :param allow_disabled: Whether to only select vertices with active=True.
        :type allow_disabled: bool
        """
        if not isinstance(filters, list):
            filters = [filters]
        
        q = cls._list_filter_traversal(filters)
        if not allow_disabled:
            q = q.has("active", True)
        return q.count().next()

    @classmethod
    def get_list(cls, range: tuple = (0, -1), order_by: list = [], 
                 filters: list = [], allow_disabled: bool = False):
        """
        Return a list of Vertex instances based in the range :param range:,
        optionally filtered and ordered according to specified parameters.

        An example filter: [{"name": TextP.containing("a"), "type": "filter"},
        {"name": TextP.startingWith("antenna_")}]. This will search for vertices
        with "name" containing the letter "a" and type "filter", or with "name"
        starting with "antenna_".

        :param range: The range of ComponentTypes to query. If the second
            coordinate is -1, then the range is (range[0], inf)
        :type range: tuple[int, int]

        :param order_by: A list of what attribute(s) to order the results by;
            each list item can either be a string naming the attribute, or a
            tuple with (attribute, asc/desc); if no "asc" or "desc" is included,
            "asc" is assumed.
        :type order_by: list of str, or of (str, str) tuples. (If just a string
            or just a tuple is passed, then it is automatically converted to a
            list of length one.)

        :param filters: A list of dictionaries, with key-value pairs being
            field name, field value. If the field is a connexion to another
            vertex, then the match will be with its `primary_attr`. Note that
            the field value can use a gremlin method such as
            `TextP.containing()`. Within a dictionary, all matches must occur
            (boolean AND) and between dictionaries in the list, any match may
            occur (boolean OR).
        :type filters: A list of dictionaries; if a single dictionary is passed
            it is automatically treated as list of length one.

        :param allow_disabled: Whether to only select vertices with active=True.
        :type allow_disabled: bool
        """
        # Validation of input.
        if not isinstance(order_by, list) or isinstance(order_by, str):
            order_by = [order_by]
        if not isinstance(filters, list):
            filters = [filters]
        if len(order_by) > 0:
            for i in _range(len(order_by)):
                if not isinstance(order_by[i], tuple):
                    order_by[i] = (order_by[i], "asc")
                assert order_by[i][1].lower() in ("asc", "desc")

        # Build traversal.
        t = cls._list_filter_traversal(filters)
        if len(order_by) > 0:
            t = t.order()
            for ob in order_by:
                # The following is inefficient … But hopefully not limiting.
                va = None
                for va in cls._vertex_attrs:
                    if va.name == ob[0]:
                        break
                if va is None:
                    raise TypeError("Filter key %s not in Vertex." % and_key)
                if issubclass(va.type, Vertex):
                    t = t.by(__.both(va.edge_class.category)\
                               .values(va.type.primary_attr), 
                               Order.asc if ob[1] == "asc" else Order.desc)
                else:
                    t = t.by(ob[0], Order.asc if ob[1] == "asc" else Order.desc)
        t = t.range(range[0], range[1])
        t = cls._attrs_query(t, allow_disabled)
        return [cls._from_attrs(t_i) for t_i in t.toList()]


class Edge(Element):
    """
    The representation of an edge connecting two Vertex instances.

    :ivar inVertex: The Vertex instance that the Edge is going into.
    :ivar outVertex: The Vertex instance that the Edge is going out of.
    :ivar category: The category of the Edge.
    :ivar time_added: When this edge was added to the database (UNIX time).
    :ivar time_disabled: When this edge was disabled in the database (UNIX
        time).
    :ivar active: Whether the edge is disabled or not.
    :ivar replacement: If the edge has been replaced, then this property points
        towards the edge that replaced it.
    """

    inVertex: Vertex
    outVertex: Vertex

    category: str
    time_added: int
    time_disabled: int
    active: bool
    replacement: int

    def __init__(
        self, id: int, inVertex: Vertex, outVertex: Vertex
    ):
        """
        Initialize the Edge.

        :param id: ID of the Edge.
        :type id: int

        :param inVertex: A Vertex instance that the Edge will go into.
        :type inVertex: Vertex

        :param outVertex: A Vertex instance that the Edge will go out of.
        :type outNote: Vertex

        :param outVertex: A Vertex instance that the Edge will go out of.
        :type outNote: Vertex

        :param category: The category of the Edge
        :type category: str
        """

        Element.__init__(self, id)

        self.inVertex = inVertex
        self.outVertex = outVertex

    @authenticated
    def add(self, attributes: dict, permissions=None):
        """Add an edge between two vertices in JanusGraph.

        :param attributes: Attributes to add to the edge. Must have string
        keys and corresponding values.
        :type attributes: dict
        """

        if not self.inVertex.in_db():
            self.inVertex.add()

        if not self.outVertex.in_db():
            self.outVertex.add()

        if self.added_to_db():
            raise EdgeAlreadyAddedError(
                f"Edge already exists in the database."
            )

        else:

            # set time added to now.
            self.time_added = int(time.time())

            self.active = True

            self.replacement = 0

            self.time_disabled = g._TIMESTAMP_NO_EDITTIME_VALUE

            traversal = g.t.V(self.outVertex.id()).addE(self.category) \
                           .to(__.V(self.inVertex.id())) \
                           .property('category', self.category)\
                           .property('time_added', self.time_added)\
                           .property('time_disabled', self.time_disabled)\
                           .property('active', self.active)\
                           .property('replacement', self.replacement)

            for key in attributes:
                traversal = traversal.property(key, attributes[key])

            e = traversal.next()

            self._set_id(e.id)

    @authenticated
    def disable(self, disable_time: int = int(time.time()),
                permissions=None):
        """Disable this connexion by setting active to false.

        :param disable_time: When this edge was disabled in the database.
        :type disable_time: int
        """
        g.t.E(self.id()).property('active', False)\
                        .property('time_disabled', disable_time).iterate()

    def other_vertex(self, v):
        """Given one vertex of this edge, return the other.

        :param v: The vertex on one side of the connexion; the other will be
        returned.
        :return: The other Vertex.
        """
        if v == self.inVertex:
            return self.outVertex
        elif v == self.outVertex:
            return self.inVertex
        else:
           raise ValueError("Vertex not in edge.")

    def __str__(self, connector=" -> "):
        return self.inVertex.name + connector + self.outVertex.name

class Timestamp(object):
    """A timestamp for starting or ending connections, properties, etc.

    :ivar time: The time of the timestamp, in UNIX time.
    :ivar uid: The user who made the timestamp. It is set automatically when the
        instance is created.
    :ivar edit_time: The time of when the timestamp was created, in UNIX time.
        It is set automatically when the instance is created.
    :ivar comments: Any comments about this timestamp.
    """
    time: float
    uid: str
    edit_time: float
    comments: str

    def __init__(self, at_time, comments=""):
        """For creating a new timestamp, rather than reading in from the DB.
        """
        self.uid = _get_user()
        self.time = at_time
        self.edit_time = int(time.time())
        self.comments = comments

    @classmethod
    def from_cal(cls, year, month, day, hour=0, minute=0, second=0,
                 microsecond=0, tzinfo=None, fold=0, comments=""):
        """For creating a new timestamp, rather than reading in from the DB.

        This constructor accepts the same arguments as the datetime.datetime()
        constructor.

        The only other parameter is :param comments:.
        """
        t = int(datetime.datetime(year, month, day, hour, minute, second,
                                  microsecond, tzinfo, fold=fold).timestamp())
        return cls(t, comments)

    @classmethod
    def __raw_init__(cls, at_time, uid, edit_time, comments=""):
        """A private initialiser, for internal use, in which the uid and
        edit_time can be manually specified.
        """
        self = cls.__new__(cls)
        self.time = at_time
        self.uid = uid
        self.edit_time = edit_time
        self.comments = comments
        return self

    @classmethod
    def _from_dict(cls, d, prefix, index=0):
        """Create a timestamp with explicit control over the uid and edit_time.
        When creating a new timestamp, ordinarily you should use the regular
        initialiser that automatically sets the edit_time and uid. This
        initialiser is for cases when you are reading from the DB and need to
        set those values from the DB.

        :param d: The dictionary returned by the database query.
        :type d: dict or list[dict]
        :param prefix: The dictionary should have entries {…, Ptime, Puid,
            Pedit_time, Pcomments, …}, where P is the prefix that you pass
            here.
        :type prefix: str
        :param index: If d is a list of dictionaries, the index to use.
        """
        if isinstance(d, (list,tuple)):
            dd = d[index]
        else:
            dd = d
        return cls.__raw_init__(dd["%stime" % prefix],
                                dd["%suid" % prefix],
                                dd["%sedit_time" % prefix],
                                dd["%scomments" % prefix]
                               )

    @classmethod
    def _no_end(cls):
        """Create a placeholder timestamp.
        This is for when the end timestamp does not yet exist; the timestamp has
        no user id, and reserved values for the time and edit_time.
        """
        return cls.__raw_init__(g._TIMESTAMP_NO_ENDTIME_VALUE, "", 
                                g._TIMESTAMP_NO_EDITTIME_VALUE, comments="")

    def as_dict(self):
        return {
            "time": self.time,
            "uid": self.uid,
            "edit_time": self.edit_time,
            "comments": self.comments
        }

    def as_datetime(self):
        """Return the time as a datetime object."""
        if self.time == g._TIMESTAMP_NO_ENDTIME_VALUE:
            return None
        else:
            return datetime.datetime.fromtimestamp(self.time)


class TimestampedEdge(Edge):
    """An edge that has a timestamp."""
    """Representation of a "rel_connection" edge.

    :ivar start: The starting timestamp, as a `Timestamp` instance.
    :ivar end: The ending timestamp, as a `Timestamp` instance.
    """

    start: Timestamp
    end: Timestamp

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex, start: Timestamp,
        end: Timestamp = None, id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        """Initialize the connection.

        :param inVertex: The Vertex that the edge is going into.
        :type inVertex: Vertex
        :param outVertex: The Vertex that the edge is going out of.
        :type outVertex: Vertex
        :param start: The starting timestamp.
        :type start: Timestamp
        :param end: The ending timestamp.
        :type end: Timestamp or None
        """

        self.start = start
        if end:
            self.end = end
        else:
            self.end = Timestamp._no_end()
        Edge.__init__(self=self, id=id, inVertex=inVertex, outVertex=outVertex)

    def as_dict(self):
        """Return a dictionary representation."""
        return {
            "start": self.start.as_dict(),
            "end": self.end.as_dict()
        }

    @authenticated
    def add(self, permissions=None):
        """Add this timestamped edge to the database.
        """

        attributes = {
            "start_time": self.start.time,
            "start_uid": self.start.uid,
            "start_edit_time": self.start.edit_time,
            "start_comments": self.start.comments,
            "end_time": self.end.time,
            "end_uid": self.end.uid,
            "end_edit_time": self.end.edit_time,
            "end_comments": self.end.comments
        }

        Edge.add(self, attributes=attributes)

    def _end(self, end: Timestamp):
        """Set the end timestamp.

        :param end: The ending timestamp of the connection. 
        :type end: Timestamp
        """

        if not self.added_to_db():
            # Edge not added to DB!
            raise EdgeNotAddedError(
                f"Edge between {self.inVertex} and {self.outVertex} " +
                "does not exist in the database."
            )

        self.end = end

        g.t.E(self.id()).property('end_time', end.time) \
              .property('end_uid', end.uid) \
              .property('end_edit_time', end.edit_time) \
              .property('end_comments', end.comments).iterate()

    def __str__(self, connector=" <-> ", sep=" :: ", trange=" .. ",
                strfmt = "%Y-%m-%d %H:%m:%S"):
        ret = super().__str__(connector=connector) + sep + \
              self.start.as_datetime().strftime(strfmt) + trange
        if self.end.time == g._TIMESTAMP_NO_ENDTIME_VALUE:
            ret += "None"
        else:
            ret += self.end.as_datetime().strftime(strfmt)
        return ret
