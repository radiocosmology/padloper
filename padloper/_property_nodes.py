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
from _edges import RelationPropertyType, RelationPropertyAllowedType
from _exceptions import *

from typing import Optional, List

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
            .project('id', 'attrs', 'type_ids') \
            .by(__.id_()) \
            .by(__.valueMap()) \
            .by(__.both(RelationPropertyAllowedType.category).id_().fold()) \
            .toList()

        types = []

        for entry in pts:
            id, ctype_ids, attrs = entry['id'], entry['type_ids'], \
                entry['attrs']

            ctypes = []

            for ctype_id in ctype_ids:
                ctypes.append(ComponentType.from_id(ctype_id))

            types.append(
                PropertyType._attrs_to_type(
                    id=id,
                    name=attrs['name'][0],
                    units=attrs['units'][0],
                    allowed_regex=attrs['allowed_regex'][0],
                    n_values=attrs['n_values'][0],
                    comments=attrs['comments'][0],
                    allowed_types=ctypes,
                )
            )

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

        try:
            if len(kwargs["values"]) != kwargs["type"].n_values:
                raise TypeError("%d values are required." %\
                                kwargs["type"].n_values)
        except KeyError:
            raise TypeError("%s() missing required keyword \"type\"." %\
                            self.__class__.__name__)

        for val in kwargs["values"]:
            if not bool(re.fullmatch(kwargs["type"].allowed_regex, val)):
                raise ValueError(
                    f"Property with values {values} of type " +
                    f"{type.name} does not match regex " +
                    f"{type.allowed_regex} for value {val}."
                )

    def _add(self):
        """
        Add this Property to the serverside.
        """

        attributes = {
            'values': self.values
        }

        Vertex.add(self, attributes)

        if not self.type.added_to_db():
            self.type.add()

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

    @classmethod
    def from_id(cls, id: int):
        """Given an ID of a serverside property vertex, 
        return a Property instance. 
        """

        if id not in g._vertex_cache:

            d = g.t.V(id).project('values', 'ptype_id') \
                   .by(__.properties('values').value().fold()) \
                   .by(__.both(RelationPropertyType.category).id_()).next()

            values, ptype_id = d['values'], d['ptype_id']

            if not isinstance(values, list):
                values = [values]

            Vertex._cache_vertex(
                Property(
                    values=values,
                    type=PropertyType.from_id(ptype_id),
                    id=id
                )
            )

        return g._vertex_cache[id]

    def __repr__(self):
        return f"{self.category}: {self.type.name} ({self.values})"
