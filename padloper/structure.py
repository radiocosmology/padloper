"""
structure.py

Contains methods for storing clientside interface information.
"""
import time
import re
from unicodedata import name

import warnings
from xmlrpc.client import boolean
from attr import attr, attributes

from gremlin_python.process.traversal import Order, P, TextP
from sympy import true
from graph_connection import g
from gremlin_python.process.graph_traversal import __, constant

from exceptions import *

from typing import Optional, List

# A placeholder value for the end_time attribute for a
# relation that is still ongoing.
EXISTING_RELATION_END_PLACEHOLDER = 2**63 - 1

# A placeholder value for the end_edit_time attribute for a relation
# that is still ongoing.
EXISTING_RELATION_END_EDIT_PLACEHOLDER = -1

# Placeholder for the ID of an element that does not exist serverside.
VIRTUAL_ID_PLACEHOLDER = -1

_vertex_cache = dict()


class Element:
    """
    The simplest element. Contains an ID.
    :ivar id: The unique identifier of the element. 

    If id is VIRTUAL_ID_PLACEHOLDER, then the 
    element is not in the actual graph and only exists clienside.
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

    def added_to_db(self) -> bool:
        """Return whether this element is added to the database,
        that is, whether the ID is not the virtual ID placeholder.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return self._id != VIRTUAL_ID_PLACEHOLDER


class Vertex(Element):
    """
    The representation of a vertex. Can contain attributes.

    :ivar category: The category of the Vertex.
    :ivar time_added: When this vertex was added to the database (UNIX time).
    :ivar time_disabled: When this vertex was disabled in the database (UNIX time).
    :ivar active: Whether the vertex is disabled or not.
    :ivar replacement: If the vertex has been replaced, then this property points towards the vertex that replaced it.
    """

    category: str
    time_added: int
    time_disabled: int
    active: bool
    replacement: int

    def __init__(self, id: int):
        """
        Initialize the Vertex.

        :param id: ID of the Vertex.
        :type id: int

        :param category: The category of the Vertex.
        :type category: str

        :param edges: The list of Edge instances that are 
        connected to the Vertex.
        :type edges: List[Edge]
        """

        Element.__init__(self, id)

    def add(self, attributes: dict):
        """
        Add the vertex of category self.category
        to the JanusGraph DB along with attributes from :param attributes:.

        :param attributes: A dictionary of attributes to attach to the vertex.
        :type attributes: dict
        """

        # If already added.
        if self.added_to_db():
            raise VertexAlreadyAddedError(
                f"Vertex already exists in the database."
            )

        else:

            # set time added to now.
            self.time_added = int(time.time())

            self.active = True

            self.replacement = 0

            self.time_disabled = EXISTING_RELATION_END_EDIT_PLACEHOLDER

            traversal = g.addV().property('category', self.category).property('time_added', self.time_added).property(
                'time_disabled', self.time_disabled).property('active', self.active).property('replacement', self.replacement)

            for key in attributes:

                if isinstance(attributes[key], list):
                    for val in attributes[key]:
                        traversal = traversal.property(key, val)

                else:
                    traversal = traversal.property(key, attributes[key])

            v = traversal.next()

            # this is NOT the id of a Vertex instance,
            # but rather the id of the GremlinPython vertex returned
            # by the traversal.
            self._set_id(v.id)

            Vertex._cache_vertex(self)

    def added_to_db(self) -> bool:
        """Return whether this vertex is added to the database,
        that is, whether the ID is not the virtual ID placeholder and perform 
        a query to the database to determine if the vertex 
        has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or
            g.V(self.id()).count().next() > 0
        )

    def _in_vertex_cache(self) -> bool:
        """Return whether this vertex ID is in the vertex cache.

        :return: True if vertex ID is in _vertex_cache, false otherwise.
        :rtype: bool
        """

        return self.id() in _vertex_cache

    @classmethod
    def _cache_vertex(cls, vertex):
        """Add a vertex and its ID to the vertex cache if not already added,
        and return this new cached vertex. 

        TODO: Raise an error if already cached, because that'd mean there's
        an implementation error with the caching.
        """

        if vertex.id() not in _vertex_cache:

            if not vertex.added_to_db():

                # Do nothing?

                return

            _vertex_cache[vertex.id()] = vertex

        return _vertex_cache[vertex.id()]


class Edge(Element):
    """
    The representation of an edge connecting two Vertex instances.

    :ivar inVertex: The Vertex instance that the Edge is going into.
    :ivar outVertex: The Vertex instance that the Edge is going out of.
    :ivar category: The category of the Edge.
    """

    inVertex: Vertex
    outVertex: Vertex

    category: str

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

    def add(self, attributes: dict):
        """Add an edge between two vertices in JanusGraph.

        :param attributes: Attributes to add to the edge. Must have string
        keys and corresponding values.
        :type attributes: dict
        """

        if not self.inVertex.added_to_db():
            self.inVertex.add()

        if not self.outVertex.added_to_db():
            self.outVertex.add()

        if self.added_to_db():
            raise EdgeAlreadyAddedError(
                f"Edge already exists in the database."
            )

        else:
            traversal = g.V(self.outVertex.id()).addE(self.category) \
                .to(__.V(self.inVertex.id())) \
                .property('category', self.category)

            for key in attributes:
                traversal = traversal.property(key, attributes[key])

            e = traversal.next()

            self._set_id(e.id)

    def added_to_db(self) -> bool:
        """Return whether this edge is added to the database,
        that is, whether the ID is not the virtual ID placeholder, and perform a
        query to the database to determine if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or
            g.E(self.id()).count().next() > 0
        )


###############################################################################
#                                   NODES                                     #
###############################################################################

class ComponentType(Vertex):
    """
    The representation of a component type.

    :ivar comments: The comments associated with the component type.
    :ivar name: The name of the component type.
    """

    comments: str
    name: str
    category: str = "component_type"

    def __new__(
        cls, name: str, comments: str = "", id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        """
        Return a ComponentType instance given the desired attributes.

        :param name: The name of the component type. 
        :type name: str

        :param comments: The comments attached to the component type, 
        defaults to ""
        :type comments: str  

        :param id: The serverside ID of the ComponentType, 
        defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id is not VIRTUAL_ID_PLACEHOLDER and id in _vertex_cache:
            return _vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(
        self, name: str, comments: str = "", id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        """
        Initialize the ComponentType vertex with a category, name,
        and comments for self.attributes.

        :param name: The name of the component type. 
        :type name: str

        :param comments: The comments attached to the component type. 
        :type comments: str  
        """

        self.name = name
        self.comments = comments
        Vertex.__init__(self, id=id)

    def add(self):
        """Add this ComponentType vertex to the serverside.
        """

        # If already added.
        if self.added_to_db():
            raise VertexAlreadyAddedError(
                f"ComponentType with name {self.name} " +
                "already exists in the database."
            )

        attributes = {
            'name': self.name,
            'comments': self.comments
        }

        Vertex.add(self=self, attributes=attributes)

    def added_to_db(self) -> bool:
        """Return whether this ComponentType is added to the database,
        that is, whether the ID is not the virtual ID placeholder and perform 
        a query to the database to determine if the 
        vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or (
                g.V().has('category', ComponentType.category)
                .has('name', self.name).count().next() > 0
            )
        )

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a ComponentType instance based on
        component type of name :param name:.

        :param name: The name of the component type.
        :type name: str
        :return: A ComponentType instance with the correct name, comments, and 
        ID.
        :rtype: ComponentType
        """

        d = g.V().has('category', ComponentType.category).has('name', name) \
            .as_('v').valueMap().as_('props').select('v').id().as_('id') \
            .select('props', 'id').next()

        props, id_ = d['props'], d['id']

        Vertex._cache_vertex(
            ComponentType(
                name=name,
                comments=props['comments'][0],
                id=id_
            )
        )

        return _vertex_cache[id_]

    @classmethod
    def from_id(cls, id: int):
        """Query the database and return a ComponentType instance based on
        the ID.

        :param id: The serverside ID of the ComponentType vertex.
        :type id: int
        :return: Return a ComponentType from that ID.
        :rtype: ComponentType
        """

        if id not in _vertex_cache:

            d = g.V(id).valueMap().next()

            Vertex._cache_vertex(
                ComponentType(
                    name=d['name'][0],
                    comments=d['comments'][0],
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def _attrs_to_type(cls, name: str, comments: str, id: int):
        """Given name, comments and id of a ComponentType, see if one
        exists in the cache. If so, return the cached ComponentType.
        Otherwise, create a new one, cache it, and return it.

        :param name: The name of the ComponentType vertex
        :type name: str
        :param comments: Comments associated with the ComponentType vertex
        :type comments: str
        :param id: The ID of the ComponentType vertex.
        :type id: int
        """

        if id not in _vertex_cache:
            Vertex._cache_vertex(
                ComponentType(
                    name=name,
                    comments=comments,
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def get_names_of_types_and_versions(cls):
        """
        Return a list of dictionaries, of the format
        {'type': <ctypename>, 'versions': [<revname>, ..., <revname>]}

        where <ctypename> is the name of the component type, and
        the corresponding value of the 'versions' key is a list of the names
        of all of the versions.

        Used for updating the filter panels.

        :return: a list of dictionaries, of the format
        {'type': <ctypename>, 'versions': [<revname>, ..., <revname>]}
        :rtype: list[dict]
        """

        ts = g.V().has('category', ComponentType.category) \
            .order().by('name', Order.asc) \
            .project('name', 'versions') \
            .by(__.values('name')) \
            .by(
                __.both(RelationVersionAllowedType.category)
            .order().by('name', Order.asc).values('name').fold()
        ) \
            .toList()

        return ts

    @classmethod
    def get_list(
        cls,
        range: tuple,
        order_by: str,
        order_direction: str,
        name_substring: str
    ):
        """
        Return a list of ComponentTypes based in the range :param range:,
        based on the name substring in :param name_substring:, 
        and order them based on :param order_by: 
        in the direction :param order_direction:.

        :param range: The range of ComponentTypes to query. If the second
        coordinate is -1, then the range is (range[1], inf)
        :type range: tuple[int, int]

        :param order_by: What to order the component types by. Must be in
        {'name'}
        :type order_by: str

        :param order_direction: Order the component types by 
        ascending or descending?
        Must be in {'asc', 'desc'}
        :type order_by: str

        :param name_substring: What substring of the name property of the
        component type to filter by.
        :type name_substring: str

        :return: A list of ComponentType instances.
        :rtype: list[ComponentType]
        """

        assert order_direction in {'asc', 'desc'}

        assert order_by in {'name'}

        traversal = g.V().has('category', ComponentType.category) \
            .has('name', TextP.containing(name_substring))

        # if order_direction is not asc or desc, it will just sort by asc.
        # Keep like this if removing the assert above only in production.
        if order_direction == 'desc':
            direction = Order.desc
        else:
            direction = Order.asc

        # How to order the component types.
        # This coalesce thing is done to prevent "property does not exist" error
        # not sure why it happens as the 'name' property will ALWAYS exist...
        # but maybe the traversal somehow catches other vertices not of this
        # type...
        if order_by == 'name':
            traversal = traversal.order().by(
                __.coalesce(__.values('name'), constant("")),
                direction
            )

        # Component type query to DB
        cts = traversal.range(range[0], range[1]) \
            .project('id', 'name', 'comments') \
            .by(__.id()) \
            .by(__.values('name')) \
            .by(__.values('comments')) \
            .toList()

        component_types = []

        for entry in cts:
            id, name, comments = entry['id'], entry['name'], entry['comments']

            component_types.append(
                ComponentType._attrs_to_type(
                    id=id,
                    name=name,
                    comments=comments
                )
            )

        return component_types

    @classmethod
    def get_count(cls, name_substring: str):
        """Return the count of ComponentTypes given a substring of the name
        property.

        :param name_substring: A substring of the name property of the
        ComponentType
        :type name_substring: str

        :return: The number of ComponentTypes that contain 
        :param name_substring: as a substring in the name property.
        :rtype: int
        """

        return g.V().has('category', ComponentType.category) \
            .has('name', TextP.containing(name_substring)) \
            .count().next()


class ComponentVersion(Vertex):
    """
    The representation of a component version.

    :ivar comments: The comments associated with the component type.
    :ivar name: The name of the component type.
    :ivar allowed_type: The ComponentType instance representing the allowed
    type of the component version.
    """

    category: str = "component_version"

    comments: str
    name: str
    allowed_type: ComponentType

    def __new__(
        cls, name: str, allowed_type: ComponentType, comments: str = "",
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        """
        Return a ComponentVersion instance given the desired name, comments, 
        allowed type, and id.

        :param name: The name of the component version.
        :type name: str
        :param comments: The comments attached to the component version,
        defaults to ""
        :str comments: str  

        :param allowed_type: The ComponentType instance representing the 
        allowed component type of the version.
        :type allowed_type: ComponentType

        :param id: The serverside ID of the ComponentType, 
        defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id is not VIRTUAL_ID_PLACEHOLDER and id in _vertex_cache:
            return _vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(
        self, name: str, allowed_type: ComponentType, comments: str = "",
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        """
        Initialize the ComponentVersion vertex.

        :param name: The name of the component version. 
        :param comments: The comments attached to the component version.    
        :param allowed_type: The ComponentType instance representing the 
        allowed component type of the version.
        """

        self.name = name
        self.comments = comments
        self.allowed_type = allowed_type

        Vertex.__init__(self, id=id)

    def add(self):
        """Add this ComponentVersion vertex to the serverside.
        """

        # If already added.
        if self.added_to_db():
            raise VertexAlreadyAddedError(
                f"ComponentVersion with name {self.name} " +
                f"and allowed type {self.allowed_type} " +
                "already exists in the database."
            )

        attributes = {
            'name': self.name,
            'comments': self.comments
        }

        Vertex.add(self=self, attributes=attributes)

        if not self.allowed_type.added_to_db():
            self.allowed_type.add()

        e = RelationVersionAllowedType(
            inVertex=self.allowed_type,
            outVertex=self
        )

        e.add()

    def added_to_db(self) -> bool:
        """Return whether this ComponentVersion is added to the database,
        that is, whether the ID is not the virtual ID placeholder and perform 
        a query to the database to determine if the vertex 
        has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or (
                self.allowed_type.added_to_db() and
                g.V(self.allowed_type.id())
                .both(RelationVersionAllowedType.category)
                .has('name', self.name).count().next() > 0
            )
        )

    @classmethod
    def _attrs_to_version(
        cls,
        name: str,
        comments: str,
        allowed_type: ComponentType,
        id: int
    ):
        """Given name, comments and id of a ComponentType, see if one
        exists in the cache. If so, return the cached ComponentType.
        Otherwise, create a new one, cache it, and return it.

        :param name: The name of the ComponentType vertex
        :type name: str
        :param comments: Comments associated with the ComponentType vertex
        :type comments: str
        :param id: The ID of the ComponentType vertex.
        :type id: int
        """

        if id not in _vertex_cache:
            Vertex._cache_vertex(
                ComponentVersion(
                    name=name,
                    comments=comments,
                    allowed_type=allowed_type,
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def from_db(cls, name: str, allowed_type: ComponentType):
        """Query the database and return a ComponentVersion instance based on
        component version of name :param name: connected to component type
        :param allowed_type:.

        :param name: The name of the component type.
        :type name: str
        :param allowed_type: The ComponentType instance that this component
        version is to be connected to.
        :type allowed_type: ComponentType
        :return: A ComponentVersion instance with the correct name, comments, 
        allowed component type, and ID.
        :rtype: ComponentVersion
        """

        if allowed_type.added_to_db():

            d = g.V(allowed_type.id()) \
                .both(RelationVersionAllowedType.category).has('name', name) \
                .as_('v').valueMap().as_('attrs').select('v').id().as_('id') \
                .select('attrs', 'id').next()

            props, id = d['attrs'], d['id']

            Vertex._cache_vertex(
                ComponentVersion(
                    name=name,
                    comments=props['comments'][0],
                    allowed_type=allowed_type,
                    id=id
                )
            )

            return _vertex_cache[id]

        else:
            raise ComponentTypeNotAddedError(
                f"Allowed type {allowed_type.name} of " +
                f"proposed component version {name} has not yet been added " +
                "to the database."
            )

    @classmethod
    def from_id(cls, id: int):
        """Query the database and return a ComponentVersion instance based on
        the ID.

        :param id: The serverside ID of the ComponentVersion vertex.
        :type id: int
        :return: Return a ComponentVersion from that ID.
        :rtype: ComponentVersion
        """

        if id not in _vertex_cache:

            d = g.V(id).project('attrs', 'type_id').by(__.valueMap()) \
                .by(__.both(RelationVersionAllowedType.category).id()).next()

            t = ComponentType.from_id(d['type_id'])

            Vertex._cache_vertex(
                ComponentVersion(
                    name=d['attrs']['name'][0],
                    comments=d['attrs']['comments'][0],
                    allowed_type=t,
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def get_list(
        cls,
        range: tuple,
        order_by: str,
        order_direction: str,
        filters: list
    ):
        """
        Return a list of ComponentVersions in the range :param range:,
        based on the filters in :param filters:,
        and order them based on  :param order_by: in the direction 
        :param order_direction:.

        :param range: The range of ComponentVersions to query
        :type range: tuple[int, int]

        :param order_by: What to order the component versions by. Must be in
        {'name', 'allowed_type'}
        :type order_by: str

        :param order_direction: Order the component versions by 
        ascending or descending?
        Must be in {'asc', 'desc'}
        :type order_by: str

        :param filters: A list of 2-tuples of the format (name, ctype)
        :type order_by: list

        :return: A list of ComponentVersion instances.
        :rtype: list[ComponentType]
        """

        assert order_direction in {'asc', 'desc'}

        assert order_by in {'name', 'allowed_type'}

        traversal = g.V().has('category', ComponentVersion.category)

        # if order_direction is not asc or desc, it will just sort by asc.
        # Keep like this if removing the assert above only in production.
        if order_direction == 'desc':
            direction = Order.desc
        else:
            direction = Order.asc

        if filters is not None:

            ands = []

            for f in filters:

                assert len(f) == 2

                contents = []

                # substring of component version name
                if f[0] != "":
                    contents.append(__.has('name', TextP.containing(f[0])))

                # component type
                if f[1] != "":
                    contents.append(
                        __.both(RelationVersionAllowedType.category).has(
                            'name',
                            f[1]
                        )
                    )

                if len(contents) > 0:
                    ands.append(__.and_(*contents))

            if len(ands) > 0:
                traversal = traversal.or_(*ands)

        # How to order the component types.
        if order_by == 'name':
            traversal = traversal.order().by('name', direction) \
                .by(
                    __.both(
                        RelationVersionAllowedType.category
                    ).values('name'),
                    Order.asc
            )
        elif order_by == 'allowed_type':
            traversal = traversal.order().by(
                __.both(
                    RelationVersionAllowedType.category
                ).values('name'),
                direction
            ).by('name', Order.asc)

        # Component type query to DB
        cts = traversal.range(range[0], range[1]) \
            .project('id', 'name', 'comments', 'type_id') \
            .by(__.id()) \
            .by(__.values('name')) \
            .by(__.values('comments')) \
            .by(__.both(RelationVersionAllowedType.category).id()) \
            .toList()

        component_versions = []

        for entry in cts:
            id, name, comments, type_id = entry['id'], entry['name'], \
                entry['comments'], entry['type_id']

            t = ComponentType.from_id(id=type_id)

            component_versions.append(
                ComponentVersion._attrs_to_version(
                    id=id,
                    name=name,
                    comments=comments,
                    allowed_type=t
                )
            )
        return component_versions

    @classmethod
    def get_count(cls, filters: list):
        """Return the count of ComponentVersions given a list of filters

        :param filters: A list of 2-tuples of the format (name, ctype)
        :type order_by: list

        :return: The number of ComponentVersions that agree with
        :param filters:.
        :rtype: int
        """

        traversal = g.V().has('category', ComponentVersion.category)

        if filters is not None:

            ands = []

            for f in filters:

                assert len(f) == 2

                contents = []

                # substring of component version name
                if f[0] != "":
                    contents.append(__.has('name', TextP.containing(f[0])))

                # component type
                if f[1] != "":
                    contents.append(
                        __.both(RelationVersionAllowedType.category).has(
                            'name',
                            f[1]
                        )
                    )

                if len(contents) > 0:
                    ands.append(__.and_(*contents))

            if len(ands) > 0:
                traversal = traversal.or_(*ands)

        return traversal.count().next()


class Component(Vertex):
    """
    The representation of a component. 
    Contains a name attribute, ComponentType instance, can contain a
    ComponentVersion and can contain a Flag

    :ivar name: The name of the component
    :ivar type: The ComponentType instance representing the 
    type of the component.
    :ivar version: Optional ComponentVersion instance representing the
    version of the component.

    """

    category: str = "component"

    name: str
    type: ComponentType
    version: ComponentVersion = None

    def __new__(
        cls, name: str, type: ComponentType,
        version: ComponentVersion = None,
        id: int = VIRTUAL_ID_PLACEHOLDER,
        time_added: int = -1
    ):
        """
        Return a Component instance given the desired name, component type,
        and version.

        :param name: The name of the Component.
        :type name: str

        :param type: The component type of the Component.
        :type type: ComponentType

        :param version: The ComponentVersion instance representing the 
        version of the Component.
        :type version: ComponentVersion

        :param id: The serverside ID of the ComponentType, 
        defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id is not VIRTUAL_ID_PLACEHOLDER and id in _vertex_cache:
            return _vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(
        self, name: str, type: ComponentType,
        version: ComponentVersion = None,
        id: int = VIRTUAL_ID_PLACEHOLDER,
        time_added: int = -1
    ):
        """
        Initialize the Component vertex.

        :param name: The name of the component version. 
        :param type: A ComponentType instance representing the type of the
        component.
        :param version: A ComponentVersion instance representing the 
        version of the component, optional.
        """

        self.name = name
        self.type = type
        self.version = version
        self.time_added = time_added

        Vertex.__init__(self, id=id)

    def __str__(self):

        if self.version is None:
            version_text = "no version"

        else:
            version_text = 'version "{self.version.name}"'

        return f'Component of name "{self.name}", \
            type "{self.type.name}", \
            {version_text}, id {self.id()}'

    def add(self):
        """Add this Component to the serverside.
        """

        if self.added_to_db():
            raise VertexAlreadyAddedError(
                f"Component with name {self.name} " +
                "already exists in the database."
            )

        attributes = {
            'name': self.name
        }

        Vertex.add(self, attributes)

        if self.version is not None:
            if not self.version.added_to_db():
                self.version.add()

            rev_edge = RelationVersion(
                inVertex=self.version,
                outVertex=self
            )

            rev_edge._add()

        if not self.type.added_to_db():
            self.type.add()

        type_edge = RelationComponentType(
            inVertex=self.type,
            outVertex=self
        )

        type_edge.add()

    def get_property(self, property_type, time: int, kind: bool):
        """
        Given a property type, get a property of this component active at time
        :param time:. 

        :param property_type: The type of the property to extract
        :type property_type: PropertyType
        :param time: The time to check the active property at.
        :type time: int

        :param kind: This parameter controls what kind of output is returned contingent on whether the get_property method is being called by set_property method or unset_property method. If it is true, then that means set_property method is calling the get_property method and if it is false, then unset_property method is calling the get_property method.
        :type kind: boolean
        """

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not property_type.added_to_db():
            raise PropertyTypeNotAddedError(
                f"Property type {property_type.name} of component {self.name} " +
                "has not yet been added to the database."
            )

        # list of property vertices of this property type
        # and active at this time
        vs = g.V(self.id()).bothE(RelationProperty.category) \
            .has('start_time', P.lte(time)) \
            .has('end_time', P.gt(time)).otherV().as_('v') \
            .both(RelationPropertyType.category) \
            .has('name', property_type.name) \
            .select('v').toList()

        # If no such vertices found
        if len(vs) == 0:
            if kind:
                return None
            else:
                raise ComponentPropertyStartTimeExceedsInputtedTime(
                    f"{self.name} has no property with the given combination of time and property type. Make sure time inputted is later than property start time."
                )

        # There should be only one!

        assert len(vs) == 1

        return Property.from_id(vs[0].id)

    def get_all_properties(self):
        """Return all properties, along with their edges of this component as
        a tuple of the form (Property, RelationProperty)

        :rtype: tuple[Property, RelationProperty]
        """

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # list of property vertices of this property type
        # and active at this time
        query = g.V(self.id()).bothE(RelationProperty.category) \
            .as_('e').valueMap().as_('edge_props') \
            .select('e').otherV().id().as_('vertex_id') \
            .select('edge_props', 'vertex_id').toList()

        # Build up the result of format (property vertex, relation)
        result = []

        for q in query:
            prop = Property.from_id(q['vertex_id'])
            edge = RelationProperty(
                inVertex=prop,
                outVertex=self,
                start_time=q['edge_props']['start_time'],
                start_uid=q['edge_props']['start_uid'],
                start_edit_time=q['edge_props']['start_edit_time'],
                start_comments=q['edge_props']['start_comments'],
                end_time=q['edge_props']['end_time'],
                end_uid=q['edge_props']['end_uid'],
                end_edit_time=q['edge_props']['end_edit_time'],
                end_comments=q['edge_props']['end_comments'],
            )
            result.append((prop, edge))

        return result

    def get_all_properties_of_type(
        self, property_type,
        from_time: int = -1,
        to_time: int = EXISTING_RELATION_END_PLACEHOLDER
    ):
        """
        Given a property type, return all edges that connected them between time
        :param from_time: and to time :param to_time: as a list.

        :param property_type: The property type of the desired properties
        to consider.
        :type component: PropertyType
        :param from_time: Lower bound for time range to consider properties, 
        defaults to -1
        :type from_time: int, optional
        :param to_time: Upper bound for time range to consider properties, 
        defaults to EXISTING_RELATION_END_PLACEHOLDER
        :type to_time: int, optional

        :rtype: list[RelationProperty]
        """

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not property_type.added_to_db():
            raise PropertyTypeNotAddedError(
                f"Property type {property_type.name} of component {self.name} " +
                "has not yet been added to the database."
            )

        edges = g.V(self.id()).bothE(RelationProperty.category)

        if to_time < EXISTING_RELATION_END_PLACEHOLDER:
            edges = edges.has('start_time', P.lt(to_time))

        edges = edges.has('end_time', P.gt(from_time)) \
            .as_('e').otherV().as_('v') \
            .both(RelationPropertyType.category) \
            .has('name', property_type.name) \
            .select('e').order().by(__.values('start_time'), Order.asc) \
            .project('properties', 'id').by(__.valueMap()).by(__.id()).toList()

        return [RelationProperty(
            inVertex=self, outVertex=property_type,
            start_time=e['properties']['start_time'],
            start_uid=e['properties']['start_uid'],
            start_edit_time=e['properties']['start_edit_time'],
            start_comments=e['properties']['start_comments'],
            end_time=e['properties']['end_time'],
            end_uid=e['properties']['end_uid'],
            end_edit_time=e['properties']['end_edit_time'],
            end_comments=e['properties']['end_comments'],
            id=e['id']['@value']['relationId']  # weird but you have to
        ) for e in edges]

    def get_all_flags(self):
        """Return all flags connected to this component of the form (Flag)

        :rtype: [Flag]
        """

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # list of flag vertices of this flag type and flag severity and active at this time.

        query = g.V(self.id()).bothE(
            RelationFlagComponent.category).otherV().id().toList()

        # Build up the result of format (flag vertex)
        result = []

        for q in query:
            flag = Flag.from_id(q)
            result.append((flag))

        return result

    def get_all_subcomponents(self):
        """Return all subcomponents connected to this component of the form (Component)

        :rtype: [Component]
        """

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        query = g.V(self.id()).inE(
            RelationSubcomponent.category).otherV().id().toList()

        # Build up the result of format (flag vertex)
        result = []

        for q in query:
            subcomponent = Component.from_id(q)
            result.append((subcomponent))

        return result

    def get_all_supercomponents(self):
        """Return all supercomponents connected to this component of the form (Component)

        :rtype: [Component]
        """

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )
        # Relation as a subcomponent stays the same except now
        # we have outE to distinguish from subcomponents
        query = g.V(self.id()).outE(
            RelationSubcomponent.category).otherV().id().toList()

        # Build up the result of format (flag vertex)
        result = []

        for q in query:
            supercomponent = Component.from_id(q)
            result.append((supercomponent))

        return result

    def set_property(
        self, property, time: int,
        uid: str, end_time: int = EXISTING_RELATION_END_PLACEHOLDER,
        edit_time: int = int(time.time()), comments="",
        force_property: bool = False
    ):
        """
        Given a property :param property:, MAKE A VIRTUAL COPY of it,
        add it, then connect it to the component self at start time
        :start_time:. Return the Property instance that was added.

        :param property: The property to add
        :type property: Property
        :param time: The time at which the property was added (real time)
        :type time: int
        :param uid: The ID of the user that added the property
        :type uid: str
        :param end_time: The time at which the property was unset
        (real time), defaults to EXISTING_RELATION_END_PLACEHOLDER
        :type time: int, optional
        :param edit_time: The time at which the user made the change,
        defaults to int(time.time())
        :type edit_time: int, optional
        :param comments: Comments to add with property change, defaults to ""
        :type comments: str, optional
        """

        end_edit_time = EXISTING_RELATION_END_EDIT_PLACEHOLDER
        end_uid = ""

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        current_property = self.get_property(
            property_type=property.property_type,
            time=time, kind=True
        )

        if current_property is not None:

            if current_property.values == property.values:
                raise PropertyIsSameError(
                    "An identical property of type " +
                    f"{property.property_type.name} for component {self.name} " +
                    f"is already set with values {property.values}."
                )

            else:
                # end that property.
                self.unset_property(
                    property=current_property,
                    time=time,
                    uid=uid,
                    edit_time=edit_time,
                    comments=comments
                )

        else:

            existing_properties = self.get_all_properties_of_type(
                property_type=property.property_type,
                from_time=time
            )

            if len(existing_properties) > 0:
                if force_property:
                    if end_time != EXISTING_RELATION_END_PLACEHOLDER:
                        raise ComponentPropertiesOverlappingError(
                            "Trying to set property of type " +
                            f"{property.property_type.name} for component " +
                            f"{self.name} " +
                            "before an existing property of the same type " +
                            "but with a specified end time; " +
                            "replace the property instead."
                        )

                    else:
                        end_time = existing_properties[0].start_time
                        end_edit_time = edit_time
                        end_uid = uid
                else:
                    raise ComponentSetPropertyBeforeExistingPropertyError(
                        "Trying to set property of type " +
                        f"{property.property_type.name} for component " +
                        f"{self.name} " +
                        "before an existing property of the same type; " +
                        "set 'force_property' parameter to True to bypass."
                    )

        prop_copy = Property(
            values=property.values,
            property_type=property.property_type
        )

        prop_copy._add()

        e = RelationProperty(
            inVertex=prop_copy,
            outVertex=self,
            start_time=time,
            end_time=end_time,
            start_uid=uid,
            end_uid=end_uid,
            start_edit_time=edit_time,
            end_edit_time=end_edit_time,
            start_comments=comments
        )

        e.add()

        return prop_copy

    def unset_property(
        self, property, time: int, uid: str,
        edit_time: int = int(time.time()), comments=""
    ):
        """
        Given a property that is connected to this component,
        set the "end" attributes of the edge connecting the component and
        the property to indicate that this property has been removed from the
        component.

        :param property: The property vertex connected by an edge to the 
        component vertex.
        :type property: Property

        :param time: The time at which the property was removed (real time). This value has to be provided.
        :type time: int

        :param uid: The user that removed the property
        :type uid: str

        :param edit_time: The time at which the 
        user made the change, defaults to int(time.time())
        :type edit_time: int, optional

        :param comments: Comments about the property removal, defaults to ""
        :type comments: str, optional
        """

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not property.added_to_db():
            raise PropertyNotAddedError(
                f"Property of component {self.name} " +
                f"of values {property.values} being unset " +
                "has not been added to the database."
            )

        g.V(property.id()).bothE(RelationProperty.category).as_('e').otherV() \
            .hasId(self.id()).select('e') \
            .has('end_time', EXISTING_RELATION_END_PLACEHOLDER) \
            .property('end_time', time).property('end_uid', uid) \
            .property('end_edit_time', edit_time) \
            .property('end_comments', comments).iterate()

    def connect(
        self, component, time: int, uid: str,
        end_time: int = EXISTING_RELATION_END_PLACEHOLDER,
        edit_time: int = int(time.time()), comments="",
        force_connection: bool = False
    ):
        """Given another Component :param component:,
        connect the two components.

        :param component: Another Component to connect this component to.
        :type component: Component
        :param time: The time at which these components were connected 
        (real time)
        :type time: int
        :param uid: The ID of the user that connected the components
        :type uid: str
        :param end_time: The time at which these components were disconnected
        (real time), defaults to EXISTING_RELATION_END_PLACEHOLDER
        :type time: int, optional
        :param edit_time: The time at which the user made the change,
        defaults to int(time.time())
        :type edit_time: int, optional
        :param comments: Comments to add with the connection, defaults to ""
        :type comments: str, optional
        :param force_connection: If a connection is being added at a time
        before an existing active connection, give it an end time as well,
        defaults to False
        :type force_connection: bool, optional
        """

        end_edit_time = EXISTING_RELATION_END_EDIT_PLACEHOLDER
        end_uid = ""

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not component.added_to_db():
            raise ComponentNotAddedError(
                f"Component {component.name} has not yet " +
                "been added to the database."
            )

        if self.name == component.name:
            raise ComponentConnectToSelfError(
                f"Trying to connect component {self.name} to itself."
            )

        current_connection = self.get_connection(
            component=component,
            time=time
        )

        if current_connection is not None:

            # Already connected!
            raise ComponentsAlreadyConnectedError(
                f"Components {self.name} and {component.name} " +
                "are already connected."
            )

        else:

            existing_connections = self.get_all_connections_with(
                component=component,
                from_time=time
            )

            if len(existing_connections) > 0:
                if force_connection:
                    if end_time != EXISTING_RELATION_END_PLACEHOLDER:
                        raise ComponentsOverlappingConnectionError(
                            "Trying to connect components " +
                            f"{self.name} and {component.name} " +
                            "before an existing connection but with a " +
                            "specified end time; " +
                            "replace the connection instead."
                        )

                    else:
                        end_time = existing_connections[0].start_time
                        end_edit_time = edit_time
                        end_uid = uid
                else:
                    raise ComponentsConnectBeforeExistingConnectionError(
                        "Trying to connect components " +
                        f"{self.name} and {component.name} " +
                        "before an existing connection; set 'force_connection' "
                        + "parameter to True to bypass."
                    )

            current_connection = RelationConnection(
                inVertex=self,
                outVertex=component,
                start_time=time,
                end_time=end_time,
                start_uid=uid,
                end_uid=end_uid,
                start_edit_time=edit_time,
                end_edit_time=end_edit_time,
                start_comments=comments
            )

            current_connection.add()

    def disconnect(
        self, component, time: int, uid: str,
        edit_time: int = int(time.time()), comments=""
    ):
        """Given another Component :param component:, disconnect the two
        components at time :param time:.

        :param component: Another Component to disconnect this component from.
        :type component: Component
        :param time: The time at which these components are disconnected
        (real time)
        :type time: int
        :param uid: The ID of the user that disconnected the components
        :type uid: str
        :param edit_time: The time at which the user made the change,
        defaults to int(time.time())
        :type edit_time: int, optional
        :param comments: Comments to add with the disconnection, defaults to ""
        :type comments: str, optional
        """

        # Done for troubleshooting (so you know which component is not added?)

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not component.added_to_db():
            raise ComponentNotAddedError(
                f"Component {component.name} has not yet " +
                "been added to the database."
            )

        current_connection = self.get_connection(
            component=component,
            time=time
        )

        if current_connection is None:

            # Not connected yet!
            raise ComponentsAlreadyDisconnectedError(
                f"Components {self.name} and {component.name} " +
                "are already disconnected."
            )

        else:
            current_connection._end_connection(
                end_time=time,
                end_uid=uid,
                end_edit_time=edit_time,
                end_comments=comments
            )

    def get_all_connections_at_time(
        self, time: int
    ):
        """
        Given a component, return all connections between this Component and 
        all other components.

        :param time: Time to check connections at. 
        :type from_time: int, optional

        :rtype: list[RelationConnection]
        """

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # list of property vertices of this property type
        # and active at this time
        query = g.V(self.id()).bothE(RelationConnection.category) \
            .has('start_time', P.lte(time)) \
            .has('end_time', P.gt(time)) \
            .as_('e').valueMap().as_('edge_props') \
            .select('e').otherV().id().as_('vertex_id') \
            .select('e').id().as_('edge_id') \
            .select('edge_props', 'vertex_id', 'edge_id').toList()

        # Build up the result of format (property vertex, relation)
        result = []

        for q in query:
            c = Component.from_id(q['vertex_id'])
            edge = RelationConnection(
                inVertex=c,
                outVertex=self,
                start_time=q['edge_props']['start_time'],
                start_uid=q['edge_props']['start_uid'],
                start_edit_time=q['edge_props']['start_edit_time'],
                start_comments=q['edge_props']['start_comments'],
                end_time=q['edge_props']['end_time'],
                end_uid=q['edge_props']['end_uid'],
                end_edit_time=q['edge_props']['end_edit_time'],
                end_comments=q['edge_props']['end_comments'],
                # weird but you have to
                id=q['edge_id']['@value']['relationId']
            )
            result.append(edge)

        return result

    def get_all_connections_with(
        self, component, from_time: int = -1,
        to_time: int = EXISTING_RELATION_END_PLACEHOLDER
    ):
        """
        Given two components, return all edges that connected them between time
        :param from_time: and to time :param to_time: as a list.

        :param component: The other component to check the connections with.
        :type component: Component
        :param from_time: Lower bound for time range to consider connections, 
        defaults to -1
        :type from_time: int, optional
        :param to_time: Upper bound for time range to consider connections, 
        defaults to EXISTING_RELATION_END_PLACEHOLDER
        :type to_time: int, optional

        :rtype: list[RelationConnection]
        """

        # Done for troubleshooting (so you know which component is not added?)
        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not component.added_to_db():
            raise ComponentNotAddedError(
                f"Component {component.name} has not yet " +
                "been added to the database."
            )

        edges = g.V(self.id()).bothE(RelationConnection.category)

        if to_time < EXISTING_RELATION_END_PLACEHOLDER:
            edges = edges.has('start_time', P.lt(to_time))

        edges = edges.has('end_time', P.gt(from_time)) \
            .as_('e').otherV() \
            .hasId(component.id()).select('e') \
            .order().by(__.values('start_time'), Order.asc) \
            .project('properties', 'id').by(__.valueMap()).by(__.id()).toList()

        return [RelationConnection(
            inVertex=self, outVertex=component,
            start_time=e['properties']['start_time'],
            start_uid=e['properties']['start_uid'],
            start_edit_time=e['properties']['start_edit_time'],
            start_comments=e['properties']['start_comments'],
            end_time=e['properties']['end_time'],
            end_uid=e['properties']['end_uid'],
            end_edit_time=e['properties']['end_edit_time'],
            end_comments=e['properties']['end_comments'],
            id=e['id']['@value']['relationId']  # weird but you have to
        ) for e in edges]

    def get_connection(
        self, component, time: int
    ):
        """Given two components, return the edge that connected them at
        time :param time:.

        :param component: The other component to check the connections with.
        :type component: Component
        :param time: The time to check
        :type time: int
        """

        # Done for troubleshooting (so you know which component is not added?)
        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not component.added_to_db():
            raise ComponentNotAddedError(
                f"Component {component.name} has not yet " +
                "been added to the database."
            )

        e = g.V(self.id()).bothE(RelationConnection.category) \
            .has('start_time', P.lte(time)) \
            .has('end_time', P.gt(time)) \
            .as_('e').otherV() \
            .hasId(component.id()).select('e') \
            .project('properties', 'id').by(__.valueMap()).by(__.id()).toList()

        if len(e) == 0:
            return None

        assert len(e) == 1

        return RelationConnection(
            inVertex=self, outVertex=component,
            start_time=e[0]['properties']['start_time'],
            start_uid=e[0]['properties']['start_uid'],
            start_edit_time=e[0]['properties']['start_edit_time'],
            start_comments=e[0]['properties']['start_comments'],
            end_time=e[0]['properties']['end_time'],
            end_uid=e[0]['properties']['end_uid'],
            end_edit_time=e[0]['properties']['end_edit_time'],
            end_comments=e[0]['properties']['end_comments'],
            id=e[0]['id']['@value']['relationId']  # weird but you have to
        )

    def get_all_connections(self):
        """Return all connections between this Component and all other
        components, along with their edges of this component as
        a tuple of the form (Component, RelationConnection)

        :rtype: tuple[Component, RelationConnection]
        """

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # list of property vertices of this property type
        # and active at this time
        query = g.V(self.id()).bothE(RelationConnection.category) \
            .as_('e').valueMap().as_('edge_props') \
            .select('e').otherV().id().as_('vertex_id') \
            .select('edge_props', 'vertex_id').toList()

        # Build up the result of format (property vertex, relation)
        result = []

        for q in query:
            prop = Component.from_id(q['vertex_id'])
            edge = RelationConnection(
                inVertex=prop,
                outVertex=self,
                start_time=q['edge_props']['start_time'],
                start_uid=q['edge_props']['start_uid'],
                start_edit_time=q['edge_props']['start_edit_time'],
                start_comments=q['edge_props']['start_comments'],
                end_time=q['edge_props']['end_time'],
                end_uid=q['edge_props']['end_uid'],
                end_edit_time=q['edge_props']['end_edit_time'],
                end_comments=q['edge_props']['end_comments'],
            )
            result.append((prop, edge))

        return result

    def subcomponent_connect(
            self, component):
        """
        Given another Component :param component:, make it a subcomponent of the current component.

        :param component: Another component that is a subcomponent of the current component.
        :type component: Component
        """

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not component.added_to_db():
            raise ComponentNotAddedError(
                f"Component {component.name} has not yet" +
                "been added to the database."
            )

        if self.name == component.name:
            raise ComponentSubcomponentToSelfError(
                f"Trying to make {self.name} subcomponent to itself."
            )

        current_subcomponent = self.get_subcomponent(
            component=component
        )

        component_to_subcomponent = component.get_subcomponent(
            component=self
        )

        if component_to_subcomponent is not None:
            raise ComponentIsSubcomponentOfOtherComponentError(
                f"Component {self.name} is already a subcomponent of {component.name}"
            )

        if current_subcomponent is not None:

            # Already a subcomponent!
            raise ComponentAlreadySubcomponentError(
                f"component {component.name} is already a subcomponent of component {self.name}"
            )

        else:
            current_subcomponent = RelationSubcomponent(
                inVertex=self,
                outVertex=component
            )

            current_subcomponent.add()

    def get_subcomponent(self, component):
        """Given the component itself and its subcomponent, return the edge between them.

        :param component: The other component which is the subcomponent of the current component.
        :type component: Component
        """

        # Done for troubleshooting (so you know which component is not added?)
        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not component.added_to_db():
            raise ComponentNotAddedError(
                f"Component {component.name} has not yet" +
                "been added to the database."
            )

        e = g.V(self.id()).bothE(RelationSubcomponent.category).as_('e').otherV().hasId(
            component.id()).select('e').project('id').by(__.id()).toList()

        if len(e) == 0:
            return None

        assert len(e) == 1

        return RelationSubcomponent(
            inVertex=self, outVertex=component,
            id=e[0]['id']['@value']['relationId']
        )

    def added_to_db(self) -> bool:
        """Return whether this Component is added to the database,
        that is, whether the ID is not the virtual ID placeholder and perform a 
        query to the database to determine if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or (
                g.V()
                .has('category', Component.category)
                .has('name', self.name).count().next() > 0
            )
        )

    @classmethod
    def _attrs_to_component(self, name, id, type_id, rev_ids, time_added):
        """Given the name ID of the component :param id: and the ID of the 
        component type :param type_id: and a list of the IDs of the
        component version vertices :param rev_ids:, 
        create and return a Component based on that.

        :param name: The name of the component
        :type name: str
        :param id: The ID of the component serverside
        :type id: int
        :param type_id: The ID of its component type vertex serverside
        :type type_id: int
        :param rev_ids: A list of IDs of component version vertices serverside
        :type rev_ids: list
        :param time_added: UNIX timestamp of when the Component was added to DB.
        :type time_added: int
        :return: A Component instance corresponding to :param id:, connected
        to the correct ComponentType and ComponentVersion.
        :rtype: Component
        """

        assert len(g.V(id).toList()) == 1

        Vertex._cache_vertex(ComponentType.from_id(type_id))

        crev = None

        if len(rev_ids) > 1:
            raise ValueError(
                f"More than one component version exists for component {name}."
            )

        if len(rev_ids) == 1:
            crev = Vertex._cache_vertex(
                ComponentVersion.from_id(id=rev_ids[0])
            )

        Vertex._cache_vertex(
            Component(
                name=name,
                id=id,
                type=_vertex_cache[type_id],
                version=crev,
                time_added=time_added
            )
        )

        return _vertex_cache[id]

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a Component instance based on
        name :param name:.

        :param name: The name attribute of the component serverside.
        :type name: str
        """

        d = g.V().has('category', Component.category).has('name', name) \
            .project('id', 'type_id', 'rev_ids', 'time_added') \
            .by(__.id()).by(__.both(RelationComponentType.category).id()) \
            .by(__.both(RelationVersion.category).id().fold()) \
            .by(__.values('time_added')).next()

        id, type_id, rev_ids, time_added = \
            d['id'], d['type_id'], d['rev_ids'], d['time_added']

        return Component._attrs_to_component(
            name,
            id,
            type_id,
            rev_ids,
            time_added
        )

    @classmethod
    def from_id(cls, id: int):
        """Query the database and return a Component instance based on
        the ID :param id:

        :param id: The ID of the component serverside.
        :type id: int
        """
        if id not in _vertex_cache:

            d = g.V(id).project('name', 'type_id', 'rev_ids', 'time_added') \
                .by(__.values('name')) \
                .by(__.both(RelationComponentType.category).id()) \
                .by(__.both(RelationVersion.category).id().fold()) \
                .by(__.values('time_added')).next()

            name, type_id, rev_ids, time_added = \
                d['name'], d['type_id'], d['rev_ids'], d['time_added']

            return Component._attrs_to_component(
                name,
                id,
                type_id,
                rev_ids,
                time_added
            )

        else:
            return _vertex_cache[id]

    @classmethod
    def get_list(cls,
                 range: tuple,
                 order_by: str,
                 order_direction: str,
                 filters: list = []):
        """
        Return a list of Components based in the range :param range:,
        based on the filters in :param filters:, and order them based on 
        :param order_by: in the direction :param order_direction:.

        :param range: The range of Components to query
        :type range: tuple[int, int]

        :param order_by: What to order the components by. Must be in
        {'name', 'type', 'version'}
        :type order_by: str

        :param order_direction: Order the components by ascending or descending?
        Must be in {'asc', 'desc'}
        :type order_by: str

        :param filters: A list of 3-tuples of the format (name, ctype, version)
        :type order_by: list

        :return: A list of Component instances.
        :rtype: list[Component]
        """

        assert order_direction in {'asc', 'desc'}

        assert order_by in {'name', 'type', 'version'}

        # if order_direction is not asc or desc, it will just sort by asc.
        # Keep like this if removing the assert above only in production.
        if order_direction == 'desc':
            direction = Order.desc
        else:
            direction = Order.asc

        traversal = g.V().has('category', Component.category)

        # FILTERS

        if filters is not None:

            ands = []

            for f in filters:

                assert len(f) == 3

                contents = []

                # substring of component name
                if f[0] != "":
                    contents.append(__.has('name', TextP.containing(f[0])))

                # component type
                if f[1] != "":
                    contents.append(
                        __.both(RelationComponentType.category).has(
                            'name',
                            f[1]
                        )
                    )

                    # component version

                    if f[2] != "":
                        contents.append(
                            __.both(RelationVersion.category).has(
                                'name',
                                f[2]
                            )
                        )

                if len(contents) > 0:
                    ands.append(__.and_(*contents))

            if len(ands) > 0:
                traversal = traversal.or_(*ands)

        # chr(0x10FFFF) is the "biggest" character in unicode

        if order_by == 'version':
            traversal = traversal.order() \
                .by(
                    __.coalesce(
                        __.both(RelationVersion.category).values('name'),
                        __.constant(chr(0x10FFFF))
                    ),
                    direction
            ) \
                .by('name', Order.asc) \
                .by(
                    __.both(RelationComponentType.category).values('name'),
                    Order.asc
            )

        elif order_by == 'type':
            traversal = traversal.order() \
                .by(
                    __.both(RelationComponentType.category).values('name'),
                    direction
            ) \
                .by('name', Order.asc) \
                .by(
                    __.coalesce(
                        __.both(RelationVersion.category).values('name'),
                        __.constant(chr(0x10FFFF))
                    ),
                    Order.asc
            )

        else:
            traversal = traversal.order() \
                .by('name', direction) \
                .by(
                    __.both(RelationComponentType.category).values('name'),
                    Order.asc
            ) \
                .by(
                    __.coalesce(
                        __.both(RelationVersion.category).values('name'),
                        __.constant(chr(0x10FFFF))
                    ),
                    Order.asc,
            )

        cs = traversal.range(range[0], range[1]) \
            .project('id', 'name', 'type_id', 'rev_ids', 'time_added') \
            .by(__.id()) \
            .by(__.values('name')) \
            .by(__.both(RelationComponentType.category).id()) \
            .by(__.both(RelationVersion.category).id().fold()) \
            .by(__.values('time_added')) \
            .toList()

        components = []

        for d in cs:
            id, name, type_id, rev_ids, time_added = d['id'], d['name'], \
                d['type_id'], d['rev_ids'], d['time_added']

            components.append(
                Component._attrs_to_component(
                    id=id,
                    name=name,
                    type_id=type_id,
                    rev_ids=rev_ids,
                    time_added=time_added
                )
            )

        return components

    @classmethod
    def get_count(cls, filters: str):
        """Return the count of components given a list of filters.

        :param filters: A list of 3-tuples of the format (name, ctype, version)
        :type order_by: list

        :return: The number of Components.
        :rtype: int
        """

        traversal = g.V().has('category', Component.category)

        # FILTERS

        if filters is not None:

            ands = []

            for f in filters:

                assert len(f) == 3

                contents = []

                # substring of component name
                if f[0] != "":
                    contents.append(__.has('name', TextP.containing(f[0])))

                # component type
                if f[1] != "":
                    contents.append(
                        __.both(RelationComponentType.category).has(
                            'name',
                            f[1]
                        )
                    )

                    # component version

                    if f[2] != "":
                        contents.append(
                            __.both(RelationVersion.category).has(
                                'name',
                                f[2]
                            )
                        )

                if len(contents) > 0:
                    ands.append(__.and_(*contents))

            if len(ands) > 0:
                traversal = traversal.or_(*ands)

        return traversal.count().next()

    @classmethod
    def get_as_dict(cls, name: str):
        """Return a dictionary representation of this Component at time
        :param time:.

        :param name: The name attribute of the Component
        :type name: str

        :param time: The time to check the component at.
        :type time: int

        :return: A dictionary representation of this Components's attributes.
        :rtype: dict
        """

        c = Component.from_db(name)

        prop_dicts = []

        for (prop, rel) in c.get_all_properties():
            prop_dicts.append({
                'values': prop.values,
                'type': {
                    'name': prop.property_type.name,
                    'units': prop.property_type.units
                },
                'start_time': rel.start_time,
                'end_time': rel.end_time,
                'start_uid': rel.start_uid,
                'end_uid': rel.end_uid,
                'start_edit_time': rel.start_edit_time,
                'end_edit_time': rel.end_edit_time,
                'start_comments': rel.start_comments,
                'end_comments': rel.end_comments
            })

        connection_dicts = []

        for (comp, rel) in c.get_all_connections():
            connection_dicts.append({
                'name': comp.name,
                'id': comp.id(),
                'start_time': rel.start_time,
                'end_time': rel.end_time,
                'start_uid': rel.start_uid,
                'end_uid': rel.end_uid,
                'start_edit_time': rel.start_edit_time,
                'end_edit_time': rel.end_edit_time,
                'start_comments': rel.start_comments,
                'end_comments': rel.end_comments
            })

        flag_dicts = []

        for (flag) in c.get_all_flags():
            flag_dicts.append({
                'name': flag.name,
                'start_time': flag.start_time,
                'start_uid': flag.start_uid,
                'start_edit_time': flag.start_edit_time,
                'start_comments': flag.start_comments,
                'end_time': flag.end_time,
                'end_uid': flag.end_uid,
                'end_edit_time': flag.end_edit_time,
                'end_comments': flag.end_comments,
                'type': {
                    'name': flag.flag_type.name,
                    'comments': flag.flag_type.comments
                },
                'severity': {
                    'name': flag.flag_severity.name
                }
            })

        subcomponent_dicts = []

        for (subcomponent) in c.get_all_subcomponents():
            subcomponent_dicts.append({
                'name': subcomponent.name
            })

        supercomponent_dicts = []

        for (supercomponent) in c.get_all_supercomponents():
            supercomponent_dicts.append({
                'name': supercomponent.name
            })

        return {
            'name': c.name,
            'type': {
                'name': c.type.name,
            },
            'version': {
                'name': c.version.name if c.version is not None else ''
            },
            'time_added': c.time_added,
            'properties': prop_dicts,
            'connections': connection_dicts,
            'flags': flag_dicts,
            'subcomponents': subcomponent_dicts,
            'supercomponents': supercomponent_dicts
        }


class PropertyType(Vertex):
    """
    The representation of a property type.

    :ivar name: The name of the property type.
    :ivar units: The units of the values of the properties 
    associated with the property type.
    :ivar allowed_regex: The regular expression for the allowed values of
    the properties associated with this property type.
    :ivar n_values: The expected number of values for the properties of this
    property type.
    :ivar comments: Additional comments about the property type.
    :ivar allowed_types: The allowed component types of the property type 
    Vertex, as a list of ComponentType attributes.
    """

    category: str = "property_type"

    name: str
    units: str
    allowed_regex: str
    n_values: int
    comments: str
    allowed_types: List[ComponentType]

    def __new__(
        cls, name: str, units: str, allowed_regex: str,
        n_values: int, allowed_types: List[ComponentType], comments: str = "",
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        """
        Return a PropertyType instance given the desired attributes.

        :param name: The name of the property type. 
        :type name: str

        :param units: The units which the values of the properties belonging
        to this type are to be in. 
        :type units: str

        :param allowed_regex: The regular expression that the values of the
        properties of this property type must adhere to. 
        :type allowed_regex: str

        :param n_values: The number of values that the properties of this
        property type must have. 
        :type n_values: int

        :param allowed_types: The component types that may have properties
        of this property type.
        :type allowed_types: List[ComponentType]

        :param comments: The comments attached to the property type, 
        defaults to ""
        :str comments: str  

        :param id: The serverside ID of the PropertyType, 
        defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id is not VIRTUAL_ID_PLACEHOLDER and id in _vertex_cache:
            return _vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(
        self, name: str, units: str, allowed_regex: str,
        n_values: int, allowed_types: List[ComponentType], comments: str = "",
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        """
        Initialize a PropertyType instance given the desired attributes.

        :param name: The name of the property type. 
        :type name: str

        :param units: The units which the values of the properties belonging
        to this type are to be in. 
        :type units: str

        :param allowed_regex: The regular expression that the values of the
        properties of this property type must adhere to. 
        :type allowed_regex: str

        :param n_values: The number of values that the properties of this
        property type must have. 
        :type n_values: int

        :param allowed_types: The component types that may have properties
        of this property type.
        :type allowed_types: List[ComponentType]

        :param comments: The comments attached to the property type, 
        defaults to ""
        :str comments: str  

        :param id: The serverside ID of the PropertyType, 
        defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        self.name = name
        self.units = units
        self.allowed_regex = allowed_regex
        self.n_values = n_values
        self.comments = comments
        self.allowed_types = allowed_types

        if len(self.allowed_types) == 0:
            raise PropertyTypeZeroAllowedTypesError(
                f"No allowed types were specified for property type {name}."
            )

        Vertex.__init__(self, id=id)

    def add(self):
        """Add this PropertyType to the serverside.
        """

        # If already added, raise an error!
        if self.added_to_db():
            raise VertexAlreadyAddedError(
                f"PropertyType with name {self.name} " +
                "already exists in the database."
            )

        attributes = {
            'name': self.name,
            'units': self.units,
            'allowed_regex': self.allowed_regex,
            'n_values': self.n_values,
            'comments': self.comments
        }

        Vertex.add(self, attributes)

        for ctype in self.allowed_types:

            if not ctype.added_to_db():
                ctype.add()

            e = RelationPropertyAllowedType(
                inVertex=ctype,
                outVertex=self
            )

            e.add()

    def added_to_db(self) -> bool:
        """Return whether this PropertyType is added to the database,
        that is, whether the ID is not the virtual ID placeholder and perform a 
        query to the database to determine if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or (
                g.V().has('category', PropertyType.category)
                .has('name', self.name).count().next() > 0
            )
        )

    @classmethod
    def _attrs_to_property_type(
        cls,
        name: str, units: str, allowed_regex: str,
        n_values: int, allowed_types: List[ComponentType], comments: str = "",
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        """Given the id and attributes of a PropertyType, see if one
        exists in the cache. If so, return the cached PropertyType.
        Otherwise, create a new one, cache it, and return it.

        :param name: The name of the property type. 
        :type name: str

        :param units: The units which the values of the properties belonging
        to this type are to be in. 
        :type units: str

        :param allowed_regex: The regular expression that the values of the
        properties of this property type must adhere to. 
        :type allowed_regex: str

        :param n_values: The number of values that the properties of this
        property type must have. 
        :type n_values: int

        :param allowed_types: The component types that may have properties
        of this property type.
        :type allowed_types: List[ComponentType]

        :param comments: The comments attached to the property type, 
        defaults to ""
        :type comments: str  

        :param id: The serverside ID of the PropertyType, 
        defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id not in _vertex_cache:
            Vertex._cache_vertex(
                PropertyType(
                    name=name,
                    units=units,
                    allowed_regex=allowed_regex,
                    n_values=n_values,
                    allowed_types=allowed_types,
                    comments=comments,
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a PropertyType instance based on
        name :param name:.

        :param name: The name attribute of the property type
        :type name: str
        """

        d = g.V().has('category', PropertyType.category).has('name', name) \
            .project('id', 'attrs', 'type_ids') \
            .by(__.id()) \
            .by(__.valueMap()) \
            .by(__.both(RelationPropertyAllowedType.category).id().fold()) \
            .next()

        # to access attributes from attrs, do attrs[...][0]
        id, attrs, ctype_ids = d['id'], d['attrs'], d['type_ids']

        if id not in _vertex_cache:

            ctypes = []

            for ctype_id in ctype_ids:
                ctypes.append(ComponentType.from_id(ctype_id))

            Vertex._cache_vertex(
                PropertyType(
                    name=name,
                    units=attrs['units'][0],
                    allowed_regex=attrs['allowed_regex'][0],
                    n_values=attrs['n_values'][0],
                    comments=attrs['comments'][0],
                    allowed_types=ctypes,
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def from_id(cls, id: int):
        """Query the database and return a PropertyType instance based on
        the ID.

        :param id: The serverside ID of the PropertyType vertex.
        :type id: int
        :return: Return a PropertyType from that ID.
        :rtype: PropertyType
        """

        if id not in _vertex_cache:

            d = g.V(id).project('attrs', 'type_ids') \
                .by(__.valueMap()) \
                .by(__.both(RelationPropertyAllowedType.category).id().fold()) \
                .next()

            # to access attributes from attrs, do attrs[...][0]
            attrs, ctype_ids = d['attrs'], d['type_ids']

            ctypes = []

            for ctype_id in ctype_ids:
                ctypes.append(ComponentType.from_id(ctype_id))

            Vertex._cache_vertex(
                PropertyType(
                    name=attrs['name'][0],
                    units=attrs['units'][0],
                    allowed_regex=attrs['allowed_regex'][0],
                    n_values=attrs['n_values'][0],
                    comments=attrs['comments'][0],
                    allowed_types=ctypes,
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def get_list(cls,
                 range: tuple,
                 order_by: str,
                 order_direction: str,
                 filters: list = []):
        """
        Return a list of PropertyTypes in the range :param range:,
        based on the filters in :param filters:,
        and order them based on  :param order_by: in the direction 
        :param order_direction:.

        :param range: The range of PropertyTypes to query
        :type range: tuple[int, int]

        :param order_by: What to order the PropertyTypes by. Must be in
        {'name', 'allowed_type'}
        :type order_by: str

        :param order_direction: Order the PropertyTypes by 
        ascending or descending?
        Must be in {'asc', 'desc'}
        :type order_by: str

        :param filters: A list of 2-tuples of the format (name, ctype)
        :type order_by: list

        :return: A list of PropertyType instances.
        :rtype: list[PropertyType]
        """

        assert order_direction in {'asc', 'desc'}

        assert order_by in {'name', 'allowed_type'}

        traversal = g.V().has('category', PropertyType.category)

        # if order_direction is not asc or desc, it will just sort by asc.
        # Keep like this if removing the assert above only in production.
        if order_direction == 'desc':
            direction = Order.desc
        else:
            direction = Order.asc

        if filters is not None:

            ands = []

            for f in filters:

                assert len(f) == 2

                contents = []

                # substring of property type name
                if f[0] != "":
                    contents.append(__.has('name', TextP.containing(f[0])))

                # component type
                if f[1] != "":
                    contents.append(
                        __.both(RelationPropertyAllowedType.category).has(
                            'name',
                            f[1]
                        )
                    )

                if len(contents) > 0:
                    ands.append(__.and_(*contents))

            if len(ands) > 0:
                traversal = traversal.or_(*ands)

        # How to order the property types.
        if order_by == 'name':
            traversal = traversal.order().by('name', direction) \
                .by(
                    __.both(
                        RelationPropertyAllowedType.category
                    ).values('name'),
                    Order.asc
            )
        elif order_by == 'allowed_type':
            traversal = traversal.order().by(
                __.both(
                    RelationPropertyAllowedType.category
                ).values('name'),
                direction
            ).by('name', Order.asc)

        # Component type query to DB
        pts = traversal.range(range[0], range[1]) \
            .project('id', 'attrs', 'type_ids') \
            .by(__.id()) \
            .by(__.valueMap()) \
            .by(__.both(RelationPropertyAllowedType.category).id().fold()) \
            .toList()

        property_types = []

        for entry in pts:
            id, ctype_ids, attrs = entry['id'], entry['type_ids'], \
                entry['attrs']

            ctypes = []

            for ctype_id in ctype_ids:
                ctypes.append(ComponentType.from_id(ctype_id))

            property_types.append(
                PropertyType._attrs_to_property_type(
                    id=id,
                    name=attrs['name'][0],
                    units=attrs['units'][0],
                    allowed_regex=attrs['allowed_regex'][0],
                    n_values=attrs['n_values'][0],
                    comments=attrs['comments'][0],
                    allowed_types=ctypes,
                )
            )

        return property_types

    @classmethod
    def get_count(cls, filters: list):
        """Return the count of PropertyType given a list of filters

        :param filters: A list of 2-tuples of the format (name, ctype)
        :type order_by: list

        :return: The number of PropertyType that agree with
        :param filters:.
        :rtype: int
        """

        traversal = g.V().has('category', PropertyType.category)

        if filters is not None:

            ands = []

            for f in filters:

                assert len(f) == 2

                contents = []

                # substring of property type name
                if f[0] != "":
                    contents.append(__.has('name', TextP.containing(f[0])))

                # component type
                if f[1] != "":
                    contents.append(
                        __.both(RelationPropertyAllowedType.category).has(
                            'name',
                            f[1]
                        )
                    )

                if len(contents) > 0:
                    ands.append(__.and_(*contents))

            if len(ands) > 0:
                traversal = traversal.or_(*ands)

        return traversal.count().next()

        # traversal = g.V().has('category', PropertyType.category) \
        #     .has('name', TextP.containing(name_substring))

        # # https://groups.google.com/g/gremlin-users/c/FKbxWKG-YxA/m/kO1hc0BDCwAJ
        # if order_by == "name":
        #     traversal = traversal.order().by(
        #         __.coalesce(__.values('name'), constant("")),
        #         direction
        #     )

        # ids = traversal.range(range[0], range[1]).id().toList()

        # property_types = []

        # for id in ids:

        #     property_types.append(
        #         PropertyType.from_id(id)
        #     )

        # return property_types


class Property(Vertex):
    """The representation of a property.

    :ivar values: The values contained within the property.
    :ivar property_type: The PropertyType instance representing the property
    type of this property.
    """

    category: str = "property"

    values: List[str]
    property_type: PropertyType

    def __init__(
        self, values: List[str], property_type: PropertyType,
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):

        # if len(values) != property_type.n_values:

        # print(len(values), property_type.n_values)

        # TODO: This isn't working for some reason.....!!!!!!!!!!!
        # raise PropertyWrongNValuesError

        for val in values:

            # If the value does not match the property type's regex
            if not bool(re.fullmatch(property_type.allowed_regex, val)):
                raise PropertyNotMatchRegexError(
                    f"Property with values {values} of type " +
                    f"{property_type.name} does not match regex " +
                    f"{property_type.allowed_regex} for value {val}."
                )

        self.values = values
        self.property_type = property_type

        Vertex.__init__(self, id=id)

    def _add(self):
        """
        Add this Property to the serverside.
        """

        attributes = {
            'values': self.values
        }

        Vertex.add(self, attributes)

        if not self.property_type.added_to_db():
            self.property_type.add()

        e = RelationPropertyType(
            inVertex=self.property_type,
            outVertex=self
        )

        e.add()

    @classmethod
    def from_id(cls, id: int):
        """Given an ID of a serverside property vertex, 
        return a Property instance. 
        """

        if id not in _vertex_cache:

            d = g.V(id).project('values', 'ptype_id') \
                .by(__.properties('values').value().fold()) \
                .by(__.both(RelationPropertyType.category).id()).next()

            values, ptype_id = d['values'], d['ptype_id']

            if not isinstance(values, list):
                values = [values]

            Vertex._cache_vertex(
                Property(
                    values=values,
                    property_type=PropertyType.from_id(ptype_id),
                    id=id
                )
            )

        return _vertex_cache[id]


class FlagType(Vertex):
    """The representation of a flag type. 

    :ivar name: The name of the flag type.
    :ivar comments: Comments about the flag type.
    """

    category: str = "flag_type"

    name: str
    comments: str

    def __new__(
        cls, name: str, comments: str = "", id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        """
        Return a FlagType instance given the desired attributes.

        :param name: The name of the flag type
        :type name: str

        :param comments: The comments attached to this flag type, defaults to ""
        :type comments: str

        :param id: The serverside ID of the FlagType,
        defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id is not VIRTUAL_ID_PLACEHOLDER and id in _vertex_cache:
            return _vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(
        self, name: str, comments: str = "", id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        """Initialize a FlagType instance given the desired attributes.

        :param name: The name of the flag type
        :type name: str

        :param comments: The comments attached to this flag type, defaults to ""
        :type comments: str

        :param id: The serverside ID of the FlagType,
        defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        self.name = name
        self.comments = comments

        Vertex.__init__(self, id=id)

    def add(self):
        """Add this FlagType to the database.
        """

        # If already added.
        if self.added_to_db():
            raise VertexAlreadyAddedError(
                f"FlagType with name {self.name} " +
                "already exists in the database."
            )

        attributes = {
            'name': self.name,
            'comments': self.comments
        }

        Vertex.add(self=self, attributes=attributes)

    def added_to_db(self) -> bool:
        """Return whether this FlagType is added to the database,
        that is, whether the ID is not the virtual ID placeholder and perform a 
        query to the database to determine if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or (
                g.V().has('category', FlagType.category)
                .has('name', self.name).count().next() == 1
            )
        )

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a FlagType instance based on
        flag type of name :param name:.

        :param name: The name of the flag type.
        :type name: str

        :return: A FlagType instance with the correct name, comments, and 
        ID.
        :rtype: FlagType
        """

        d = g.V().has('category', FlagType.category).has('name', name) \
            .as_('v').valueMap().as_('props').select('v').id().as_('id') \
            .select('props', 'id').next()

        props, id = d['props'], d['id']

        Vertex._cache_vertex(
            FlagType(
                name=name,
                comments=props['comments'][0],
                id=id
            )
        )

        return _vertex_cache[id]

    @classmethod
    def from_id(cls, id: int):
        """Query the database and return a FlagType instance based on
        the ID.

        :param id: The serverside ID of the FlagType vertex.
        :type id: int

        :return: Return a FlagType from that ID.
        :rtype: FlagType
        """

        if id not in _vertex_cache:

            d = g.V(id).valueMap().next()

            Vertex._cache_vertex(
                FlagType(
                    name=d['name'][0],
                    comments=d['comments'][0],
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def _attrs_to_type(cls, name: str, comments: str, id: int):
        """Given name, comments and id of a FlagType, see if one
        exists in the cache. If so, return the cached FlagType.
        Otherwise, create a new one, cache it, and return it.

        :param name: The name of the FlagType vertex
        :type name: str
        :param comments: Comments associated with the FlagType vertex
        :type comments: str
        :param id: The ID of the FlagType vertex.
        :type id: int
        """

        if id not in _vertex_cache:
            Vertex._cache_vertex(
                FlagType(
                    name=name,
                    comments=comments,
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def get_list(
        cls,
        range: tuple,
        order_by: str,
        order_direction: str,
        name_substring: str
    ):
        """
        Return a list of FlagTypes based in the range :param range:,
        based on the name substring in :param name_substring:, 
        and order them based on :param order_by: 
        in the direction :param order_direction:.

        :param range: The range of FlagTypes to query. If the second
        coordinate is -1, then the range is (range[1], inf)
        :type range: tuple[int, int]

        :param order_by: What to order the flag types by. Must be in
        {'name'}
        :type order_by: str

        :param order_direction: Order the flag types by 
        ascending or descending?
        Must be in {'asc', 'desc'}
        :type order_by: str

        :param name_substring: What substring of the name property of the
        flag type to filter by.
        :type name_substring: str

        :return: A list of FlagType instances.
        :rtype: list[FlagType]
        """

        assert order_direction in {'asc', 'desc'}

        assert order_by in {'name'}

        traversal = g.V().has('category', FlagType.category) \
            .has('name', TextP.containing(name_substring))

        # if order_direction is not asc or desc, it will just sort by asc.
        # Keep like this if removing the assert above only in production.
        if order_direction == 'desc':
            direction = Order.desc
        else:
            direction = Order.asc

        # How to order the flag types.
        # This coalesce thing is done to prevent "property does not exist" error
        # not sure why it happens as the 'name' property will ALWAYS exist...
        # but maybe the traversal somehow catches other vertices not of this
        # type...
        if order_by == 'name':
            traversal = traversal.order().by(
                __.coalesce(__.values('name'), constant("")),
                direction
            )

        # Component type query to DB
        cts = traversal.range(range[0], range[1]) \
            .project('id', 'name', 'comments') \
            .by(__.id()) \
            .by(__.values('name')) \
            .by(__.values('comments')) \
            .toList()

        flag_types = []

        for entry in cts:
            id, name, comments = entry['id'], entry['name'], entry['comments']

            flag_types.append(
                FlagType._attrs_to_type(
                    id=id,
                    name=name,
                    comments=comments
                )
            )

        return flag_types

    @classmethod
    def get_count(cls, name_substring: str):
        """Return the count of FlagTypes given a substring of the name
        property.

        :param name_substring: A substring of the name property of the
        FlagType
        :type name_substring: str

        :return: The number of FlagTypes that contain 
        :param name_substring: as a substring in the name property.
        :rtype: int
        """

        return g.V().has('category', FlagType.category) \
            .has('name', TextP.containing(name_substring)) \
            .count().next()


class FlagSeverity(Vertex):
    """
    The representation of a flag severity.

    :ivar name: The name of the severity.
    """
    category: str = "flag_severity"

    name: str

    def __new__(cls, name: str, id: int = VIRTUAL_ID_PLACEHOLDER):
        """
        Return a FlagSeverity instance given the desired attribute.

        :param name: Indicates the severity of a flag.
        :type name: str

        :param id: The serverside ID of the FlagType,
        defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id is not VIRTUAL_ID_PLACEHOLDER and id in _vertex_cache:
            return _vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(self, name: str, id: int = VIRTUAL_ID_PLACEHOLDER):
        """
        Initialize a FlagSeverity instance given the FlagSeverity instance given the desired attributes.

        :param name: Indicates the severity of a flag.
        :type name: str

        :param id: The serverside ID of the FlagType,
        defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        self.name = name

        Vertex.__init__(self, id=id)

    def add(self):
        """Add this FlagSeverity to the database."""

        # If already added.
        if self.added_to_db():
            raise VertexAlreadyAddedError(
                f"FlagSeverity with name {self.name}" +
                "already exists in the database."
            )

        attributes = {
            'name': self.name
        }

        Vertex.add(self=self, attributes=attributes)

    def added_to_db(self) -> bool:
        """
        Return whether this FlagSeverity is added to the database, that is, whether the ID is not the virtual ID placeholder and perform a query to the database to determine if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or (
                g.V().has('category', FlagSeverity.category).has(
                    'name', self.name).count().next() == 1
            )
        )

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a FlagSeverity instance based on Flag Severity name :param name:.

        :param name: Indicated the severity of a flag.
        :type name: str

        :return: A FlagSeverity instance with the correct name and ID.
        :rtype: FlagSeverity.
        """

        d = g.V().has('category', FlagSeverity.category).has('name', name).as_(
            'v').valueMap().as_('props').select('v').id().as_('id').select('props', 'id').next()

        props, id = d['props'], d['id']

        Vertex._cache_vertex(
            FlagSeverity(
                name=name,
                id=id
            )
        )

        return _vertex_cache[id]

    @classmethod
    def from_id(cls, id: int):
        """Query the database and return a FlagSeverity instance based on the ID.

        :param id: The serverside ID of the FlagSeverity vertex.
        :type id: int

        :return: Return a FlagSeverity from that ID.
        :rtype: FlagSeverity
        """

        if id not in _vertex_cache:

            d = g.V(id).valueMap().next()

            Vertex._cache_vertex(
                FlagSeverity(
                    name=d['name'][0],
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def _attrs_to_type(cls, name: str, id: int):
        """Given name of a FlagSeverity, see if one
        exists in the cache. If so, return the cached FlagSeverity.
        Otherwise, create a new one, cache it, and return it.

        :param name: Indicates the severity of flag.
        :type name: str

        :param id: The ID of the ComponentType vertex.
        :type id: int
        """

        if id not in _vertex_cache:
            Vertex._cache_vertex(
                FlagSeverity(
                    name=name,
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def get_list(
        cls,
        range: tuple,
        order_by: str,
        order_direction: str
    ):
        """
        Return a list of FlagSeverity based in the range :param range:, 
        and order them based on :param order_by: 
        in the direction :param order_direction:.

        :param range: The range of FlagSeverity to query. If the second
        coordinate is -1, then the range is (range[1], inf)
        :type range: tuple[int, int]

        :param order_by: What to order the flag severities by. Must be in
        {'name'}
        :type order_by: str

        :param order_direction: Order the flag severities by 
        ascending or descending?
        Must be in {'asc', 'desc'}
        :type order_by: str

        :return: A list of FlagSeverity instances.
        :rtype: list[FlagSeverity]
        """

        assert order_direction in {'asc', 'desc'}

        assert order_by in {'name'}

        traversal = g.V().has('category', FlagSeverity.category) \


        # if order_direction is not asc or desc, it will just sort by asc.
        # Keep like this if removing the assert above only in production.
        if order_direction == 'desc':
            direction = Order.desc
        else:
            direction = Order.asc

        # How to order the flag severities.
        # This coalesce thing is done to prevent "property does not exist" error
        # not sure why it happens as the 'name' property will ALWAYS exist...
        # but maybe the traversal somehow catches other vertices not of this
        # type...
        if order_by == 'name':
            traversal = traversal.order().by('name', direction
                                             )

        # flag severity query to DB
        fs = traversal.range(range[0], range[1]) \
            .project('id', 'name') \
            .by(__.id()) \
            .by(__.values('name')) \
            .toList()

        flag_severities = []

        for entry in fs:
            id, name = entry['id'], entry['name']

            flag_severities.append(
                FlagSeverity._attrs_to_type(
                    id=id,
                    name=name,

                )
            )

        return flag_severities


class Flag(Vertex):
    """
    The representation of a flag component.

    :ivar name: The name of the flag.
    :ivar start_time: The start time of the flag.
    :ivar end_time: The end time of the flag.
    :ivar start_uid: The ID of the user that created the flag.
    :ivar end_uid: The ID of the user that ended the flag.
    :ivar start_edit_time: The time that the flag was started at.
    :ivar end_edit_time: The time that the flag was ended at.
    :ivar start_comments: The comments about starting the flag.
    :ivar end_comments: The comments about ending the flag.
    :ivar flag_severity: The FlagSeverity instance representing the severity of the flag.
    :ivar flag_type: The FlagType instance representing the type of the flag.
    :ivar flag_components: A list of Component instances related to the flag.
    """

    category: str = "flag"

    name: str
    start_time: int
    end_time: int
    start_uid: str
    end_uid: str
    start_edit_time: int
    end_edit_time: int
    start_comments: str
    end_comments: str
    flag_severity: FlagSeverity
    flag_type: FlagType
    flag_components: List[Component]

    def __new__(cls, name: str, start_time: int, start_uid: str, flag_severity: FlagSeverity, flag_type: FlagType,
                start_edit_time: int = int(time.time()), start_comments: str = "", flag_components: List[Component] = [], end_time: float = EXISTING_RELATION_END_PLACEHOLDER, end_uid: str = "", end_edit_time: float = -1, end_comments: str = "", id: int = VIRTUAL_ID_PLACEHOLDER):
        """
        Return a Flag instance given the desired name,start time, end time, start_uid, end_uid, start_edit_time,end_edit_time, start_comments, end_comments, flag severity instance, flag type instance, component instance and id.

        :param name: The name of the flag.
        :type name: str

        :param start_time: The (physical) start time of the flag.
        :type start_time: int

        :param start_uid: The ID of  the user that started the flag.
        :type start_uid: str

        :param start_edit_time: When the flag start event was entered, defaults to int(time.time())
        type: start_edit_time: int

        :param start_comments: Comments associated with starting the flag, defaults to ""
        :type comments: str, optional

        :param flag_severity: The flag severity that indicates the severity of the flag.
        :type flag_severity: FlagSeverity

        :param flag_type: The flag type that indicates the type of the flag.
        :type flag_severity: FlagType

        :param flag_components: A list of The flag components that have this flag.
        :type flag_components: List[Component]

        :param end_time: The (physical) end time of the flag, defaults to EXISTING_RELATION_END_PLACEHOLDER
        :type end_time: int, optional

        :param end_uid: The ID of the user that ended the flag, defaults to ""
        :type end_uid: str, optional

        :param end_edit_time: When the flag end event was entered, defaults to EXISTING_RELATION_END_EDIT_PLACEHOLDER
        :type end_edit_time: int, optional

        :param end_comments: Comments regarding the ending of the flag, defaults to ""
        :type end_comments: str, optional

        """

        if id is not VIRTUAL_ID_PLACEHOLDER and id in _vertex_cache:
            return _vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(
        self, name: str, start_time: int, start_uid: str, flag_severity: FlagSeverity, flag_type: FlagType,
        start_edit_time: int = int(time.time()), start_comments: str = "", flag_components: List[Component] = [], end_time: float = EXISTING_RELATION_END_PLACEHOLDER, end_uid: str = "", end_edit_time: float = -1, end_comments: str = "", id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        self.name = name
        self.start_time = start_time
        self.start_uid = start_uid
        self.start_edit_time = start_edit_time
        self.start_comments = start_comments
        self.flag_severity = flag_severity
        self.flag_type = flag_type
        self.flag_components = flag_components
        self.end_time = end_time
        self.end_uid = end_uid
        self.end_edit_time = end_edit_time
        self.end_comments = end_comments

        Vertex.__init__(self=self, id=id)

    def add(self):
        """
        Add this Flag instance to the database.
        """

        if self.added_to_db():
            raise VertexAlreadyAddedError(
                f"Flag with name {self.name}" +
                "already exists in the database."
            )

        attributes = {
            'name': self.name,
            'start_time': self.start_time,
            'start_uid': self.start_uid,
            'start_edit_time': self.start_edit_time,
            'start_comments': self.start_comments,
            'end_time': self.end_time,
            'end_uid': self.end_uid,
            'end_edit_time': self.end_edit_time,
            'end_comments': self.end_comments
        }

        Vertex.add(self=self, attributes=attributes)

        if not self.flag_type.added_to_db():
            self.flag_type.add()

        e = RelationFlagType(
            inVertex=self.flag_type,
            outVertex=self
        )

        e.add()

        if not self.flag_severity.added_to_db():
            self.flag_severity.add()

        e = RelationFlagSeverity(
            inVertex=self.flag_severity,
            outVertex=self
        )

        e.add()

        for c in self.flag_components:

            if not c.added_to_db():
                c.add()

            e = RelationFlagComponent(
                inVertex=c,
                outVertex=self
            )

            e.add()

    def added_to_db(self) -> bool:
        """Return whether this Flag is added to the database,that is, whether the ID is not the virtual ID placeholder and perform a query to the database if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or (
                g.V().has('category', Flag.category).has('name', self.name).count().next() > 0
            )
        )

    @classmethod
    def _attrs_to_flag(
            cls, name: str, start_time: int, start_uid: str, flag_severity: FlagSeverity, flag_type: FlagType, start_edit_time: int = int(time.time()), start_comments: str = "", flag_components: List[Component] = [], end_time: float = EXISTING_RELATION_END_PLACEHOLDER, end_uid: str = "", end_edit_time: float = -1, end_comments: str = "", id: int = VIRTUAL_ID_PLACEHOLDER):
        """Given the id and attributes of a Flag, see if one exists in the cache. If so, return the cached Flag. Otherwise, create a new one, cache it, and return it.

        :param name: The name of the flag.
        :type name: str

        :param start_time: The (physical) start time of the flag.
        :type start_time: int

        :param start_uid: The ID of  the user that started the flag.
        :type start_uid: str

        :param start_edit_time: When the flag start event was entered, defaults to int(time.time())
        type: start_edit_time: int

        :param start_comments: Comments associated with starting the flag, defaults to ""
        :type comments: str, optional

        :param flag_severity: The flag severity that indicates the severity of the flag.
        :type flag_severity: FlagSeverity

        :param flag_type: The flag type that indicates the type of the flag.
        :type flag_severity: FlagType

        :param flag_components: A list of The flag components that have this flag.
        :type flag_components: List[Component]

        :param end_time: The (physical) end time of the flag, defaults to EXISTING_RELATION_END_PLACEHOLDER
        :type end_time: int, optional

        :param end_uid: The ID of the user that ended the flag, defaults to ""
        :type end_uid: str, optional

        :param end_edit_time: When the flag end event was entered, defaults to EXISTING_RELATION_END_EDIT_PLACEHOLDER
        :type end_edit_time: int, optional

        :param end_comments: Comments regarding the ending of the flag, defaults to ""
        :type end_comments: str, optional

        """

        if id not in _vertex_cache:
            Vertex._cache_vertex(
                Flag(
                    name=name,
                    start_time=start_time,
                    start_uid=start_uid,
                    start_edit_time=start_edit_time,
                    start_comments=start_comments,
                    flag_severity=flag_severity,
                    flag_type=flag_type,
                    flag_components=flag_components,
                    end_time=end_time,
                    end_uid=end_uid,
                    end_edit_time=end_edit_time,
                    end_comments=end_comments,
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a Flag instance based on the name
        :param name:, connected to the necessary Components, FlagType
        instances and FlagSeverity instance.

        :param name: The name of the Flag instance
        :type name: str
        """

        d = g.V().has('category', Flag.category).has('name', name) \
            .project('id', 'attrs', 'type_id', 'severity_id', 'component_ids') \
            .by(__.id()) \
            .by(__.valueMap()) \
            .by(__.both(RelationFlagType.category).id()).by(__.both(RelationFlagSeverity.category).id()) \
            .by(__.both(RelationFlagComponent.category).id().fold()).next()

        id, attrs, type_id, severity_id, component_ids = d['id'], d['attrs'], \
            d['type_id'], d['severity_id'], d['component_ids']

        if id not in _vertex_cache:

            Vertex._cache_vertex(FlagType.from_id(type_id))

            Vertex._cache_vertex(FlagSeverity.from_id(severity_id))

            components = []

            for c_id in component_ids:
                components.append(Component.from_id(c_id))

            Vertex._cache_vertex(
                Flag(
                    name=name,
                    start_time=attrs['start_time'][0],
                    start_uid=attrs['start_uid'][0],
                    start_edit_time=attrs['start_edit_time'][0],
                    start_comments=attrs['start_comments'][0],
                    flag_severity=_vertex_cache[severity_id],
                    flag_type=_vertex_cache[type_id],
                    flag_components=components,
                    end_time=attrs['end_time'][0],
                    end_uid=attrs['end_uid'][0],
                    end_edit_time=attrs['end_edit_time'][0],
                    end_comments=attrs['end_comments'][0],
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def from_id(cls, id: int):
        """Given an ID of a serverside flag vertex, return a Flag instance.
        """

        if id not in _vertex_cache:

            d = g.V(id).project('attrs', 'fseverity_id', 'ftype_id', 'fcomponent_ids').by(__.valueMap()).by(__.both(RelationFlagSeverity.category).id()).by(
                __.both(RelationFlagType.category).id()).by(__.both(RelationFlagComponent.category).id().fold()).next()

            # to access attributes from attrs, do attrs[...][0]
            attrs, fseverity_id, ftype_id, fcomponent_ids = d['attrs'], d[
                'fseverity_id'], d['ftype_id'], d['fcomponent_ids']

            components = []

            for component_id in fcomponent_ids:
                components.append(Component.from_id(component_id))

            Vertex._cache_vertex(
                Flag(
                    name=attrs['name'][0],
                    start_time=attrs['start_time'][0],
                    start_uid=attrs['start_uid'][0],
                    start_edit_time=attrs['start_edit_time'][0],
                    start_comments=attrs['start_comments'][0],
                    flag_severity=FlagSeverity.from_id(fseverity_id),
                    flag_type=FlagType.from_id(ftype_id),
                    flag_components=components,
                    end_time=attrs['end_time'][0],
                    end_uid=attrs['end_uid'][0],
                    end_edit_time=attrs['end_edit_time'][0],
                    end_comments=attrs['end_comments'][0],
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def get_list(cls,
                 range: tuple,
                 order_by: str,
                 order_direction: str,
                 filters: list = []):
        """
        Return a list of Flags in the range :param range:,
        based on the filters in :param filters:,
        and order them based on  :param order_by: in the direction 
        :param order_direction:.

        :param range: The range of Flag to query
        :type range: tuple[int, int]

        :param order_by: What to order the Flag by. Must be in
        {'name', 'flag_type','flag_severity'}
        :type order_by: str

        :param order_direction: Order the Flag by 
        ascending or descending?
        Must be in {'asc', 'desc'}
        :type order_by: str

        :param filters: A list of 3-tuples of the format (name, ftype,fseverity)
        :type order_by: list

        :return: A list of Flag instances.
        :rtype: list[Flag]
        """

        assert order_direction in {'asc', 'desc'}

        assert order_by in {'name', 'flag_type', 'flag_severity'}

        traversal = g.V().has('category', Flag.category)

        # if order_direction is not asc or desc, it will just sort by asc.
        # Keep like this if removing the assert above only in production.
        if order_direction == 'desc':
            direction = Order.desc
        else:
            direction = Order.asc

        if filters is not None:

            ands = []

            for f in filters:

                assert len(f) == 3

                contents = []

                # substring of flag name
                if f[0] != "":
                    contents.append(__.has('name', TextP.containing(f[0])))

                # flag type
                if f[1] != "":
                    contents.append(
                        __.both(RelationFlagType.category).has(
                            'name',
                            f[1]
                        )
                    )

                # flag severity
                if f[2] != "":
                    contents.append(
                        __.both(RelationFlagSeverity.category).has(
                            'name',
                            f[2]
                        )
                    )

                if len(contents) > 0:
                    ands.append(__.and_(*contents))

            if len(ands) > 0:
                traversal = traversal.or_(*ands)

        # How to order the flags.
        if order_by == 'name':
            traversal = traversal.order().by('name', direction) \
                .by(
                    __.both(
                        RelationFlagType.category
                    ).values('name'),
                    Order.asc
            ).by(
                __.both(RelationFlagSeverity.category).values(
                    'name'), Order.asc
            )

        elif order_by == 'flag_type':
            traversal = traversal.order().by(
                __.both(
                    RelationFlagType.category
                ).values('name'),
                direction
            ).by('name', Order.asc).by(
                __.both(
                    RelationFlagSeverity.category
                ).values('name'), Order.asc
            )

        elif order_by == 'flag_severity':
            traversal = traversal.order().by(
                __.both(
                    RelationFlagSeverity.category
                ).values('name'),
                direction
            ).by('name', Order.asc).by(
                __.both(RelationFlagType.category).values('name'), Order.asc
            )

        # flag query to DB
        fs = traversal.range(range[0], range[1]) \
            .project('id', 'attrs', 'ftype_id', 'fseverity_id', 'fcomponent_ids') \
            .by(__.id()) \
            .by(__.valueMap()) \
            .by(__.both(RelationFlagType.category).id()).by(__.both(RelationFlagSeverity.category).id()).by(__.both(RelationFlagComponent.category).id().fold()) \
            .toList()

        flags = []

        for entry in fs:
            id, ftype_id, fseverity_id, fcomponent_ids, attrs = entry['id'], entry['ftype_id'], entry['fseverity_id'], entry['fcomponent_ids'], \
                entry['attrs']

            fcomponents = []

            for fcomponent_id in fcomponent_ids:
                fcomponents.append(Component.from_id(fcomponent_id))

            flags.append(
                Flag._attrs_to_flag(
                    id=id,
                    name=attrs['name'][0],
                    start_time=attrs['start_time'][0],
                    start_uid=attrs['start_uid'][0],
                    start_edit_time=attrs['start_edit_time'][0],
                    start_comments=attrs['start_comments'][0],
                    flag_severity=FlagSeverity.from_id(fseverity_id),
                    flag_type=FlagType.from_id(ftype_id),
                    flag_components=fcomponents,
                    end_time=attrs['end_time'][0],
                    end_uid=attrs['end_uid'][0],
                    end_edit_time=attrs['end_edit_time'][0],
                    end_comments=attrs['end_comments'][0],
                )
            )

        return flags

    @classmethod
    def get_count(cls, filters: str):
        """Return the count of flags given a list of filters.

        :param filters: A list of 3-tuples of the format (name,ftype,fseverity)
        :type order_by: list

        :return: The number of flags.
        :rtype: int
        """
        traversal = g.V().has('category', Flag.category)

        # FILTERS

        if filters is not None:

            ands = []

            for f in filters:

                assert len(f) == 3

                contents = []

                # substring of flag name
                if f[0] != "":
                    contents.append(__.has('name', TextP.containing(f[0])))

                # flag type
                if f[1] != "":
                    contents.append(
                        __.both(RelationFlagType.category).has(
                            'name',
                            f[1]
                        )
                    )

                # flag severity
                if f[2] != "":
                    contents.append(
                        __.both(RelationFlagSeverity.category).has(
                            'name',
                            f[2]
                        )
                    )

                if len(contents) > 0:
                    ands.append(__.and_(*contents))

            if len(ands) > 0:
                traversal = traversal.or_(*ands)

        return traversal.count().next()

    def end_flag(
            self, end_time: int, end_uid: str, end_edit_time: int = int(time.time()), end_comments=""):
        """
        Given a flag, set the "end" attributes of the flag to indicate that this flag has been ended.

        :param time: The time at which the flag was ended (real time). This value has to be provided.
        :type time: int

        :param uid: The user that ended the flag.
        :type uid: str

        :param edit_time: The time at which the user made the change, defaults to int(time.time())
        :type edit_time: int, optional

        :param comments: Comments associated with ending the flag.
        :type comments: str, optional
        """

        if not self.added_to_db():
            raise FlagNotAddedError(
                f"Flag {self.name} has not yet been added to the database."
            )

        self.end_time = end_time
        self.end_uid = end_uid
        self.end_edit_time = end_edit_time
        self.end_comments = end_comments

        g.V(self.id()).property('end_time', end_time).property('end_uid', end_uid).property(
            'end_edit_time', end_edit_time).property('end_comments', end_comments).iterate()


class Permission(Vertex):
    """ The representation of a permission.

    :ivar name: The name of the permission.
    :ivar comments: Comments about the permission.
    """

    category: str = 'permission'

    name: str
    comments: str

    def __new__(
            cls, name: str, comments: str = '', id: int = VIRTUAL_ID_PLACEHOLDER):
        """
        Return a Permission instance given the desired attributes.

        :param name: The name of the permission.
        :type name: str

        :param comments: The comments attached to this permission, defaults to ""
        :type comments: str

        :param id: The serverside ID of the permission, defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id is not VIRTUAL_ID_PLACEHOLDER and id in _vertex_cache:
            return _vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(self, name: str, comments: str = " ", id: int = VIRTUAL_ID_PLACEHOLDER):
        """
        Initialize a Permission instance given the desired attributes.

        :param name: The name of the permission.
        :type name: str

        :param comments: The comments attached to this permission, defaults to ""
        :type comments: str

        :param id: The serverside ID of the permission, defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        self.name = name
        self.comments = comments

        Vertex.__init__(self, id=id)

    def add(self):
        """Add this permission to the database."""

        # if already added, raise an error!
        if self.added_to_db():
            raise VertexAlreadyAddedError(
                f"Permission with name {self.name}" +
                "already exists in the database."
            )

        attributes = {
            'name': self.name,
            'comments': self.comments
        }

        Vertex.add(self=self, attributes=attributes)

    def added_to_db(self) -> bool:
        """
        Return whether this Permission is added to the database, that is, whether the ID is not the Virtual ID placeholder and perform a query to the database to determine if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or (
                g.V().has('category', Permission.category).has(
                    'name', self.name).count().next() == 1
            )
        )

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a Permission instance based on permission :param name.

        :param name: The name of the permission.
        :type name: str

        :return: A Permission instance with the correct name, comments, and ID.
        :rtype: Permission
        """

        d = g.V().has('category', Permission.category).has('name', name).as_(
            'v').valueMap().as_('props').select('v').id().as_('id').select('props', 'id').next()

        props, id = d['props'], d['id']

        Vertex._cache_vertex(
            Permission(
                name=name,
                comments=props['comments'][0],
                id=id
            )
        )

        return _vertex_cache[id]

    @classmethod
    def from_id(cls, id: int):
        """ Query the database and return a Permission instance based on the ID.

        :param id: The serverside ID of the Permission vertex.
        :type id: int

        :return: Return a Perimssion from that ID.
        :rtype: Permission
        """

        if id not in _vertex_cache:
            d = g.V(id).valueMap().next()

            Vertex._cache_vertex(
                Permission(
                    name=d['name'][0],
                    comments=d['comments'][0],
                    id=id
                )
            )

        return _vertex_cache[id]


class UserGroup(Vertex):
    """ The representation of a user group.

    :ivar name: The name of the user group.
    :ivar comments: The comments assocaited with the group.
    :ivar permission: A list of Perimssion instances associated with this group.
    """

    category: str = 'user_group'

    name: str
    comments: str
    permission: List[Permission]

    def __init__(self, name: str, comments: str, permission: List[Permission], id: int = VIRTUAL_ID_PLACEHOLDER):

        self.name = name
        self.comments = comments
        self.permission = permission

        if len(self.permission) == 0:
            raise UserGroupZeroPermissionError(
                f"No permission were specified for user group {name}"
            )

        Vertex.__init__(self=self, id=id)

    def add(self):
        """
        Add this UserGroup instance to the database.
        """

        if self.added_to_db():
            raise VertexAlreadyAddedError(
                f"UserGroup with name {self.name}" +
                "already exists in the database."
            )

        attributes = {
            'name': self.name,
            'comments': self.comments
        }

        Vertex.add(self=self, attributes=attributes)

        for p in self.permission:

            if not p.added_to_db():
                p.add()

            e = RelationGroupAllowedPermission(
                inVertex=p,
                outVertex=self
            )

            e.add()

    def added_to_db(self) -> bool:
        """Return whether this UserGroup is added to the database, that is, whether the ID is not the virtual ID placeholder and perform a query to the database to determine if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or (
                g.V().has('category', UserGroup.category).has(
                    'name', self.name).count().next() == 1
            )
        )

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a UserGroup instance based on the name :param name:, connected to the necessary Permission instances.

        :param name: The name of the UserGroup instance.
        :type name: str
        """

        d = g.V().has('category', UserGroup.category).has('name', name).project('id', 'attrs', 'permission_ids').by(
            __.id()).by(__.valueMap()).by(__.both(RelationGroupAllowedPermission.category).id().fold()).next()

        id, attrs, perimssion_ids = d['id'], d['attrs'], d['permission_ids']

        if id not in _vertex_cache:

            permissions = []

            for p_id in perimssion_ids:
                permissions.append(Permission.from_id(p_id))

            Vertex._cache_vertex(
                UserGroup(
                    name=name,
                    comments=attrs['comments'][0],
                    permission=permissions,
                    id=id
                )
            )

        return _vertex_cache[id]


class User(Vertex):
    """ The representation of a user.

    :ivar uname: Name used by the user to login.
    :ivar pwd_hash: Password is stored after being salted and hashed.
    :ivar institution: Name of the institution of the user. 
    :ivar allowed_group: Optional allowed user group of the user vertex, as a list of UserGroup attributes.
    """

    category: str = "user"

    uname: str
    pwd_hash: str
    institution: str
    allowed_group: List[UserGroup] = None

    def __new__(
        cls, uname: str, pwd_hash: str, institution: str, allowed_group: List[UserGroup] = None, id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        """
        Return a User instance given the desired attributes.

        :param uname: Name used by the user to login.
        :type uname: str

        :param pwd_hash: Password is stored after being salted and hashed.
        :type pwd_hash: str

        :param institution: Name of the institution of the user.
        :type institution: str

        :param allowed_group: The UserGroup instance representing the groups the user is in.
        :type user_group: List[UserGroup]

        :param id: The serverside ID of the User, defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int,optional 
        """
        if id is not VIRTUAL_ID_PLACEHOLDER and id in _vertex_cache:
            return _vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(
            self, uname: str, pwd_hash: str, institution: str, allowed_group: List[UserGroup] = None, id: int = VIRTUAL_ID_PLACEHOLDER):
        """
        Initialize a User instance given the desired attributes.

        :param uname: Name used by the user to login.
        :type uname: str

        :param pwd_hash: Password is stored after being salted and hashed.
        :type pwd_hash: str

        :param institution: Name of the institution of the user.
        :type institution: str

        :param allowed_group: The UserGroup instance representing the groups the user is in.
        :type user_group: List[UserGroup]

        :param id: The serverside ID of the User, defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int,optional 
        """

        self.uname = uname
        self.pwd_hash = pwd_hash
        self.institution = institution
        self.allowed_group = allowed_group

        Vertex.__init__(self, id=id)

    def add(self):
        """Add this user to the serverside.
        """

        # If already added, raise an error!
        if self.added_to_db():
            raise VertexAlreadyAddedError(
                f"User with username {self.uname}" +
                "already exists in the database."
            )

        attributes = {
            'uname': self.uname,
            'pwd_hash': self.pwd_hash,
            'institution': self.institution
        }

        Vertex.add(self, attributes)

        if self.allowed_group is not None:

            for gtype in self.allowed_group:

                if not gtype.added_to_db():
                    gtype.add()

                e = RelationUserAllowedGroup(
                    inVertex=gtype,
                    outVertex=self
                )

                e.add()

    def added_to_db(self) -> bool:
        """Return whether this User is added to the database, that is, whether the ID is not the virtual ID placeholder and perform a query to the database if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or (
                g.V().has('category', User.category).has(
                    'uname', self.uname).count().next() > 0
            )
        )

    @classmethod
    def _attrs_to_user(
            cls, uname: str, pwd_hash: str, institution: str, allowed_group: List[UserGroup] = None, id: int = VIRTUAL_ID_PLACEHOLDER):
        """Given the id and attributes of a User, see if one exists in the cache. If so, return the cached User. Otherwise, create a new one, cache it, and return it.

        :param uname: Name used by the user to login.
        :type uname: str

        :param pwd_hash: Password is stored after being salted and hashed.
        :type pwd_hash: str

        :param institution: Name of the institution of the user.
        :type institution: str

        :param allowed_group: The UserGroup instance representing the groups the user is in.
        :type user_group: List[UserGroup]

        :param id: The serverside ID of the User, defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int,optional 
        """

        if id not in _vertex_cache:
            Vertex._cache_vertex(
                User(
                    uname=uname,
                    pwd_hash=pwd_hash,
                    institution=institution,
                    allowed_group=allowed_group,
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def from_db(cls, uname: str):
        """Query the database and return a User instance based on uname

        :param uname: Name used by the user to login.
        :type uname: str 
        """

        d = g.V().has('category', User.category).has('uname', uname).project('id', 'attrs', 'group_ids').by(
            __.id()).by(__.valueMap()).by(__.both(RelationUserAllowedGroup.category).id().fold()).next()

        # to access attributes from attrs, do attrs[...][0]
        id, attrs, gtype_ids = d['id'], d['attrs'], d['group_ids']

        if id not in _vertex_cache:

            gtypes = []

            for gtype_id in gtype_ids:
                gtypes.append(UserGroup.from_id(gtype_id))

            Vertex._cache_vertex(
                User(
                    uname=uname,
                    pwd_hash=attrs['pwd_hash'][0],
                    institution=attrs['institution'][0],
                    allowed_group=gtypes,
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def from_id(cls, id: int):
        """Query the database and return a User instance based on the ID.

        :param id: The serverside ID of the User instance vertex.
        type id: int
        :return: Return a User from that ID.
        rtype: User
        """

        if id not in _vertex_cache:

            d = g.V(id).project('attrs', 'group_ids').by(__.valueMap()).by(
                __.both(RelationUserAllowedGroup.category).id().fold()).next()

            # to access attributes from attrs, do attrs[...][0]

            attrs, gtype_ids = d['attrs'], d['group_ids']

            gtypes = []

            for gtype_id in gtype_ids:
                gtypes.append(UserGroup.from_id(gtype_id))

            Vertex._cache_vertex(
                User(
                    uname=attrs['uname'][0],
                    pwd_hash=attrs['pwd_hash'][0],
                    institution=attrs['institution'][0],
                    allowed_group=gtypes,
                    id=id
                )
            )

        return _vertex_cache[id]


###############################################################################
#                                   EDGES                                     #
###############################################################################


class RelationConnection(Edge):
    """Representation of a "rel_connection" edge.

    :ivar start_time: The start time of the connection.
    :ivar end_time: The end time of the connection. 
    :ivar start_uid: The ID of the user that started the connection.
    :ivar end_uid: The ID of the user that ended the connection.
    :ivar start_edit_time: The time that the connection was started at.
    :ivar end_edit_time: The time that the connection was ended at.
    :ivar start_comments: Comments about starting the connection.
    :ivar end_comments: Comments about ending the connection.
    :ivar permanent: Whether the connection is permanent.

    # TODO: Make permanent edges a separate edge category.
    # User ID can be an integer, not a string.
    """

    category: str = "rel_connection"

    start_time: float
    end_time: float
    start_uid: str
    end_uid: str
    start_edit_time: float
    end_edit_time: float
    start_comments: str
    end_comments: str

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex, start_time: float,
        start_uid: str, start_edit_time: float, start_comments: str = "",
        end_time: float = EXISTING_RELATION_END_PLACEHOLDER, end_uid: str = "",
        end_edit_time: float = EXISTING_RELATION_END_EDIT_PLACEHOLDER,
        end_comments: str = "",
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        """Initialize the connection.

        :param inVertex: The Vertex that the edge is going into.
        :type inVertex: Vertex
        :param outVertex: The Vertex that the edge is going out of.
        :type outVertex: Vertex
        :param start_time: The (physical) start time of the connection.
        :type start_time: float
        :param start_uid: The ID of the user that started the connection.
        :type start_uid: str
        :param start_edit_time: When the connection start event was entered.
        :type start_edit_time: float
        :param start_comments: Comments regarding the starting of 
        the connection, defaults to ""
        :type start_comments: str, optional
        :param end_time: The (physical) end time of the connection, 
        defaults to EXISTING_CONNECTION_END_PLACEHOLDER
        :type end_time: float, optional
        :param end_uid: The ID of the user that ended the connection, 
        defaults to ""
        :type end_uid: str, optional
        :param end_edit_time: When the connection end event was entered, 
        defaults to 
        :type end_edit_time: float, optional
        :param end_comments: Comments regarding the ending of 
        the connection, defaults to ""
        :type end_comments: str, optional
        :param permanent: Whether the connection is to be permanent.
        """

        self.start_time = start_time
        self.start_uid = start_uid
        self.start_edit_time = start_edit_time
        self.start_comments = start_comments

        self.end_time = end_time
        self.end_uid = end_uid
        self.end_edit_time = end_edit_time
        self.end_comments = end_comments

        Edge.__init__(self=self, id=id, inVertex=inVertex, outVertex=outVertex)

    def add(self):
        """Add this connection as an edge to the database.
        """

        attributes = {
            "start_time": self.start_time,
            "start_uid": self.start_uid,
            "start_edit_time": self.start_edit_time,
            "start_comments": self.start_comments,
            "end_time": self.end_time,
            "end_uid": self.end_uid,
            "end_edit_time": self.end_edit_time,
            "end_comments": self.end_comments
        }

        Edge.add(self, attributes=attributes)

    def _end_connection(
        self, end_time: float,
        end_uid: str, end_edit_time: float, end_comments: str = ""
    ):
        """End the connection if the connection is not permanent.

        :param end_time: The (physical) end time of the connection. 
        :type end_time: float
        :param end_uid: The ID of the user that ended the connection.
        :type end_uid: str
        :param end_edit_time: When the connection ending was entered. 
        :type end_edit_time: float
        :param end_comments: Comments regarding the ending of the connection,
        defaults to ""
        :type end_comments: str, optional
        """

        if not self.added_to_db():

            # Edge not added to DB!
            raise EdgeNotAddedError(
                f"Connection between {self.inVertex} and {self.outVertex} " +
                "does not exist in the database."
            )

        self.end_time = end_time
        self.end_uid = end_uid
        self.end_edit_time = end_edit_time
        self.end_comments = end_comments

        g.E(self.id()).property('end_time', end_time) \
            .property('end_uid', end_uid) \
            .property('end_edit_time', end_edit_time) \
            .property('end_comments', end_comments).iterate()


class RelationProperty(Edge):
    """Representation of a "rel_property" edge.

    :ivar start_time: The start time of the relation.
    :ivar end_time: The end time of the relation. 
    :ivar start_uid: The ID of the user that started the relation.
    :ivar end_uid: The ID of the user that ended the relation.
    :ivar start_edit_time: The time that the relation was started at.
    :ivar end_edit_time: The time that the relation was ended at.
    :ivar start_comments: Comments about starting the relation.
    :ivar end_comments: Comments about ending the relation.
    """

    category: str = "rel_property"

    start_time: float
    end_time: float
    start_uid: str
    end_uid: str
    start_edit_time: float
    end_edit_time: float
    start_comments: str
    end_comments: str

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex, start_time: float,
        start_uid: str, start_edit_time: float, start_comments: str = "",
        end_time: float = EXISTING_RELATION_END_PLACEHOLDER, end_uid: str = "",
        end_edit_time: float = -1, end_comments: str = "",
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        """Initialize the relation.

        :param inVertex: The Vertex that the edge is going into.
        :type inVertex: Vertex

        :param outVertex: The Vertex that the edge is going out of.
        :type outVertex: Vertex

        :param start_time: The (physical) start time of the relation.
        :type start_time: float

        :param start_uid: The ID of the user that started the relation.
        :type start_uid: str

        :param start_edit_time: When the relation start event was entered.
        :type start_edit_time: float

        :param start_comments: Comments regarding the starting of 
        the relation, defaults to ""
        :type start_comments: str, optional

        :param end_time: The (physical) end time of the relation, 
        defaults to EXISTING_RELATION_END_PLACEHOLDER
        :type end_time: float, optional

        :param end_uid: The ID of the user that ended the relation, 
        defaults to ""
        :type end_uid: str, optional

        :param end_edit_time: When the relation end event was entered, 
        defaults to EXISTING_RELATION_END_EDIT_PLACEHOLDER
        :type end_edit_time: float, optional

        :param end_comments: Comments regarding the ending of 
        the relation, defaults to ""
        :type end_comments: str, optional
        """

        self.start_time = start_time
        self.start_uid = start_uid
        self.start_edit_time = start_edit_time
        self.start_comments = start_comments
        self.end_time = end_time
        self.end_uid = end_uid
        self.end_edit_time = end_edit_time
        self.end_comments = end_comments

        Edge.__init__(self=self, id=id, inVertex=inVertex,
                      outVertex=outVertex)

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={
            "start_time": self.start_time,
            "start_uid": self.start_uid,
            "start_edit_time": self.start_edit_time,
            "start_comments": self.start_comments,
            "end_time": self.end_time,
            "end_uid": self.end_uid,
            "end_edit_time": self.end_edit_time,
            "end_comments": self.end_comments
        })

    def end_relation(
        self, end_time: float,
        end_uid: str, end_edit_time: float, end_comments: str = ""
    ):
        """End the relation.

        :param end_time: The (physical) end time of the relation. 
        :type end_time: float
        :param end_uid: The ID of the user that ended the relation.
        :type end_uid: str
        :param end_edit_time: When the relation ending was entered. 
        :type end_edit_time: float
        :param end_comments: Comments regarding the ending of the relation,
        defaults to ""
        :type end_comments: str, optional
        """
        self.end_time = end_time
        self.end_uid = end_uid
        self.end_edit_time = end_edit_time
        self.end_comments = end_comments


class RelationVersion(Edge):
    """
    Representation of a "rel_version" edge.
    """

    category: str = "rel_version"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(self=self, id=id,
                      inVertex=inVertex, outVertex=outVertex)

    def _add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationVersionAllowedType(Edge):
    """
    Representation of a "rel_version_allowed_type" edge.
    """

    category: str = "rel_version_allowed_type"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(self=self, id=id,
                      inVertex=inVertex, outVertex=outVertex,
                      )

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationComponentType(Edge):
    """
    Representation of a "rel_component_type" edge.
    """

    category: str = "rel_component_type"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(self=self, id=id,
                      inVertex=inVertex, outVertex=outVertex)

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationSubcomponent(Edge):
    """
    Representation of a "rel_subcomponent" edge.
    """

    category: str = "rel_subcomponent"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(self=self, id=id,
                      inVertex=inVertex, outVertex=outVertex)

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationPropertyType(Edge):
    """
    Representation of a "rel_property_type" edge.
    """

    category: str = "rel_property_type"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationPropertyAllowedType(Edge):
    """
    Representation of a "rel_property_allowed_type" edge.
    """

    category: str = "rel_property_allowed_type"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationFlagComponent(Edge):
    """
    Representation of a "rel_flag_component" edge.
    """

    category: str = "rel_flag_component"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside."""

        Edge.add(self, attributes={})


class RelationFlagType(Edge):
    """
    Representation of a "rel_flag_type" edge.
    """

    category: str = "rel_flag_type"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside."""

        Edge.add(self, attributes={})


class RelationFlagSeverity(Edge):
    """
    Representation of a "rel_flag_severity" edge.
    """

    category: str = "rel_flag_severity"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside."""

        Edge.add(self, attributes={})


class RelationUserAllowedGroup(Edge):
    """
    Representation of a "rel_user_group" edge.
    """

    category: str = "rel_user_group"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationGroupAllowedPermission(Edge):
    """
    Representation of a "rel_group_permission" edge.
    """

    category: str = "rel_group_permission"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})
