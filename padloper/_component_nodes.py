"""
_component_nodes.py

Classes for manipulating components, component types and component versions.
"""
import time
import _global as g
from gremlin_python.process.traversal import Order, P, TextP
from gremlin_python.process.graph_traversal import __, constant

from _exceptions import *
from _base import strictraise, Edge, Timestamp, Vertex, _parse_time
from _edges import RelationVersionAllowedType, RelationVersion,\
                   RelationComponentType, RelationSubcomponent,\
                   RelationProperty, RelationPropertyType,\
                   RelationFlagComponent, RelationConnection
from _permissions import Permission, check_permission
from padloper.method_decorators import authenticated

#import re
#from unicodedata import name
#import warnings
#from xmlrpc.client import boolean
#from attr import attr, attributes
#from sympy import true
#from typing import Optional, List

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
        cls, name: str, comments: str = "", id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        """
        Return a ComponentType instance given the desired attributes.

        :param name: The name of the component type. 
        :type name: str

        :param comments: The comments attached to the component type, 
        defaults to ""
        :type comments: str  

        :param id: The serverside ID of the ComponentType, 
        defaults to _VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id is not g._VIRTUAL_ID_PLACEHOLDER and id in g._vertex_cache:
            return g._vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(
        self, name: str, comments: str = "", id: int = g._VIRTUAL_ID_PLACEHOLDER
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

    def as_dict(self, permissions = None):
        """Return a dictionary representation."""
        return {"name": self.name, "comments": self.comments}

    @authenticated
    def add(self, strict_add=False, permissions = None):
        """Add this ComponentType vertex to the serverside.
        """

        # If already added.
        if self.added_to_db(permissions=permissions):
            strictraise(strict_add, VertexAlreadyAddedError,
                        f"ComponentType with name {self.name} " +
                         "already exists in the database.")
            return self.from_db(self.name)

        attributes = {
            'name': self.name,
            'comments': self.comments
        }

        Vertex.add(self=self, attributes=attributes, permissions=permissions)
#        print(f"Added {self}")
        return self

    @authenticated
    def replace(self, newVertex, disable_time: int = int(time.time()), permissions = None):
        """Replaces the ComponentType vertex in the serverside.

        :param newVertex: The new ComponentType vertex that is replacing the old
            ComponentType vertex.
        :type newVertex: ComponentType

        :param disable_time: When this vertex was disabled in the database (UNIX
            time).
        :type disable_time: int
        """

        # Step 1: Sets the property active from true to false and registers the
        # time when the vertex was disabled.
        g.t.V(self.id()).property(
            'active', False).property('time_disabled', disable_time).iterate()

        # Step 2: Adds the new vertex in the serverside.
        newVertex.add(strict_add=True)

        # Step 3
        newVertexId = newVertex.id()

        # Replaces the ComponentType vertex with the new ComponentType vertex.
        Vertex.replace(self=self, id=newVertexId)

    # @authenticated
    def added_to_db(self, permissions = None) -> bool:
        """Return whether this ComponentType is added to the database,
        that is, whether the ID is not the virtual ID placeholder and perform 
        a query to the database to determine if the 
        vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != g._VIRTUAL_ID_PLACEHOLDER or (
                g.t.V().has('category', ComponentType.category)\
                   .has('name', self.name)\
                   .has('active', True).count().next() > 0
            )
        )

    @classmethod
    def from_db(cls, name: str, permissions = None):
        """Query the database and return a ComponentType instance based on
        component type of name :param name:.

        :param name: The name of the component type.
        :type name: str
        :return: A ComponentType instance with the correct name, comments, and 
        ID.
        :rtype: ComponentType
        """

        try:
            d = g.t.V().has('active', True) \
                   .has('category', ComponentType.category) \
                   .has('name', name).as_('v').valueMap().as_('props') \
                   .select('v').id_().as_('id').select('props', 'id').next()
        except:
            raise ComponentTypeNotAddedError

        props, id_ = d['props'], d['id']

        Vertex._cache_vertex(
            ComponentType(
                name=name,
                comments=props['comments'][0],
                id=id_
            )
        )

        return g._vertex_cache[id_]

    @classmethod
    def from_id(cls, id: int, permissions = None):
        """Query the database and return a ComponentType instance based on
        the ID.

        :param id: The serverside ID of the ComponentType vertex.
        :type id: int
        :return: Return a ComponentType from that ID.
        :rtype: ComponentType
        """

        if id not in g._vertex_cache:

            d = g.t.V(id).valueMap().next()

            Vertex._cache_vertex(
                ComponentType(
                    name=d['name'][0],
                    comments=d['comments'][0],
                    id=id
                )
            )

        return g._vertex_cache[id]

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

        if id not in g._vertex_cache:
            Vertex._cache_vertex(
                ComponentType(
                    name=name,
                    comments=comments,
                    id=id
                )
            )

        return g._vertex_cache[id]

    @classmethod
    def get_names_of_types_and_versions(cls, permissions = None):
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

        ts = g.t.V().has('active', True)\
                .has('category', ComponentType.category) \
                .order().by('name', Order.asc) \
                .project('name', 'versions') \
                .by(__.values('name')) \
                .by(__.both(RelationVersionAllowedType.category)
                  .order().by('name', Order.asc).values('name').fold()
                ).toList()

        return ts

    @classmethod
    def get_list(
        cls,
        range: tuple,
        order_by: str,
        order_direction: str,
        name_substring: str,
        permissions = None
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

        traversal = g.t.V()\
                       .has('active', True)\
                       .has('category', ComponentType.category) \
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
            .by(__.id_()) \
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
    def get_count(cls, name_substring: str, permissions = None):
        """Return the count of ComponentTypes given a substring of the name
        property.

        :param name_substring: A substring of the name property of the
        ComponentType
        :type name_substring: str

        :return: The number of ComponentTypes that contain 
        :param name_substring: as a substring in the name property.
        :rtype: int
        """

        return g.t.V().has('active', True)\
                      .has('category', ComponentType.category) \
                      .has('name', TextP.containing(name_substring)) \
                      .count().next()

    def __repr__(self):
        return f"{self.category}: {self.name} ({self._id})"


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
        id: int = g._VIRTUAL_ID_PLACEHOLDER
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
        defaults to _VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id is not g._VIRTUAL_ID_PLACEHOLDER and id in g._vertex_cache:
            return g._vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(
        self, name: str, allowed_type: ComponentType, comments: str = "",
        id: int = g._VIRTUAL_ID_PLACEHOLDER
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

    def as_dict(self, permissions = None):
        """Return a dictionary representation."""
        return {"name": self.name, "comments": self.comments,
                "allowed_type": self.allowed_type.as_dict()}

    @authenticated
    def add(self, strict_add=False, permissions = None):
        """Add this ComponentVersion vertex to the serverside.
        """

        # If already added.
        if self.added_to_db(permissions=permissions):
            strictraise(strict_add, VertexAlreadyAddedError, 
                f"ComponentVersion with name {self.name} " +
                f"and allowed type {self.allowed_type.name} " +
                "already exists in the database."
            )
            return self.from_db(self.name, self.allowed_type)

        attributes = {
            'name': self.name,
            'comments': self.comments
        }

        Vertex.add(self=self, attributes=attributes)

        if not self.allowed_type.added_to_db(permissions=permissions):
            self.allowed_type.add(permissions=permissions)

        e = RelationVersionAllowedType(
            inVertex=self.allowed_type,
            outVertex=self
        )

        e.add()
#        print(f"Added {self}")
        return self

    @authenticated
    def replace(self, newVertex, disable_time: int = int(time.time()), permissions = None):
        """Replaces the ComponentVersion vertex in the serverside.

        :param newVertex: The new ComponentVersion vertex that is replacing the
            old ComponentVersion vertex.
        :type newVertex: ComponentVersion

        :param disable_time: When this vertex was disabled in the database (UNIX
            time).
        :type disable_time: int
        """

        # Step 1
        g.t.V(self.id()).property('active', False)\
           .property('time_disabled', disable_time).iterate()

        # Step 2
        newVertex.add(strict_add=True)

        # Step 3
        newVertexId = newVertex.id()

        Vertex.replace(self=self, id=newVertexId)

    # @authenticated
    def added_to_db(self, permissions = None) -> bool:
        """Return whether this ComponentVersion is added to the database,
        that is, whether the ID is not the virtual ID placeholder and perform 
        a query to the database to determine if the vertex 
        has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != g._VIRTUAL_ID_PLACEHOLDER or (
                self.allowed_type.added_to_db(permissions=permissions) and
                g.t.V(self.allowed_type.id())\
                   .both(RelationVersionAllowedType.category)
                   .has('name', self.name)\
                   .has('active', True).count().next() > 0
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

        if id not in g._vertex_cache:
            Vertex._cache_vertex(
                ComponentVersion(
                    name=name,
                    comments=comments,
                    allowed_type=allowed_type,
                    id=id
                )
            )

        return g._vertex_cache[id]

    @classmethod
    def from_db(cls, name: str, allowed_type: ComponentType, permissions=None):
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

        if allowed_type.added_to_db(permissions=permissions):

            try:
                d = g.t.V(allowed_type.id()).has('active', True) \
                       .both(RelationVersionAllowedType.category) \
                       .has('name', name).as_('v').valueMap().as_('attrs') \
                       .select('v').id_().as_('id').select('attrs', 'id').next()
            except StopIteration:
                raise ComponentVersionNotAddedError

            props, id = d['attrs'], d['id']

            Vertex._cache_vertex(
                ComponentVersion(
                    name=name,
                    comments=props['comments'][0],
                    allowed_type=allowed_type,
                    id=id
                )
            )

            return g._vertex_cache[id]

        else:
            raise ComponentTypeNotAddedError(
                f"Allowed type {allowed_type.name} of " +
                f"proposed component version {name} has not yet been added " +
                "to the database."
            )

    
    @classmethod
    def from_id(cls, id: int, permissions = None):
        """Query the database and return a ComponentVersion instance based on
        the ID.

        :param id: The serverside ID of the ComponentVersion vertex.
        :type id: int
        :return: Return a ComponentVersion from that ID.
        :rtype: ComponentVersion
        """

        if id not in g._vertex_cache:

            d = g.t.V(id).project('attrs', 'type_id').by(__.valueMap()) \
                   .by(__.both(RelationVersionAllowedType.category).id_())\
                   .next()

            t = ComponentType.from_id(d['type_id'])

            Vertex._cache_vertex(
                ComponentVersion(
                    name=d['attrs']['name'][0],
                    comments=d['attrs']['comments'][0],
                    allowed_type=t,
                    id=id
                )
            )

        return g._vertex_cache[id]

    @classmethod
    def get_list(
        cls,
        range: tuple,
        order_by: str,
        order_direction: str,
        filters: list,
        permissions = None
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

        traversal = g.t.V().has('active', True)\
                       .has('category', ComponentVersion.category)

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
            .by(__.id_()) \
            .by(__.values('name')) \
            .by(__.values('comments')) \
            .by(__.both(RelationVersionAllowedType.category).id_()) \
            .toList()

        component_versions = []

        for entry in cts:
            id, name, comments, type_id = entry['id'], entry['name'], \
                entry['comments'], entry['type_id']

            t = ComponentType.from_id(id=type_id, permissions=permissions)

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
    def get_count(cls, filters: list, permissions = None):
        """Return the count of ComponentVersions given a list of filters

        :param filters: A list of 2-tuples of the format (name, ctype)
        :type order_by: list

        :return: The number of ComponentVersions that agree with
        :param filters:.
        :rtype: int
        """

        traversal = g.t.V().has('active', True)\
                       .has('category', ComponentVersion.category)

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

    def __repr__(self):
        return f"{self.category}: {self.name}"


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
        id: int = g._VIRTUAL_ID_PLACEHOLDER,
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
        defaults to _VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id is not g._VIRTUAL_ID_PLACEHOLDER and id in g._vertex_cache:
            return g._vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(
        self, name: str, type: ComponentType,
        version: ComponentVersion = None,
        id: int = g._VIRTUAL_ID_PLACEHOLDER,
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

    @authenticated
    def add(self, strict_add=False, permissions = None):
        """Add this Component to the serverside.
        """

#        CONTINUE HERE: figure out how to check if a vertex already exists!!
#        print(">>>>> ", self.name)
        if self.added_to_db(permissions=permissions):
            strictraise(strict_add, VertexAlreadyAddedError, 
                f"Component with name {self.name} " +
                "already exists in the database."
            )
            return self.from_db(self.name)


        attributes = {
            'name': self.name
        }

        Vertex.add(self, attributes)

        if self.version is not None:
            if not self.version.added_to_db(permissions=permissions):
                self.version.add(permissions=permissions)

            rev_edge = RelationVersion(
                inVertex=self.version,
                outVertex=self
            )

            rev_edge._add()

        if not self.type.added_to_db(permissions=permissions):
            self.type.add(permissions=permissions)

        type_edge = RelationComponentType(
            inVertex=self.type,
            outVertex=self
        )

        type_edge.add()

#        print(f"Added {self}")
        return self

    @authenticated
    def replace(self, newVertex, disable_time: int = int(time.time()), permissions = None):
        """Replaces the Component vertex in the serverside.

        :param newVertex: The new Component vertex that is replacing the old
            Component vertex.
        :type newVertex: Component

        :param disable_time: When this vertex was disabled in the database (UNIX
            time).
        :type disable_time: int
        """

        # Step 1
        g.t.V(self.id()).property('active', False)\
           .property('time_disabled', disable_time).iterate()

        # Step 2
        newVertex.add(strict_add=True)

        # Step 3
        newVertexId = newVertex.id()

        Vertex.replace(self=self, id=newVertexId)

    # @authenticated
    def get_property(self, type, at_time: int, permissions = None):
        """
        Given a property type, get a property of this component active at time
        :param time:. 

        :param type: The type of the property to extract
        :type type: PropertyType
        :param at_time: The time to check the active property at.
        :type at_time: int

        :rtype: Property or None
        """
        from _property_nodes import Property

        if not self.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not type.added_to_db(permissions=permissions):
            raise PropertyTypeNotAddedError(
                f"Property type {type.name} of component " +
                 "{self.name} " +
                "has not yet been added to the database."
            )

        # list of property vertices of this property type
        # and active at this time
        vs = g.t.V(self.id()).bothE(RelationProperty.category) \
                .has('active', True) \
                .has('start_time', P.lte(at_time)) \
                .has('end_time', P.gt(at_time)).otherV().as_('v') \
                .both(RelationPropertyType.category) \
                .has('name', type.name) \
                .select('v').toList()

        # If no such vertices found
        if len(vs) == 0:
            return None

        # There should be only one!

        assert len(vs) == 1

        return Property.from_id(vs[0].id)

    @authenticated
    def get_all_properties(self, permissions = None):
        """Return all properties, along with their edges of this component as
        a tuple of the form (Property, RelationProperty)

        :rtype: tuple[Property, RelationProperty]
        """
        from _property_nodes import Property

        if not self.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # list of property vertices of this property type
        # and active at this time
        query = g.t.V(self.id()).bothE(RelationProperty.category)\
                   .has('active', True) \
                   .as_('e').valueMap().as_('edge_props') \
                   .select('e').otherV().id_().as_('vertex_id') \
                   .select('edge_props', 'vertex_id').toList()

        # Build up the result of format (property vertex, relation)
        result = []

        for q in query:
            prop = Property.from_id(q['vertex_id'])
            edge = RelationProperty(
                inVertex=prop,
                outVertex=self,
                start=Timestamp._from_dict(q["edge_props"], "start_"),
                end=Timestamp._from_dict(q["edge_props"], "end_"),
            )
            result.append((prop, edge))

        return result

    @authenticated
    def get_all_properties_of_type(
        self, type,
        from_time: int = -1,
        to_time: int = g._TIMESTAMP_NO_ENDTIME_VALUE,
        permissions = None
    ):
        """
        Given a property type, return all edges that connected them between time
        :param from_time: and to time :param to_time: as a list.

        :param type: The property type of the desired properties to consider.
        :type component: PropertyType
        :param from_time: Lower bound for time range to consider properties, 
        defaults to -1
        :type from_time: int, optional
        :param to_time: Upper bound for time range to consider properties, 
        defaults to _TIMESTAMP_NO_ENDTIME_VALUE
        :type to_time: int, optional

        :rtype: list[RelationProperty]
        """

        if not self.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not type.added_to_db():
            raise PropertyTypeNotAddedError(
                f"Property type {type.name} of component {self.name} " +
                "has not yet been added to the database."
            )

        edges = g.t.V(self.id()).bothE(RelationProperty.category) \
                   .has('active', True) \
                   .has('end_edit_time', g._TIMESTAMP_NO_EDITTIME_VALUE)

        if to_time < g._TIMESTAMP_NO_ENDTIME_VALUE:
            edges = edges.has('start_time', P.lt(to_time))

        edges = edges.has('end_time', P.gt(from_time)) \
            .as_('e').otherV().as_('v') \
            .both(RelationPropertyType.category) \
            .has('name', type.name) \
            .select('e').order().by(__.values('start_time'), Order.asc) \
            .project('properties', 'id').by(__.valueMap()).by(__.id_()).toList()

        print("Warning: RelationProperty not initialised properly! "\
              "outVertex should not = type but the property vertex …")
        return [RelationProperty(
            inVertex=self, outVertex=type,
            start=Timestamp._from_dict(q["properties"], "start_"),
            end=Timestamp._from_dict(q["properties"], "end_"),
            id=e['id']['@value']['relationId']  # weird but you have to
        ) for e in edges]

    @authenticated
    def get_all_flags(self, permissions = None):
        """Return all flags connected to this component of the form (Flag)

        :rtype: [Flag]
        """

        if not self.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # list of flag vertices of this flag type and flag severity and active at this time.

        query = g.t.V(self.id()).bothE(RelationFlagComponent.category)\
                   .has('active', True).otherV().id_().toList()

        # Build up the result of format (flag vertex)
        result = []

        for q in query:
            flag = Flag.from_id(q)
            result.append((flag))

        return result

    @authenticated
    def get_subcomponents(self, permissions = None):
        """Return all subcomponents connected to this component.

        :rtype: [Component]
        """

        if not self.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        query = g.t.V(self.id()).inE(RelationSubcomponent.category) \
                   .has('active', True).otherV().id_()

        return [Component.from_id(q, permissions=permissions) for q in query.toList()]

    @authenticated
    def get_supercomponents(self, permissions = None):
        """Return all supercomponents connected to this component of the form
        (Component)

        :rtype: [Component]
        """

        if not self.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # Relation as a subcomponent stays the same except now
        # we have outE to distinguish from subcomponents
        query = g.t.V(self.id()).outE(RelationSubcomponent.category) \
                   .has('active', True).otherV().id_()

        return [Component.from_id(q, permissions=permissions) for q in query.toList()]

    @authenticated
    def set_property(
        self, property, start: Timestamp, end: Timestamp = None, 
        force_property: bool = False,
        strict_add: bool = False,
        permissions = None,
    ):
        """
        Given a property :param property:, MAKE A _VIRTUAL COPY of it,
        add it, then connect it to the component self at start time
        :start_time:. Return the Property instance that was added.

        """
        # print('perms: ', permissions)
        from _property_nodes import Property
        # # TODO: check permissions here
        # # test
        # perms = Permission(['set_property', 'edit_component', 'add_component'], "j")
        # permission_group_pass = ['set_property', 'edit_component']
        # permission_group_fail = ['set_property', 'edit_component', 'admin']
        # if not check_permission(perms, permission_group_fail):
        #     raise NoPermissionsError(
        #         "User does not have the required permissions to perform this action."
        #         )
        # print(kwargs['method_name'])
        # print(self.__class__.__name__)

        if not self.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if (self.type not in property.type.allowed_types):
            raise PropertyWrongType(
                f"Property type {property.type.name} is not applicable to "\
                f"component type {self.type.name}."
            )

        current_property = self.get_property(
            type=property.type, at_time=start.time,
            permissions=permissions
        )

        if current_property is not None:
#    CONTINUE HERE: probably ready for a pull request.
#    CONTINUE HERE 2: see if behaviour is correct (when this trips in
#            init_simple-db.py).
            if current_property.values == property.values:
                strictraise(strict_add, PropertyIsSameError, 
                    "An identical property of type " +
                    f"{property.type.name} for component {self.name} " +
                    f"is already set with values {property.values}."
                )
                return

#            elif current_property.end.time != g._TIMESTAMP_NO_ENDTIME_VALUE:
#                raise PropertyIsSameError(
#                    "Property of type {property.type.name} for component "\
#                    "{self.name} is already set at this time with an end "\
#                    "time after this time."
#                )
            else:
                # end that property.
                self.unset_property(current_property, start,
                permissions=permissions)

        else:

            existing_properties = self.get_all_properties_of_type(
                type=property.type,
                from_time=start.time,
                permissions=permissions
            )

            if len(existing_properties) > 0:
                if force_property:
                    if end != None:
                        raise ComponentPropertiesOverlappingError(
                            "Trying to set property of type " +
                            f"{property.type.name} for component " +
                            f"{self.name} " +
                            "before an existing property of the same type " +
                            "but with a specified end time; " +
                            "replace the property instead."
                        )

                    else:
                        end = Timestamp(existing_properties[0].start_time,
                                        start.comments)
                else:
                    raise ComponentSetPropertyBeforeExistingPropertyError(
                        "Trying to set property of type " +
                        f"{property.type.name} for component " +
                        f"{self.name} " +
                        "before an existing property of the same type; " +
                        "set 'force_property' parameter to True to bypass."
                    )

        prop_copy = Property(
            values=property.values,
            type=property.type
        )

        prop_copy._add(permissions=permissions)

        e = RelationProperty(inVertex=prop_copy, outVertex=self, start=start,
                             end=end)
        e.add()

        return prop_copy

    @authenticated
    def unset_property(self, property, end: Timestamp, permissions = None):
        """
        Given a property that is connected to this component,
        set the "end" attributes of the edge connecting the component and
        the property to indicate that this property has been removed from the
        component.

        :param property: The property vertex connected by an edge to the 
        component vertex.
        :type property: Property

        :param at_time: The time at which the property was removed (real time). This value has to be provided.
        :type at_time: int

        :param uid: The user that removed the property
        :type uid: str

        :param edit_time: The time at which the 
        user made the change, defaults to int(time.time())
        :type edit_time: int, optional

        :param comments: Comments about the property removal, defaults to ""
        :type comments: str, optional
        """

        if not self.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not property.added_to_db(permissions=permissions):
            raise PropertyNotAddedError(
                f"Property of component {self.name} " +
                f"of values {property.values} being unset " +
                "has not been added to the database."
            )

        # Check to see if the property already has an end time.
        vs = g.t.V(self.id()).bothE(RelationProperty.category) \
                .has('active', True) \
                .has('start_time', P.lte(end.time)) \
                .has('end_time', P.gt(end.time)) \
                .as_('e').valueMap().as_('edge_props').select('e') \
                .otherV().as_('v').both(RelationPropertyType.category) \
                .has('name', property.type.name) \
                .select('edge_props').toList()
        if len(vs) == 0:
            raise PropertyNotAddedError(
                "Property of type {property.type.name} cannot be unset for "\
                "component {this.name} because it has not been set yet."
            )
        assert(len(vs) == 1)
#        print(vs[0])
        if vs[0]['end_time'] < g._TIMESTAMP_NO_ENDTIME_VALUE:
            raise PropertyIsSameError(
                f"Property of type {property.type.name} cannot be unset for "\
                f"component {self.name} because it is set at this time and "\
                f"already has an end time."
            )
#        print("slkdjflskdjfslkdjfslkdfjslkdjf")

        g.t.V(property.id()).bothE(RelationProperty.category).as_('e')\
           .otherV() \
           .hasId(self.id()).select('e') \
           .has('end_time', g._TIMESTAMP_NO_ENDTIME_VALUE) \
           .property('end_time', end.time).property('end_uid', end.uid) \
           .property('end_edit_time', end.edit_time) \
           .property('end_comments', end.comments).iterate()

    @authenticated
    def replace_property(self, propertyTypeName: str, property, at_time: int,
                         uid: str, start: Timestamp, comments="", permissions = None):
        """Replaces the Component property vertex in the serverside.

        :param propertyTypeName: The name of the property type being replaced.
        :type propertyTypeName: str

        :param property: The new property that is replacing the old property.
        :type property: Property

        :param at_time: The time at which the property was added (real time)
        :type at_time: int

        :param uid: The ID of the user that added the property
        :type uid: str

        :param comments: Comments to add with property change, defaults to ""
        :type comments: str, optional

        :param disable_time: When this vertex was disabled in the database
          (UNIX time).
        :type disable_time: int
        """
        from _property_nodes import Property

        # id of the property being replaced.
        print("This method needs to be updated to use the Timestamp class.")
        id = g.t.V(self.id()).bothE(RelationProperty.category)\
                .has('active', True)\
                .has('end_edit_time', g._TIMESTAMP_NO_EDITTIME_VALUE)\
                .otherV().where(\
                  __.outE().otherV().properties('name').value()\
                  .is_(propertyTypeName)\
                ).id_().next()

        property_vertex = Property.from_id(id)

        property_vertex.disable()

        # Sets a new property
        self.set_property(
            property=property,
            start=start,
            permissions=permissions
        )

    @authenticated
    def disable_property(self, propertyTypeName,
                         disable_time: int = int(time.time()),                         
                         permissions = None):
        """Disables the property in the serverside

        :param propertyTypeName: The name of the property type being replaced.
        :type propertyTypeName: str

        :param disable_time: When this vertex was disabled in the database
            (UNIX time).
        :type disable_time: int

        """

        g.t.V(self.id()).bothE(RelationProperty.category)\
           .has('active', True)\
           .has('end_edit_time', g._TIMESTAMP_NO_EDITTIME_VALUE)\
           .where(__.otherV().bothE(RelationPropertyType.category).otherV()\
           .properties('name').value().is_(propertyTypeName))\
           .property('active', False).property('time_disabled', disable_time)\
           .next()

    @authenticated
    def connect(
        self, component, start: Timestamp, end: Timestamp = None,
        strict_add: bool = True, is_replacement: bool = False,
        permissions = None
    ):
        """Given another Component :param component:,
        connect the two components.

        :param component: Another component to connect this component to.
        :type component: Component
        :param start: The starting timestamp for the connection.
        :type start: Timestamp
        :param end: The ending timestamp for the connection; if omitted, the
           connection is into the indefinite future.
        :type end: Timestamp or None
        :param strict_add: If connexion already exists, raise an error if True;
          otherwise print a warning and return.
        :type strict_add: bool
        :param is_replacement: Disable current connexion and replace it with
           this one.
        :type is_replacement: bool
        """

        if is_replacement:
            raise RuntimeError(f"Is_replacement feature not implemented yet. {is_replacement}")

        if not self.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not component.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {component.name} has not yet " +
                "been added to the database."
            )

        if self.name == component.name:
            raise ComponentConnectToSelfError(
                f"Trying to connect component {self.name} to itself."
            )

        curr_conn = self.get_connections(component=component,
                                         at_time=start.time,
                                         permissions=permissions)
        # If this doesn't pass, something is very broken!
        assert(len(curr_conn) <= 1)

        if len(curr_conn) == 1 and is_replacement == False:
            # Already connected!
            strictraise(strict_add, ComponentsAlreadyConnectedError, 
                f"Components {self.name} and {component.name} " +
                "are already connected."
            )
            return
        elif len(curr_conn) == 0 and is_replacement == True:
            # Not connected, but expected them to be connected.
            strictraise(strict_add, ComponentsAlreadyConnectedError,
                f"Trying to replace connection between {self.name} and " +
                "{component.name}, but it does not exist."
            )
            return

        all_conn = self.get_connections(component=component,
                                        from_time=start.time,
                                        permissions=permissions)

        if len(all_conn) > 0:
            if end == None:
                raise ComponentsOverlappingConnectionError(
                    "Trying to connect components " +
                    f"{self.name} and {component.name} " +
                    "before an existing connection but without a " +
                    "specified end time. Specify an end time or " +
                    "replace the connection instead."
                    )
            elif end.time >= all_conn[0].start.time:
                raise ComponentsOverlappingConnectionError(
                    "Trying to connect components " +
                    f"{self.name} and {component.name} " +
                    "but existing connection between these components " +
                    "overlaps in time."
                )

        if is_replacement:
            raise RuntimeError(f"Is_replacement feature not implemented yet. {is_replacement}")

        curr_conn = RelationConnection(
            inVertex=self,
            outVertex=component,
            start=start,
            end=end
        )

        curr_conn.add()
#        print(f'connected: {self} -> {component}  ({start.uid} {start.time})')

    @authenticated
    def disconnect(self, component, end, permissions = None):
        """Given another Component :param component:, disconnect the two
        components at time :param time:.

        :param component: Another Component to disconnect this component from.
        :type component: Component
        :param end: The starting timestamp for the connection.
        :type end: Timestamp
        """

        # Done for troubleshooting (so you know which component is not added?)
        if not self.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not component.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {component.name} has not yet " +
                "been added to the database."
            )

        curr_conn = self.get_connections(component=component,
                                         at_time = end.time,
                                         permissions=permissions)
        assert(len(curr_conn) <= 1)

        if len(curr_conn) == 0:
            # Not connected yet!
            raise ComponentsAlreadyDisconnectedError(
                f"Components {self.name} and {component.name} " +
                "are already disconnected at this time."
            )

        else:
            curr_conn[0]._end(end)

    @authenticated
    def disable_connection(self, component,
                           disable_time: int = int(time.time()), permissions = None):
        """Disables the connection in the serverside

        :param component: Component that this component has connection with.
        :type component: Component
        :param disable_time: When this edge was disabled in the database.
        :type disable_time: int    
        """
        raise RuntimeError("Deprecated!")

    @authenticated
    def get_connections(self, component = None, at_time = None,
                        from_time = None, to_time = None,
                        exclude_subcomponents: bool = False,
                        permissions = None):
        """
        Get connections to another component, or all other components, at a
        time, at all times or in a time range, depending on the parameters.

        :param component: The other component(s) to check the connections with; 
            if None then find connections with all other components.
        :type component: Component or list of Components, optional
        :param at_time: Time to check connections at. If this parameter is set,
            then :from_time: and :to_time: are ignored.
        :type at_time: int, optional
        :param from_time: Lower bound for time range to consider connections, 
            defaults to -1
        :type from_time: int, optional
        :param to_time: Upper bound for time range to consider connections, 
            defaults to _TIMESTAMP_NO_ENDTIME_VALUE
        :type to_time: int, optional
        :param exclude_subcomponents: If True, then do not return connections
            to subcomponents or supercomponents.
        :type exclude_subcomponents: bool, optional

        :rtype: list[RelationConnection]
        """
        if not self.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )
        if component:
            if not isinstance(component, list):
                component = [component]
            comp_id = [c.id() for c in component]
            for c in component:
                if not c.added_to_db(permissions=permissions):
                    raise ComponentNotAddedError(
                        f"Component {c.name} has not yet " +
                        "been added to the database."
                    )
 
        at_time = _parse_time(at_time) 
        from_time = _parse_time(from_time)
        to_time = _parse_time(to_time)

        # Build up the result of format (property vertex, relation)
        result = []

        if not exclude_subcomponents:
            for inout in ("in", "out"):
                query = g.t.V(self.id())
                if inout == "in":
                    query = query.inE(RelationSubcomponent.category)
                else:
                    query = query.outE(RelationSubcomponent.category)
                query = query.has('active', True).as_('e').otherV()
                if component:
                    query = query.hasId(*comp_id)
                query = query.id_().as_('vertex_id') \
                             .select('e').id_().as_('edge_id') \
                             .select('vertex_id', 'edge_id')
                for q in query.toList():
                    c = Component.from_id(q['vertex_id'])
                    if inout == "in":
                        inV, outV = self, c
                    else:
                        inV, outV = c, self
                    edge = RelationSubcomponent(
                        inVertex=inV,
                        outVertex=outV,
                        id=q['edge_id']['@value']['relationId']
                    )
                    result.append(edge)

        # List of property vertices of this property type and active at this
        # time
        query = g.t.V(self.id()).bothE(RelationConnection.category) \
                   .has('active', True)
        if at_time:
            query = query.has('start_time', P.lte(at_time)) \
                         .has('end_time', P.gt(at_time))
        else:
            if to_time:
                query = query.has('start_time', P.lt(to_time))
            if from_time:
                query = query.has('end_time', P.gt(from_time))
        query = query.as_('e').valueMap().as_('edge_props') \
                     .select('e').otherV()
        if component:
            query = query.hasId(*comp_id)
        query = query.id_().as_('vertex_id') \
                     .select('e').id_().as_('edge_id') \
                     .select('edge_props', 'vertex_id', 'edge_id')

        for q in query.toList():
            c = Component.from_id(q['vertex_id'])
            edge = RelationConnection(
                inVertex=c,
                outVertex=self,
                start=Timestamp._from_dict(q["edge_props"], "start_"),
                end=Timestamp._from_dict(q["edge_props"], "end_"),
                # weird but you have to
                id=q['edge_id']['@value']['relationId']
            )
            result.append(edge)

        return result

    @authenticated
    def get_all_connections_at_time(
        self, at_time: int, exclude_subcomponents: bool = False,
        permissions = None
    ):
        """
        Given a component, return all connections between this Component and 
        all other components.

        :param at_time: Time to check connections at. 
        :param exclude_subcomponents: If True, then do not return connections
            to subcomponents or supercomponents.

        :rtype: list[RelationConnection/RelationSubcomponent]
        """
        raise RuntimeError("Deprecated! Use get_connections().")

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # Build up the result of format (property vertex, relation)
        result = []

        if not exclude_subcomponents:
            # First do subcomponents.
            for q in g.t.V(self.id()).inE(RelationSubcomponent.category) \
                        .has('active', True).as_('e') \
                        .otherV().id_().as_('vertex_id') \
                        .select('e').id_().as_('edge_id') \
                        .select('vertex_id', 'edge_id').toList():
                c = Component.from_id(q['vertex_id'])
                edge = RelationSubcomponent(
                    inVertex=self,
                    outVertex=c,
                    id=q['edge_id']['@value']['relationId']
                )
                result.append(edge)

            # Now supercomponents.
            for q in g.t.V(self.id()).outE(RelationSubcomponent.category) \
                        .has('active', True).as_('e') \
                        .otherV().id_().as_('vertex_id') \
                        .select('e').id_().as_('edge_id') \
                        .select('vertex_id', 'edge_id').toList():
                c = Component.from_id(q['vertex_id'])
                edge = RelationSubcomponent(
                    inVertex=c,
                    outVertex=self,
                    id=q['edge_id']['@value']['relationId']
                )
                result.append(edge)

        # List of property vertices of this property type and active at this
        # time
        query = g.t.V(self.id()).bothE(RelationConnection.category) \
                   .has('active', True) \
                   .has('start_time', P.lte(at_time)) \
                   .has('end_time', P.gt(at_time)) \
                   .as_('e').valueMap().as_('edge_props') \
                   .select('e').otherV().id_().as_('vertex_id') \
                   .select('e').id_().as_('edge_id') \
                   .select('edge_props', 'vertex_id', 'edge_id').toList()

        for q in query:
            c = Component.from_id(q['vertex_id'])
            edge = RelationConnection(
                inVertex=c,
                outVertex=self,
                start=Timestamp._from_dict(q["edge_props"], "start_"),
                end=Timestamp._from_dict(q["edge_props"], "end_"),
                # weird but you have to
                id=q['edge_id']['@value']['relationId']
            )
            result.append(edge)

        return result

    @authenticated
    def get_all_connections_with(
        self, component, from_time: int = -1,
        to_time: int = g._TIMESTAMP_NO_ENDTIME_VALUE,
        permissions = None
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
        defaults to _TIMESTAMP_NO_ENDTIME_VALUE
        :type to_time: int, optional

        :rtype: list[RelationConnection]
        """
        raise RuntimeError("Deprecated! Use get_connections().")
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

        edges = g.t.V(self.id()).bothE(RelationConnection.category)\
                   .has('active', True)

        if to_time < g._TIMESTAMP_NO_ENDTIME_VALUE:
            edges = edges.has('start_time', P.lt(to_time))

        edges = edges.has('end_time', P.gt(from_time)) \
            .as_('e').otherV() \
            .hasId(component.id()).select('e') \
            .order().by(__.values('start_time'), Order.asc) \
            .project('properties', 'id').by(__.valueMap()).by(__.id_()).toList()

        return [RelationConnection(
            inVertex=self, outVertex=component,
            start=Timestamp._from_dict(e["properties"], "start_"),
            end=Timestamp._from_dict(e["properties"], "end_"),
            id=e['id']['@value']['relationId']  # weird but you have to
        ) for e in edges]

    @authenticated
    def get_connection(
        self, component, at_time: int,
        permissions = None
    ):
        """Given two components, return the edge that connected them at
        time :param at_time:.

        :param component: The other component to check the connections with.
        :type component: Component
        :param at_time: The time to check
        :type at_time: int
        """
        raise RuntimeError("Deprecated! Use get_connections().")

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

        e = g.t.V(self.id()).bothE(RelationConnection.category)\
               .has('active', True) \
               .has('start_time', P.lte(at_time)) \
               .has('end_time', P.gt(at_time)) \
               .as_('e').otherV() \
               .hasId(component.id()).select('e') \
               .project('properties', 'id')\
               .by(__.valueMap())\
               .by(__.id_()).toList()

        if len(e) == 0:
            return None

        assert len(e) == 1

        return RelationConnection(
            inVertex=self, outVertex=component,
            start=Timestamp._from_dict(e[0]["properties"], "start_"),
            end=Timestamp._from_dict(e[0]["properties"], "end_"),
            id=e[0]['id']['@value']['relationId']  # weird but you have to
        )

    def get_all_connections(self):
        """Return all connections between this Component and all other
        components, along with their edges of this component as
        a tuple of the form (Component, RelationConnection)

        :rtype: tuple[Component, RelationConnection]
        """
        raise RuntimeError("Deprecated! Use get_connections().")

        if not self.added_to_db():
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # list of property vertices of this property type
        # and active at this time
        query = g.t.V(self.id()).bothE(RelationConnection.category)\
                   .has('active', True) \
                   .as_('e').valueMap().as_('edge_props') \
                   .select('e').otherV().id_().as_('vertex_id') \
                   .select('edge_props', 'vertex_id').toList()

        # Build up the result of format (property vertex, relation)
        result = []

        for q in query:
            prop = Component.from_id(q['vertex_id'])
            edge = RelationConnection(
                inVertex=prop,
                outVertex=self,
                start=Timestamp._from_dict(q["edge_props"], "start_"),
                end=Timestamp._from_dict(q["edge_props"], "end_")
            )
            result.append((prop, edge))

        return result

    @authenticated
    def subcomponent_connect(
            self, component, strict_add=False, permissions = None):
        """
        Given another Component :param component:, make it a subcomponent of the current component.

        :param component: Another component that is a subcomponent of the current component.
        :type component: Component
        """

        if not self.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not component.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {component.name} has not yet" +
                "been added to the database."
            )

        if self.name == component.name:
            raise ComponentSubcomponentToSelfError(
                f"Trying to make {self.name} subcomponent to itself."
            )

        current_subcomponent = self.get_subcomponent(
            component=component,
            permissions=permissions
        )

        component_to_subcomponent = component.get_subcomponent(
            component=self,
            permissions=permissions
        )

        if component_to_subcomponent is not None:
            strictraise(strict_add, ComponentIsSubcomponentOfOtherComponentError,
                f"Component {component.name} is already a subcomponent of {self.name}"
            )
            return
        if current_subcomponent is not None:

            # Already a subcomponent!
            strictraise(strict_add, ComponentAlreadySubcomponentError,
                f"component {self.name} is already a subcomponent of component {component.name}"
            )
            return
        else:
            current_subcomponent = RelationSubcomponent(
                inVertex=self,
                outVertex=component
            )

            current_subcomponent.add(permissions=permissions)
#            print(f'subcomponent connected: {self} -> {component}')

    @authenticated
    def get_subcomponent(self, component, permissions = None):
        """Given the component itself and its subcomponent, return the edge between them.

        :param component: The other component which is the subcomponent of the current component.
        :type component: Component
        """

        # Done for troubleshooting (so you know which component is not added?)
        if not self.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not component.added_to_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {component.name} has not yet" +
                "been added to the database."
            )

        e = g.t.V(self.id()).bothE(RelationSubcomponent.category)\
               .has('active', True)\
               .as_('e').otherV()\
               .hasId(component.id())\
               .select('e').project('id').by(__.id_()).toList()

        if len(e) == 0:
            return None

        assert len(e) == 1

        return RelationSubcomponent(
            inVertex=self, outVertex=component,
            id=e[0]['id']['@value']['relationId']
        )

    @authenticated
    def disable_subcomponent(self, otherComponent,
                             disable_time: int = int(time.time()),
                             permissions = None):
        """Disabling an edge for a subcomponent

        :param otherComponent: Another Component that this component has 
          connection 'rel_subcomponent' with.
        :type othercomponent: Component

        :param disable_time: When this edge was disabled in the database (UNIX
          time).
        :type disable_time: int
        """

        g.t.V(self.id()).bothE(RelationSubcomponent.category)\
           .where(__.otherV().hasId(otherComponent.id()))\
           .property('active', False)\
           .property('time_disabled', disable_time).next()

    # @authenticated
    def added_to_db(self, permissions = None) -> bool:
        """Return whether this Component is added to the database,
        that is, whether the ID is not the virtual ID placeholder and perform a 
        query to the database to determine if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """
#        return self.in_db()

        return (
            self.id() != g._VIRTUAL_ID_PLACEHOLDER or (
                g.t.V()
                   .has('category', Component.category)
                   .has('name', self.name)\
                   .has('active', True).count().next() > 0
            )
        )

    @classmethod
    def _attrs_to_component(self, name, id, type_id, rev_ids, time_added, permissions=None):
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

        assert len(g.t.V(id).toList()) == 1

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
                type=g._vertex_cache[type_id],
                version=crev,
                time_added=time_added
            )
        )

        return g._vertex_cache[id]

    @classmethod
    def from_db(cls, name: str, permissions = None):
        """Query the database and return a Component instance based on
        name :param name:.

        :param name: The name attribute of the component serverside.
        :type name: str
        """

        try:
            d = g.t.V().has('active', True)\
                   .has('category', Component.category) \
                   .has('name', name) \
                   .project('id', 'type_id', 'rev_ids', 'time_added') \
                   .by(__.id_()) \
                   .by(__.both(RelationComponentType.category).id_()) \
                   .by(__.both(RelationVersion.category).id_().fold()) \
                   .by(__.values('time_added')).next()
        except StopIteration:
            raise ComponentNotAddedError

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
    def from_id(cls, id: int, permissions = None):
        """Query the database and return a Component instance based on
        the ID :param id:

        :param id: The ID of the component serverside.
        :type id: int
        """
        if id not in g._vertex_cache:

            d = g.t.V(id).project('name', 'type_id', 'rev_ids', 'time_added') \
                   .by(__.values('name')) \
                   .by(__.both(RelationComponentType.category).id_()) \
                   .by(__.both(RelationVersion.category).id_().fold()) \
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
            return g._vertex_cache[id]

    @classmethod
    def get_list(cls,
                 range: tuple,
                 order_by: str,
                 order_direction: str,
                 filters: list = [],
                 permissions = None):
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

        traversal = g.t.V().has('active', True)\
                       .has('category', Component.category)

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
            .by(__.id_()) \
            .by(__.values('name')) \
            .by(__.both(RelationComponentType.category).id_()) \
            .by(__.both(RelationVersion.category).id_().fold()) \
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
    def get_count(cls, filters: str, permissions = None):
        """Return the count of components given a list of filters.

        :param filters: A list of 3-tuples of the format (name, ctype, version)
        :type order_by: list

        :return: The number of Components.
        :rtype: int
        """

        traversal = g.t.V().has('active', True)\
                       .has('category', Component.category)

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

    def as_dict(self, at_time: int = None, bare = False, permissions = None):
        """Return a dictionary representation of this Component at time
        :param at_time: The time to check the component at. Pass `None` to get
          properties/flags/connexions at all times.
        :type at_time: int or None

        :param bare: If True, then only return a dictionary with the name and
        type and version and comments; if False, then also return all the
        properties, flags and connexions.
        :type bare: bool

        :return: A dictionary representation of this Components's attributes.
        :rtype: dict
        """
        # TODO: at_time has not yet been implemented!
        assert(at_time == None)
        
        base = {'name': self.name,
                'type': self.type.as_dict(),
                'version': self.version.as_dict() if self.version else {},
                'time_added': self.time_added}

        if not bare:
            prop_dicts = [{**prop.as_dict(), **rel.as_dict()} \
                for (prop, rel) in self.get_all_properties(permissions=permissions)
            ]

            conn_dicts = [{**{"name": conn.other_vertex(self).name},
                           **conn.as_dict()} \
                for conn in self.get_connections(exclude_subcomponents=True, permissions=permissions)
            ]

            flag_dicts = [flag.as_dict() for flag in self.get_all_flags(permissions=permissions)]

            subcomponent_dicts = [{"name": subcomponents.name} \
                for subcomponents in self.get_subcomponents(permissions=permissions)
            ]
        
            supercomponent_dicts = [{"name": supercomponents.name} \
                for supercomponents in self.get_supercomponents(permissions=permissions)
            ]
            extra = {
                'properties': prop_dicts,
                'connections': conn_dicts,
                'flags': flag_dicts,
                'subcomponents': subcomponent_dicts,
                'supercomponents': supercomponent_dicts
            }
        else:
            extra = {}

        return {**base, **extra}

    def __repr__(self):
        return f"{self.category} {self.type.name}: {self.name} ({self._id})"
