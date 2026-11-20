"""
_sequences.py

Classes for setting up naming/numbering sequences for components.
"""

import re
import time
from gremlin_python.process.traversal import Order, P, TextP, T, Direction
from gremlin_python.process.graph_traversal import __, constant

import _global as g
from _exceptions import *
from _base import (strictraise, Edge, Timestamp, Vertex, VertexAttr,
                   _parse_time, authenticated)
from _component_nodes import ComponentType
from _edges import RelationComponentSequence


class ComponentSequence(Vertex):
    """
    A numbering sequence for components.

    For certain components, this sequence will auto-increment when creating
    labels. For other components, this stores the standard label sequence
    from the manufacturer or otherwise. The implementation of such sequence
    will be used to auto-populate the component type when scanned in.

    Attributes
    ----------
    component_type : ComponentType
    """

    category: str = "sequence"
    _vertex_attrs: list = [
        VertexAttr("name", str),
        VertexAttr("component_type", ComponentType,
                   edge_class=RelationComponentSequence),
        VertexAttr("format", str),
        VertexAttr("increment", bool, default=False),
        VertexAttr("next_seq", int, default=0),
    ]
    primary_attr: str = "name"
    name: str = "default"

    # define node attribute types for type-checking
    component_type: ComponentType
    format: str  # @TODO: change this attribute from a reserved word
    increment: bool
    next_seq: int

    def _validate(self, **kwargs):
        return super()._validate(**kwargs)

    @authenticated
    def update(self, permissions=None, **kwargs):
        # set the new values client-side
        self.name = kwargs.get('name', self.name)
        self.component_type = kwargs.get('component_type', self.component_type)
        self.format = kwargs.get('format', self.format)
        self.increment = kwargs.get('increment', self.increment)
        self.next_seq = kwargs.get('next_seq', self.next_seq)

        # set the properties on the graph object
        g.t.V(self.id()).property('name', self.name)\
            .property('format', self.format)\
            .property('increment', self.increment)\
            .property('next_seq', self.next_seq)\
            .iterate()

        # remove the old edge to component type
        g.t.V(self.id()).bothE(RelationComponentSequence.category).drop()\
            .iterate()

        # add the new connection to component type
        g.t.V(self.id()).addE(RelationComponentSequence.category)\
            .from_(__.V(self.component_type.id())).iterate()
        return

    @authenticated
    def delete(self, permissions=None):
        # remove edges associated with this node before deleting the node
        g.t.V(self.id()).bothE().drop().iterate()

        # remove the node after removing the edges
        g.t.V(self.id()).drop().iterate()
        return

    @classmethod
    def match(cls, cname: str):
        sequences = cls.get_list()
        matches = [
            seq for seq in sequences
            if re.fullmatch(seq.format, cname)
        ]
        return matches[0] if matches else None
