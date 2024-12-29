"""
flag.py

Classes for manipulating flags, flag types and flag severities.
"""
import time
import re
from unicodedata import name

import warnings
from xmlrpc.client import boolean
from attr import attr, attributes

from gremlin_python.process.traversal import Order, P, TextP
from sympy import true
from gremlin_python.process.graph_traversal import __, constant

import _global as g
from _base import Vertex, VertexAttr, Timestamp, strictraise
from _component_nodes import Component
from _exceptions import *
from _edges import RelationFlagType, RelationFlagComponent, RelationFlagSeverity

from typing import Optional, List

from padloper.method_decorators import authenticated

class FlagType(Vertex):
    """The representation of a flag type. 

    :ivar name: The name of the flag type.
    :ivar comments: Comments about the flag type.
    """

    category: str = "flag_type"
    _vertex_attrs: list = [
        VertexAttr("name", str),
        VertexAttr("comments", str, optional=True, default="")
    ]
    primary_attr = "name"

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

        if id not in g._vertex_cache:
            Vertex._cache_vertex(
                FlagType(
                    name=name,
                    comments=comments,
                    id=id
                )
            )

        return g._vertex_cache[id]


class FlagSeverity(Vertex):
    """
    The representation of a flag severity.
    """
    category: str = "flag_severity"
    _vertex_attrs: list = [
        VertexAttr("name", str),
        VertexAttr("comments", str, optional=True, default="")
    ]
    primary_attr = "name"


class Flag(Vertex):
    """
    The representation of a flag component.

    :ivar name: The name of the flag.
    :ivar comments: Comments associated with the flag in general.
    :ivar start: The starting timestamp of the flag.
    :ivar end: The ending timestamp of the flag.
    :ivar severity: The FlagSeverity instance representing the severity of the
        flag.
    :ivar type: The FlagType instance representing the type of the flag.
    :ivar components: A list of Component instances related to the flag.
    """

    category: str = "flag"
    _vertex_attrs: list = [
        VertexAttr("type", FlagType, edge_class=RelationFlagType),
        VertexAttr("severity", FlagSeverity, edge_class=RelationFlagSeverity),
        VertexAttr("notes", str, optional=True),
        VertexAttr("start", Timestamp),
        VertexAttr("end", Timestamp, optional=True,
                   default=Timestamp._no_end()),
        VertexAttr("components", Component, edge_class=RelationFlagComponent,
                   is_list=True, list_len=(0, int(1e10)))
    ]
    _primary_attr = None

    def end_flag(self, dummy):
        raise RuntimeError("Method deprecated. Use set_end().")

    @authenticated
    def set_end(self, end : Timestamp, permissions=None):
        """
        Given a flag, set the "end" attributes of the flag to indicate that this
        flag has been ended.

        :param end: The timestamp for the end of the flag.
        :type end: Timestamp
        """

        if not self.in_db(strict_check=False, permissions=permissions):
            raise FlagNotAddedError(
                f"Flag {self.name} has not yet been added to the database."
            )
        if self.end.time < g._TIMESTAMP_NO_ENDTIME_VALUE:
            raise ValueError("Flag already has an end time.")
        if self.start.time > end.time:
            raise ValueError("Flag ending time should be >= starting time.")

        self.end = end

        g.t.V(self.id()).property('end_time', end.time)\
           .property('end_uid', end.uid)\
           .property('end_edit_time', end.edit_time)\
           .property('end_comments', end.comments).iterate()
