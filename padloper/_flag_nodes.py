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

        traversal = g.t.V().has('active', True)\
                       .has('category', FlagType.category) \
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
            .by(__.id_()) \
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

        return g.t.V().has('active', True).has('category', FlagType.category) \
                  .has('name', TextP.containing(name_substring)) \
                  .count().next()


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

        traversal = g.t.V().has('active', True)\
                       .has('category', FlagSeverity.category)

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
            traversal = traversal.order().by('name', direction)

        # flag severity query to DB
        fs = traversal.range(range[0], range[1]) \
                      .project('id', 'name') \
                      .by(__.id_()) \
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
        {'name', 'type','severity'}
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

        assert order_by in {'name', 'type', 'severity'}

        traversal = g.t.V().has('active', True).has('category', Flag.category)

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

        elif order_by == 'type':
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

        elif order_by == 'severity':
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
            .by(__.id_()) \
            .by(__.valueMap()) \
            .by(__.both(RelationFlagType.category).id_()).by(__.both(RelationFlagSeverity.category).id_()).by(__.both(RelationFlagComponent.category).id_().fold()) \
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
                    comments=attrs['comments'][0],
                    start=Timestamp._from_dict(attrs, "start_"),
                    severity=FlagSeverity.from_id(fseverity_id),
                    type=FlagType.from_id(ftype_id),
                    components=fcomponents,
                    end=Timestamp._from_dict(attrs, "end_")
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
        traversal = g.t.V().has('active', True).has('category', Flag.category)

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

    def end_flag(self, dummy):
        raise RuntimeError("Method deprecated. Use set_end().")

    def set_end(self, end : Timestamp):
        """
        Given a flag, set the "end" attributes of the flag to indicate that this
        flag has been ended.

        :param end: The timestamp for the end of the flag.
        :type end: Timestamp
        """

        if not self.in_db(strict_check=False):
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
