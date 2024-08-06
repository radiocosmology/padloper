"""
property_nodes.py

Classes for manipulating properties and property types.
"""
import time
import re
from unicodedata import name

import warnings
from xmlrpc.client import boolean
from attr import attr, attributes

from gremlin_python.process.traversal import Order, P, TextP
from sympy import true
import _global as g
from gremlin_python.process.graph_traversal import __, constant

from _base import Vertex, VertexAttr, strictraise
from _component_nodes import ComponentType
from _edges import RelationPropertyType, RelationPropertyAllowedType, \
                   RelationComponentType
from _exceptions import *

from typing import Optional, List

from padloper.method_decorators import authenticated

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
<<<<<<< HEAD

    name: str
    units: str
    allowed_regex: str
    n_values: int
    comments: str
    allowed_types: List[ComponentType]

    def __new__(
        cls, name: str, units: str, allowed_regex: str,
        n_values: int, allowed_types: List[ComponentType], comments: str = "",
        id: int = g._VIRTUAL_ID_PLACEHOLDER
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
        defaults to _VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id is not g._VIRTUAL_ID_PLACEHOLDER and id in g._vertex_cache:
            return g._vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(
        self, name: str, units: str, allowed_regex: str,
        n_values: int, allowed_types: List[ComponentType], comments: str = "",
        id: int = g._VIRTUAL_ID_PLACEHOLDER
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
        defaults to _VIRTUAL_ID_PLACEHOLDER
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

    def as_dict(self):
        """Return dictionary representation."""
        return {
            'name': self.name,
            'units': self.units,
            'allowed_regex': self.allowed_regex,
            'n_values': self.n_values,
            'allowed_types': [t.name for t in self.allowed_types],
            'comments': self.comments
        }

    @authenticated
    def add(self, strict_add=False, permissions=None):
        """Add this PropertyType to the serverside.
        """

        # If already added, raise an error!
        if self.added_to_db(permissions=permissions):
            strictraise(strict_add, VertexAlreadyAddedError,
                f"PropertyType with name {self.name} " +
                "already exists in the database."
            )
            return self.from_db(self.name)


        attributes = {
            'name': self.name,
            'units': self.units,
            'allowed_regex': self.allowed_regex,
            'n_values': self.n_values,
            'comments': self.comments
        }

        Vertex.add(self, attributes)

        for ctype in self.allowed_types:

            if not ctype.added_to_db(permissions=permissions):
                ctype.add(permissions=permissions)

            e = RelationPropertyAllowedType(
                inVertex=ctype,
                outVertex=self
            )

            e.add()

        print(f"Added {self}")
        return self

    @authenticated
    def replace(self, newVertex, disable_time: int = int(time.time()), permissions=None):
        """Replaces the PropertyType vertex in the serverside.

        :param newVertex: The new PropertyType vertex that is replacing the old PropertyType vertex.
        :type newVertex: PropertyType

        :param disable_time: When this vertex was disabled in the database (UNIX time).
        :type disable_time: int
        """

        # Step 1
        g.t.V(self.id()).property('active', False)\
           .property('time_disabled', disable_time).iterate()

        # Step 2
        newVertex.add()

        # Step 3
        newVertexId = newVertex.id()

        Vertex.replace(self=self, id=newVertexId)

    # @authenticated
    def added_to_db(self, permissions=None) -> bool:
        """Return whether this PropertyType is added to the database,
        that is, whether the ID is not the virtual ID placeholder and perform a 
        query to the database to determine if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != g._VIRTUAL_ID_PLACEHOLDER or (\
                g.t.V().has('category', PropertyType.category)
                   .has('name', self.name)\
                   .has('active', True).count().next() > 0 \
            )
        )

    @classmethod
    def _attrs_to_type(
        cls,
        name: str, units: str, allowed_regex: str,
        n_values: int, allowed_types: List[ComponentType], comments: str = "",
        id: int = g._VIRTUAL_ID_PLACEHOLDER
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
        defaults to _VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id not in g._vertex_cache:
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

        return g._vertex_cache[id]

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a PropertyType instance based on
        name :param name:.

        :param name: The name attribute of the property type
        :type name: str
        """

        try:
            d = g.t.V().has('active', True) \
                   .has('category', PropertyType.category).has('name', name) \
                   .project('id', 'attrs', 'type_ids') \
                   .by(__.id_()) \
                   .by(__.valueMap()) \
                   .by(__.both(RelationPropertyAllowedType.category) \
                   .id_().fold()) \
                   .next()
        except StopIteration:
            raise PropertyTypeNotAddedError

        # to access attributes from attrs, do attrs[...][0]
        id, attrs, ctype_ids = d['id'], d['attrs'], d['type_ids']

        if id not in g._vertex_cache:

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

        return g._vertex_cache[id]

    @classmethod
    def from_id(cls, id: int):
        """Query the database and return a PropertyType instance based on
        the ID.

        :param id: The serverside ID of the PropertyType vertex.
        :type id: int
        :return: Return a PropertyType from that ID.
        :rtype: PropertyType
        """

        if id not in g._vertex_cache:

            d = g.t.V(id).project('attrs', 'type_ids') \
                   .by(__.valueMap()) \
                   .by(__.both(RelationPropertyAllowedType.category)\
                     .id_().fold()\
                   ).next()

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

        return g._vertex_cache[id]
=======
    _vertex_attrs: list = [
        VertexAttr("name", str),
        VertexAttr("units", str, optional=True, default=""),
        VertexAttr("allowed_regex", str, optional=True, default=".*"),
        VertexAttr("n_values", int),
        VertexAttr("allowed_types", ComponentType, 
                   edge_class=RelationPropertyAllowedType, is_list=True,
                   list_len=(1, int(1e10))),
        VertexAttr("comments", str, optional=True, default="")
    ]
    primary_attr = "name"
>>>>>>> main

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

        traversal = g.t.V().has('active', True)\
                       .has('category', PropertyType.category)

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
                       .project("id", "time_added", "uid_added",
                                "time_disabled", "uid_disabled", "name",
                                "units", "allowed_regex", "n_values",
                                "allowed_types", "comments") \
                       .by(__.id_()) \
                       .by(__.values('time_added')) \
                       .by(__.values('uid_added')) \
                       .by(__.values('time_disabled')) \
                       .by(__.values('uid_disabled')) \
                       .by(__.values('name')) \
                       .by(__.values("units")) \
                       .by(__.values("allowed_regex")) \
                       .by(__.values("n_values")) \
                       .by(__.both(RelationPropertyAllowedType.category) \
                                   .id_().fold()) \
                       .by(__.values("comments")) \
                       .toList()

        types = []

        for entry in pts:
            ctypes = []

            for ctype_id in entry["allowed_types"]:
                ctypes.append(ComponentType.from_id(ctype_id))

            print(entry)
            types.append(PropertyType._from_attrs(entry))

        return types

    @classmethod
    def get_count(cls, filters: list):
        """Return the count of PropertyType given a list of filters

        :param filters: A list of 2-tuples of the format (name, ctype)
        :type order_by: list

        :return: The number of PropertyType that agree with
        :param filters:.
        :rtype: int
        """

        traversal = g.t.V().has('active', True)\
                       .has('category', PropertyType.category)

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

        # traversal = g.t.V().has('category', PropertyType.category) \
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

    def __repr__(self):
        return f"{self.category}: {self.name}"

class Property(Vertex):
    """The representation of a property.

    :ivar values: The values contained within the property.
    :ivar type: The PropertyType instance representing the property
    type of this property.
    """
    category: str = "property"

    _vertex_attrs: list = [
        VertexAttr("type", PropertyType, edge_class=RelationPropertyType),
        VertexAttr("values", str, is_list=True)
    ]
    primary_attr = None

    def _validate(self, **kwargs):
        """This is called by the initialiser; to do some important checks."""
        try:
            # If the user passes a string rather than a list of strings,
            # interpret it as a list of length one.
            if not isinstance(kwargs["values"], list):
                kwargs["values"] = [kwargs["values"]]
        except KeyError:
            raise TypeError("%s() missing required keyword \"values\"." %\
                            self.__class__.__name__)

<<<<<<< HEAD
        if len(values) != int(type.n_values):
            raise PropertyWrongNValuesError
=======
        try:
            nn = kwargs["type"].n_values
            if len(kwargs["values"]) != nn:
                raise TypeError("%d value%s %s required." %\
                                (nn, "" if nn == 1 else "s",
                                 "is" if nn == 1 else "are"))
        except KeyError:
            raise TypeError("%s() missing required keyword \"type\"." %\
                            self.__class__.__name__)
>>>>>>> main

        for val in kwargs["values"]:
            if not bool(re.fullmatch(kwargs["type"].allowed_regex, val)):
                raise ValueError(
                    f"Property with value {val} of type " +
                    f"{kwargs['type'].name} does not match regex " +
                    f"{kwargs['type'].allowed_regex}."
                )

<<<<<<< HEAD
        self.values = values
        self.type = type

        Vertex.__init__(self, id=id)

    # Shouldn't be called directly, but will add authentication.
    @authenticated
    def _add(self, permissions=None):
=======
    def _add(self):
>>>>>>> main
        """
        Add this Property to the serverside.
        """

        attributes = {
            'values': self.values
        }

        Vertex.add(self, attributes)

        if not self.type.added_to_db(permissions=permissions):
            self.type.add(permissions=permissions)

        e = RelationPropertyType(
            inVertex=self.type,
            outVertex=self
        )

        e.add()

    def as_dict(self):
        """Return a dictionary representation of this property."""
        return {
            'values': self.values,
            'type': self.type.as_dict()
        }

    def __repr__(self):
        return f"{self.category}: {self.type.name} ({self.values})"
