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
            nn = kwargs["type"].n_values
            if len(kwargs["values"]) != nn:
                raise TypeError("%d value%s %s required." %\
                                (nn, "" if nn == 1 else "s",
                                 "is" if nn == 1 else "are"))
        except KeyError:
            raise TypeError("%s() missing required keyword \"type\"." %\
                            self.__class__.__name__)

        for val in kwargs["values"]:
            if not bool(re.fullmatch(kwargs["type"].allowed_regex, val)):
                raise ValueError(
                    f"Property with value {val} of type " +
                    f"{kwargs['type'].name} does not match regex " +
                    f"{kwargs['type'].allowed_regex}."
                )

    # Shouldn't be called directly, but will add authentication.
    @authenticated
    def _add(self, permissions=None):
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
