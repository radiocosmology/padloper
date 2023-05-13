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
from gremlin_python.process.graph_traversal import __, constant
from gremlin_python.process.traversal import Order, P, TextP
import time
import _global as g
from _exceptions import *

#import re
#from unicodedata import name
#import warnings
#from xmlrpc.client import boolean
#from attr import attr, attributes
#from sympy import true
#from typing import Optional, List

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
    g._user = dict()
    g._user["id"] = uid

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

    def added_to_db(self) -> bool:
        """Return whether this element is added to the database,
        that is, whether the ID is not the virtual ID placeholder.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return self._id != g._VIRTUAL_ID_PLACEHOLDER


    def __repr__(self):
        return str(self._id)


class Vertex(Element):
    """
    The representation of a vertex. Can contain attributes.

    :ivar category: The category of the Vertex.
    :ivar time_added: When this vertex was added to the database (UNIX time).
    :ivar time_disabled: When this vertex was disabled in the database (UNIX 
          time).
    :ivar active: Whether the vertex is disabled or not.
    :ivar replacement: If the vertex has been replaced, then this property
          points towards the vertex that replaced it.
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

            self.time_disabled = g._TIMESTAMP_NO_EDITTIME_VALUE

            traversal = g.t.addV().property('category', self.category) \
                           .property('time_added', self.time_added) \
                           .property('time_disabled', self.time_disabled) \
                           .property('active', self.active) \
                           .property('replacement', self.replacement)

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

    def replace(self, id):
        """Replaces the vertex in the JanusGraph DB with the new vertex by
        changing its property 'active' from true to false and transfering
        all the edges to the new vertex. The old vertex contains the ID of
        the new vertex as an attribute.d

        :param id: ID of the new Vertex.
        :type id: int

        """

        # The 'replacement' property now points to the new vertex that replaced
        # the self vertex..
        g.t.V(self.id()).property('replacement', id).iterate()

        # List of all the properties of the outgoing edges from the self vertex.
        o_edges_values_list = g.t.V(self.id()).outE().valueMap().toList()

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
            add_edge_1 = g.t.V(id).addE(o_edges_values_list[i]['category'])\
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

            add_edge_2 = g.t.V(id).addE(i_edges_values_list[j]['category'])\
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

    def disable(self, disable_time: int = int(time.time())):
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

        # Disables all the conencted edges.
        for i in range(len(edge_count)):
            g.t.V(self.id()).bothE()[i].property('active', False).property(
                'time_disabled', disable_time).next()

    def added_to_db(self) -> bool:
        """Return whether this vertex is added to the database,
        that is, whether the ID is not the virtual ID placeholder and perform 
        a query to the database to determine if the vertex 
        has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != g._VIRTUAL_ID_PLACEHOLDER or
            g.t.V(self.id()).count().next() > 0
        )

    def _in_vertex_cache(self) -> bool:
        """Return whether this vertex ID is in the vertex cache.

        :return: True if vertex ID is in _vertex_cache, false otherwise.
        :rtype: bool
        """

        return self.id() in g._vertex_cache

    @classmethod
    def _cache_vertex(cls, vertex):
        """Add a vertex and its ID to the vertex cache if not already added,
        and return this new cached vertex. 

        TODO: Raise an error if already cached, because that'd mean there's
        an implementation error with the caching.
        """

        if vertex.id() not in g._vertex_cache:

            if not vertex.added_to_db():

                # Do nothing?

                return

            g._vertex_cache[vertex.id()] = vertex

        return g._vertex_cache[vertex.id()]


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

    def added_to_db(self) -> bool:
        """Return whether this edge is added to the database,
        that is, whether the ID is not the virtual ID placeholder, and perform a
        query to the database to determine if the vertex has already been
        added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != g._VIRTUAL_ID_PLACEHOLDER or
            g.t.E(self.id()).count().next() > 0
        )

class _RawTimestamp:
    """A timestamp for starting or ending connections, properties, etc.
    This is a private class used internally by Padloper. Users who
    load the module should use the public the `Timestamp` class that inherits
    it.

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

    def __init__(self, time, uid, edit_time, comments=""):
        self.time = time
        self.uid = uid
        self.edit_time = edit_time
        self.comments = comments
    
    @classmethod
    def from_dict(cls, d, prefix, index=0):
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
        return cls(dd["%stime" % prefix],
                   dd["%suid" % prefix],
                   dd["%sedit_time" % prefix],
                   dd["%scomments" % prefix]
                )

    @classmethod
    def no_end(cls):
        """Create a placeholder timestamp.
        This is for when the end timestamp does not yet exist; the timestamp has
        no user id, and reserved values for the time and edit_time.
        """
        return cls(g._TIMESTAMP_NO_ENDTIME_VALUE, "", 
                   g._TIMESTAMP_NO_EDITTIME_VALUE, comments="")

    def as_dict(self):
        return {
            "time": self.time,
            "uid": self.uid,
            "edit_time": self.edit_time,
            "comments": self.comments
        }

class Timestamp(_RawTimestamp):
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
        try:
            self.uid = g._user["id"]
        except TypeError:
            raise RuntimeError(
                "You must call padloper.set_user() before creating a "\
                "Timestamp."
            )
        super().__init__(at_time, self.uid, int(time.time()), comments=comments)

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
            self.end = _RawTimestamp.no_end()
        Edge.__init__(self=self, id=id, inVertex=inVertex, outVertex=outVertex)

    def as_dict(self):
        """Return a dictionary representation."""
        return {
            "start": self.start.as_dict(),
            "end": self.end.as_dict()
        }

    def add(self):
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
