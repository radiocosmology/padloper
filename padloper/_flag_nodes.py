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

    :ivar name: The name of the severity.
    """
    category: str = "flag_severity"

    name: str

    def __new__(cls, name: str, id: int = g._VIRTUAL_ID_PLACEHOLDER):
        """
        Return a FlagSeverity instance given the desired attribute.

        :param name: Indicates the severity of a flag.
        :type name: str

        :param id: The serverside ID of the FlagType,
        defaults to _VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id is not g._VIRTUAL_ID_PLACEHOLDER and id in g._vertex_cache:
            return g._vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(self, name: str, id: int = g._VIRTUAL_ID_PLACEHOLDER):
        """
        Initialize a FlagSeverity instance given the FlagSeverity instance given the desired attributes.

        :param name: Indicates the severity of a flag.
        :type name: str

        :param id: The serverside ID of the FlagType,
        defaults to _VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        self.name = name

        Vertex.__init__(self, id=id)

    def as_dict(self):
        """Return a dictionary representation."""
        return {"name": self.name}

    @authenticated
    def add(self, strict_add=False, permissions=None):
        """Add this FlagSeverity to the database."""

        # If already added.
        if self.added_to_db(permissions=permissions):
            strictraise(strict_add, VertexAlreadyAddedError,
                f"FlagSeverity with name {self.name}" +
                "already exists in the database."
            )
            return self.from_db(self.name)


        attributes = {
            'name': self.name
        }

        Vertex.add(self=self, attributes=attributes)

        print(f"Added {self}")
        return self

    @authenticated
    def replace(self, newVertex, disable_time: int = int(time.time()), permissions=None):
        """Replaces the FlagSeverity vertex in the serverside.

        :param newVertex: The new FlagSeverity vertex that is replacing the old FlagSeverity vertex.
        :type newVertex: FlagSeverity

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
        """
        Return whether this FlagSeverity is added to the database, that is, whether the ID is not the virtual ID placeholder and perform a query to the database to determine if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != g._VIRTUAL_ID_PLACEHOLDER or (\
                g.t.V().has('category', FlagSeverity.category)\
                   .has('name', self.name)\
                   .has('active', True).count().next() == 1 \
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

        try:
            d = g.t.V().has('active', True) \
                   .has('category', FlagSeverity.category).has('name', name) \
                   .as_('v').valueMap().as_('props')\
                   .select('v').id_().as_('id') \
                   .select('props', 'id').next()
        except StopIteration:
            raise FlagSeverityNotAddedError

        props, id = d['props'], d['id']

        Vertex._cache_vertex(
            FlagSeverity(
                name=name,
                id=id
            )
        )

        return g._vertex_cache[id]

    @classmethod
    def from_id(cls, id: int):
        """Query the database and return a FlagSeverity instance based on the ID.

        :param id: The serverside ID of the FlagSeverity vertex.
        :type id: int

        :return: Return a FlagSeverity from that ID.
        :rtype: FlagSeverity
        """

        if id not in g._vertex_cache:

            d = g.t.V(id).valueMap().next()

            Vertex._cache_vertex(
                FlagSeverity(
                    name=d['name'][0],
                    id=id
                )
            )

        return g._vertex_cache[id]

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

        if id not in g._vertex_cache:
            Vertex._cache_vertex(
                FlagSeverity(
                    name=name,
                    id=id
                )
            )

        return g._vertex_cache[id]

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
    _vertex_attr: list = [
        VertexAttr("name", str),
        VertexAttr("comments", str)
    ]

    name: str
    comments: str
    start: Timestamp
    end: Timestamp
    severity: FlagSeverity
    type: FlagType
    components: List[Component]

    def __new__(cls, name: str, start: Timestamp, severity: FlagSeverity, 
                type: FlagType, comments: str = "", end: Timestamp = None, 
                components: List[Component] = [],
                id: int = g._VIRTUAL_ID_PLACEHOLDER):
        """
        Return a Flag instance with the specified properties.

        :param name: The name of the flag.
        :type name: str
        :param comments: Comments associated with the flag in general,
            defaults to ""
        :type comments: str, optional
        :param start: The starting timestamp of the flag.
        :type start: Timestamp
        :param severity: The flag severity that indicates the severity of the
            flag.
        :type severity: FlagSeverity
        :param type: The flag type that indicates the type of the flag.
        :type type: FlagType
        :param components: A list of The flag components that have this flag.
        :type components: List[Component]
        :param end: The ending timestamp of the flag.
        :type end: Timestamp or None.
        """
        if id is not g._VIRTUAL_ID_PLACEHOLDER and id in g._vertex_cache:
            return g._vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(self, name: str, start: Timestamp, severity: FlagSeverity, 
                type: FlagType, comments: str = "", end: Timestamp = None, 
                components: List[Component] = [],
                id: int = g._VIRTUAL_ID_PLACEHOLDER):
        self.name = name
        self.comments = comments
        self.start = start
        self.severity = severity
        self.type = type
        self.components = components
        if end:
            self.end = end
        else:
            self.end = Timestamp._no_end()

        Vertex.__init__(self=self, id=id)

    def as_dict(self):
        """Return a dictionary representation."""
        return {
            "name": self.name,
            "comments": self.comments,
            "type": self.type.as_dict(),
            "severity": self.severity.as_dict(),
            "start": {
                "time": self.start.time,
                "uid": self.start.uid,
                "edit_time": self.start.edit_time,
                "comments": self.start.comments
            },
            "end": {
                "time": self.end.time,
                "uid": self.end.uid,
                "edit_time": self.end.edit_time,
                "comments": self.end.comments
            },
            "components": [c.as_dict(bare=True) for c in self.components]
        }

    
    @authenticated
    def add(self, strict_add=False, permissions=None):
        """
        Add this Flag instance to the database.
        """

        if self.added_to_db(permissions=permissions):
            strictraise(strict_add, VertexAlreadyAddedError,
                f"Flag with name {self.name}" +
                "already exists in the database."
            )
            return self.from_db(self.name)


        attributes = {
            'name': self.name,
            'comments': self.comments,
            'start_time': self.start.time,
            'start_uid': self.start.uid,
            'start_edit_time': self.start.edit_time,
            'start_comments': self.start.comments,
            'end_time': self.end.time,
            'end_uid': self.end.uid,
            'end_edit_time': self.end.edit_time,
            'end_comments': self.end.comments
        }

        Vertex.add(self=self, attributes=attributes)

        if not self.type.added_to_db(permissions=permissions):
            self.type.add()

        e = RelationFlagType(
            inVertex=self.type,
            outVertex=self
        )

        e.add()

        if not self.severity.added_to_db(permissions=permissions):
            self.severity.add(permissions=permissions)

        e = RelationFlagSeverity(
            inVertex=self.severity,
            outVertex=self
        )

        e.add()

        for c in self.components:

            if not c.added_to_db(permissions=permissions):
                c.add(permissions=permissions)

            e = RelationFlagComponent(
                inVertex=c,
                outVertex=self
            )

            e.add()

        print(f"Added {self}")
        return self

    @authenticated
    def replace(self, newVertex, disable_time: int = int(time.time()), permissions=None):
        """Replaces the Flag vertex in the serverside.

        :param newVertex: The new Flag vertex that is replacing the old Flag vertex.
        :type newVertex: Flag

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
        """Return whether this Flag is added to the database,that is, whether the ID is not the virtual ID placeholder and perform a query to the database if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != g._VIRTUAL_ID_PLACEHOLDER or (\
                g.t.V().has('category', Flag.category)\
                   .has('name', self.name)\
                   .has('active', True).count().next() > 0 \
            )
        )

    @classmethod
    def _attrs_to_flag(cls, name: str, start: Timestamp,
                       severity: FlagSeverity, type: FlagType,
                       comments: str = "", end: Timestamp = None, 
                       components: List[Component] = [],
                       id: int = g._VIRTUAL_ID_PLACEHOLDER):
        """Given the id and attributes of a Flag, see if one exists in the
        cache. If so, return the cached Flag. Otherwise, create a new one,
        cache it, and return it.

        :param name: The name of the flag.
        :type name: str
        :param comments: Comments associated with the flag in general,
            defaults to ""
        :type comments: str, optional
        :param start: The starting timestamp of the flag.
        :type start: Timestamp
        :param severity: The flag severity that indicates the severity of the
            flag.
        :type severity: FlagSeverity
        :param type: The flag type that indicates the type of the flag.
        :type type: FlagType
        :param components: A list of The flag components that have this flag.
        :type components: List[Component]
        :param end: The ending timestamp of the flag.
        :type end: Timestamp or None.
        """

        if id not in g._vertex_cache:
            Vertex._cache_vertex(
                Flag(
                    name=name,
                    comments=comments,
                    start=start,
                    severity=severity,
                    type=type,
                    components=components,
                    end=end,
                    id=id
                )
            )

        return g._vertex_cache[id]

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a Flag instance based on the name
        :param name:, connected to the necessary Components, FlagType
        instances and FlagSeverity instance.

        :param name: The name of the Flag instance
        :type name: str
        """

        try:
            d = g.t.V().has('active', True).has('category', Flag.category) \
                   .has('name', name) \
                   .project('id', 'attrs', 'type_id', 'severity_id',
                            'component_ids') \
                   .by(__.id_()) \
                   .by(__.valueMap()) \
                   .by(__.both(RelationFlagType.category).id_()) \
                   .by(__.both(RelationFlagSeverity.category).id_()) \
                   .by(__.both(RelationFlagComponent.category).id_()\
                   .fold()).next()
        except StopIteration:
            raise FlagNotAddedError

        id, attrs, type_id, severity_id, component_ids = d['id'], d['attrs'], \
            d['type_id'], d['severity_id'], d['component_ids']

        if id not in g._vertex_cache:

            Vertex._cache_vertex(FlagType.from_id(type_id))

            Vertex._cache_vertex(FlagSeverity.from_id(severity_id))

            components = []

            for c_id in component_ids:
                components.append(Component.from_id(c_id))

            Vertex._cache_vertex(
                Flag(
                    name=name,
                    comments=attrs['comments'][0],
                    start=Timestamp._from_dict(attrs, "start_"),
                    severity=g._vertex_cache[severity_id],
                    type=g._vertex_cache[type_id],
                    components=components,
                    end=Timestamp._from_dict(attrs, "end_"),
                    id=id
                )
            )

        return g._vertex_cache[id]

    @classmethod
    def from_id(cls, id: int):
        """Given an ID of a serverside flag vertex, return a Flag instance.
        """

        if id not in g._vertex_cache:

            d = g.t.V(id).project('attrs', 'fseverity_id', 'ftype_id',
                                  'fcomponent_ids')\
                   .by(__.valueMap())\
                   .by(__.both(RelationFlagSeverity.category).id_())\
                   .by(__.both(RelationFlagType.category).id_())\
                   .by(__.both(RelationFlagComponent.category).id_().fold())\
                   .next()

            # to access attributes from attrs, do attrs[...][0]
            attrs, fseverity_id, ftype_id, fcomponent_ids = d['attrs'], d[
                'fseverity_id'], d['ftype_id'], d['fcomponent_ids']

            components = []

            for component_id in fcomponent_ids:
                components.append(Component.from_id(component_id))

            Vertex._cache_vertex(
                Flag(
                    name=attrs['name'][0],
                    comments=attrs['comments'][0],
                    start=Timestamp._from_dict(attrs, "start_"),
                    severity=FlagSeverity.from_id(fseverity_id),
                    type=FlagType.from_id(ftype_id),
                    components=components,
                    end=Timestamp._from_dict(attrs, "end_"),
                    id=id
                )
            )

        return g._vertex_cache[id]

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

    @authenticated
    def end_flag(self, end : Timestamp, permissions=None):
        """
        Given a flag, set the "end" attributes of the flag to indicate that this
        flag has been ended.

        :param end: The timestamp for the end of the flag.
        :type end: Timestamp
        """

        if not self.added_to_db(permissions=permissions):
            raise FlagNotAddedError(
                f"Flag {self.name} has not yet been added to the database."
            )

        self.end = end

        g.t.V(self.id()).property('end_time', end.time)\
           .property('end_uid', end.uid)\
           .property('end_edit_time', end.edit_time)\
           .property('end_comments', end.comments).iterate()
