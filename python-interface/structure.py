"""
structure.py

Contains methods for storing clientside interface information.

"""

from copy import Error
from graph_connection import g
from gremlin_python.process.graph_traversal import __   


from typing import Optional, List

# A placeholder value for the end_time attribute for a 
# connection that is still ongoing.
EXISTING_CONNECTION_END_PLACEHOLDER = 2**63 - 1

# A placeholder value for the end_edit_time attribute for a connection
# that is still ongoing.
EXISTING_CONNECTION_END_EDIT_PLACEHOLDER = -1

# Placeholder for the ID of an element that does not exist serverside.
VIRTUAL_ID_PLACEHOLDER = -1

_vertex_cache = dict()

class Element:
    """
    The simplest element. Contains an ID, and some attributes.

    :ivar id: The unique identifier of the element. 
    If id is VIRTUAL_ID_PLACEHOLDER, then the 
    element is not in the actual graph and only exists clienside.
    """

    id: int

    def __init__(self, id: int):
        """
        Initialize the Element.

        :param id: ID of the element.
        :type id: int
        """

        self.set_id(id)


    def set_id(self, id: int):
        """Set the ID of the element.

        NOTE: This function need not exist.

        :param id: What to set the identifier to.
        :type id: int
        """

        self.id = id

    
    def added_to_db(self) -> bool:
        """Return whether this element is added to the database,
        that is, whether the ID is not the virtual ID placeholder.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        # TODO: do an actual query to determine whether this is added to DB.

        return self.id != VIRTUAL_ID_PLACEHOLDER


class Vertex(Element):
    """
    The representation of a vertex. Can contain attributes.

    :ivar category: The category of the Vertex.
    """

    category: str


    def __init__(self, id: int, category: str):
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

        self.category = category

    
    def add(self, attributes: dict):
        """
        Add the vertex of category self.category
        to the JanusGraph DB along with attributes from :param attributes:.

        :param attributes: A dictionary of attributes to attach to the vertex.
        :type attributes: dict
        """

        if not self.added_to_db():

            traversal = g.addV().property('category', self.category)

            for key in attributes:
                traversal = traversal.property(key, attributes[key])

            v = traversal.next()

            self.set_id(v.id)

            Vertex._cache_vertex(self)


    def _in_vertex_cache(self) -> bool:
        """Return whether this vertex ID is in the vertex cache.

        :return: True if vertex ID is in _vertex_cache, false otherwise.
        :rtype: bool
        """

        return self.id in _vertex_cache


    @classmethod
    def _cache_vertex(cls, vertex):
        """Add a vertex and its ID to the vertex cache if not already added,
        and return this new cached vertex. 

        TODO: Raise an error if already cached, because that'd mean there's
        an implementation error with the caching.
        """

        if not vertex.added_to_db():
                
            # Do nothing?
                
            return

        if vertex.id not in _vertex_cache:

            _vertex_cache[vertex.id] = vertex

        return _vertex_cache[vertex.id]




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
        self, id: int, inVertex: Vertex, 
        outVertex: Vertex, category: str
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

        self.category = category

    
    def add(self, attributes: dict):
        """Add an edge between two vertices in JanusGraph.

        :param attributes: Attributes to add to the edge. Must have string
        keys and corresponding values.
        :type attributes: dict
        """

        if self.inVertex.added_to_db() and self.outVertex.added_to_db():

            traversal = g.V(self.outVertex.id).addE(self.category) \
                        .to(__.V(self.inVertex.id)) \
                        .property('category', self.category)

            for key in attributes:
                traversal = traversal.property(key, attributes[key])

            e = traversal.next()

            self.id = e.id


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

    def __init__(
        self, name: str, comments: str="", id: int=VIRTUAL_ID_PLACEHOLDER
    ):
        """
        Initialize the ComponentType vertex with a category, name,
        and comments for self.attributes.

        :param name: The name of the component type. 
        :type name: str

        :param comments: The comments attached to the component type. 
        :str comments: str  
        """

        self.name = name

        self.comments = comments

        Vertex.__init__(self, id=id, 
            category="component_type")

    def add(self):
        """Add this ComponentType vertex to the serverside.
        """

        attributes = {
            'name': self.name,
            'comments': self.comments
        }

        Vertex.add(self=self, attributes=attributes)

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

        d =  g.V().has('category', 'component_type').has('name', name) \
            .as_('v').valueMap().as_('props').select('v').id().as_('id') \
            .select('props', 'id').next()
        
        props, id = d['props'], d['id']



        if id not in _vertex_cache:

            Vertex._cache_vertex(
                ComponentType(
                    name=name, 
                    comments=props['comments'][0], 
                    id=id
                )
            )


        return _vertex_cache[id]

    @classmethod
    def from_id(cls, id: int):
        """Query te database and return a ComponentType instance based on
        the ID.

        :param id: The serverside ID of the ComponentType vertex.
        :type id: int
        :return: Return a ComponentType from that ID.
        :rtype: ComponentType
        """

        if id not in _vertex_cache:

            d = g.V(id).valueMap().next()

            _vertex_cache[id] = ComponentType(
                name=d['name'][0], 
                comments=d['comments'][0], 
                id=id
            )

        return _vertex_cache[id]
    

class ComponentRevision(Vertex):
    """
    The representation of a component revision.

    :ivar comments: The comments associated with the component type.
    :ivar name: The name of the component type.
    :ivar allowed_type: The ComponentType instance representing the allowed
    type of the component revision.
    """

    comments: str
    name: str
    allowed_type: ComponentType

    def __init__(
        self, name: str, comments: str, allowed_type: ComponentType,
        id: int=VIRTUAL_ID_PLACEHOLDER
        ):
        """
        Initialize the ComponentRevision vertex.

        :param name: The name of the component revision. 
        :param comments: The comments attached to the component revision.    
        :param allowed_type: The ComponentType instance representing the 
        allowed component type of the revision.
        """

        self.name = name
        self.comments = comments
        self.allowed_type = allowed_type

        Vertex.__init__(self, id=id, 
            category="component_revision")

    def add(self):
        """Add this ComponentType vertex to the serverside.
        """

        attributes = {
            'name': self.name,
            'comments': self.comments
        }

        Vertex.add(self=self, attributes=attributes)     

        if not self.allowed_type.added_to_db():
            self.allowed_type.add()

        e = ConnectionRevisionAllowedType(
                inVertex=self.allowed_type, 
                outVertex=self
            )

        e.add()

    @classmethod
    def from_db(cls, name: str, allowed_type: ComponentType):
        """Query the database and return a ComponentRevision instance based on
        component revision of name :param name: connected to component type
        :param allowed_type:.

        :param name: The name of the component type.
        :type name: str
        :param allowed_type: The ComponentType instance that this component
        revision is to be connected to.
        :type allowed_type: ComponentType
        :return: A ComponentRevision instance with the correct name, comments, 
        allowed component type, and ID.
        :rtype: ComponentRevision
        """

        if allowed_type.added_to_db():

            d =  g.V(allowed_type.id) \
                .both("cxn_revision_allowed_type").has('name', name) \
                .as_('v').valueMap().as_('attrs').select('v').id().as_('id') \
                .select('attrs', 'id').next()
            
            props, id = d['props'], d['id']

            if id not in _vertex_cache:

                Vertex._cache_vertex(
                    ComponentRevision(
                        name=name, 
                        comments=props['comments'][0], 
                        allowed_type=allowed_type,
                        id=id
                    )
                )

            return _vertex_cache[id]

        else:
            # TODO: RAISE CUSTOM ERROR!

            raise Error

    @classmethod
    def from_id(cls, id: int):
        """Query te database and return a ComponentRevision instance based on
        the ID.

        :param id: The serverside ID of the ComponentRevision vertex.
        :type id: int
        :return: Return a ComponentRevision from that ID.
        :rtype: ComponentRevision
        """

        if id not in _vertex_cache:

            d = g.V(id).project('attrs', 'type_id').by(__.valueMap()) \
                .by(__.id()).next()

            t = ComponentType.from_id(d['type_id'])

            _vertex_cache[id] = ComponentRevision(
                name=d['attrs']['name'][0], 
                comments=d['attrs']['comments'][0], 
                allowed_type=t,
                id=id
            )

        return _vertex_cache[id]


class Component(Vertex):
    """
    The representation of a component. 
    Contains a name attribute, ComponentType instance and can contain a
    ComponentRevision.

    :ivar name: The name of the component
    :ivar component_type: The ComponentType instance representing the 
    type of the component.
    :ivar revision: Optional ComponentRevision instance representing the
    revision of the component.

    # TODO: Figure out how to represent properties along with timestamps.
    """

    name: str
    component_type: ComponentType
    revision: ComponentRevision = None

    def __init__(
        self, name: str, component_type: ComponentType, 
        revision: ComponentRevision=None,
        id: int=VIRTUAL_ID_PLACEHOLDER
        ):
        """
        Initialize the ComponentRevision vertex.

        :param name: The name of the component revision. 
        :param type: A ComponentType instance representing the type of the
        component.
        :param revision: A ComponentRevision instance representing the 
        revision of the component, optional.
        """

        self.name = name
        self.component_type = component_type
        self.revision = revision

        # TODO: component name needs to be unique.

        Vertex.__init__(self, id=id, category="component")


    def add(self):

        attributes = {
            'name': self.name
        }

        Vertex.add(self, attributes)

        if self.revision is not None:
            if not self.revision.added_to_db():
                self.revision.add()

            rev_edge = ConnectionRevision(
                inVertex=self.revision,
                outVertex=self
            )

            rev_edge.add()

        if not self.component_type.added_to_db():
            self.component_type.add()

        type_edge = ConnectionComponentType(
            inVertex=self.component_type,
            outVertex=self
        )

        type_edge.add()

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a Component instance based on
        name :param name:.

        :param name: The name attribute of the component serverside.
        :type name: str
        """

        d = g.V().has('category', 'component').has('name', name) \
            .project('id', 'type_id', 'rev_ids') \
            .by(__.id()).by(__.both('cxn_component_type').id()) \
            .by(__.both('cxn_revision').id().fold()).next()

        id, type_id, rev_ids = d['id'], d['type_id'], d['rev_ids']

        if type_id not in _vertex_cache:
            Vertex._cache_vertex(ComponentType.from_id(type_id))

        crev = None

        if len(rev_ids) > 1:

            # raise an error because THIS SHOULD NOT HAPPEN!!!
            raise ValueError

        if len(rev_ids) == 1:
            crev = Vertex._cache_vertex(
                ComponentRevision.from_id(id=rev_ids[0])
            )

        if id not in _vertex_cache:
            Vertex._cache_vertex(
                Component(
                    name=name,  
                    id=id,
                    component_type=_vertex_cache[type_id],
                    revision=crev
                )
            )

        return _vertex_cache[id]


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

    name: str
    units: str
    allowed_regex: str
    n_values: int
    comments: str
    allowed_types: List[ComponentType]

    def __init__(
        self, name: str, units: str, allowed_regex: str,
        n_values: int, comments: str, allowed_types: List[ComponentType],
        id: int=VIRTUAL_ID_PLACEHOLDER
    ):
        self.name = name
        self.units = units
        self.allowed_regex = allowed_regex
        self.n_values = n_values
        self.comments = comments
        self.allowed_types = allowed_types

        Vertex.__init__(self, id=id, category="property_type")


class Property(Vertex):
    """The representation of a property.
    
    :ivar values: The values contained within the property.
    :ivar property_type: The PropertyType instance representing the property
    type of this property.
    """

    values: List[str]
    property_type: PropertyType

    def __init__(
        self, values: List[str], property_type: PropertyType,
        id: int=VIRTUAL_ID_PLACEHOLDER
    ):

        if len(values) != property_type.n_values:

            # TODO: RAISE A CUSTOM ERROR!

            raise ValueError

        # TODO: Make sure it adheres to the regex.

        self.values = values
        self.property_type = property_type

        Vertex.__init__(self, id=id, category="property")


class FlagType(Vertex):
    """The representation of a flag type. 

    :ivar name: The name of the flag type.
    :ivar comments: Comments about the flag type.
    """

    name: str
    comments: str

    def __init__(
        self, name: str, comments: str, id: int=VIRTUAL_ID_PLACEHOLDER
    ):
        self.name = name
        self.comments = comments

        Vertex.__init__(self, id=id, category="flag_type")


class Flag(Vertex):
    """
    The representation of a flag.

    :ivar name: The name of the flag.
    :ivar start_time: The start time of the flag.
    :ivar end_time: The end time of the flag.
    :ivar severity: The severity of the flag.
    :ivar comments: The comments relating to the flag.
    :ivar flag_type: The FlagType instance representing the type of the flag.
    :ivar flag_components: A list of Component instances related to the flag.
    """

    name: str
    start_time: int
    end_time: int
    severity: int
    comments: str
    flag_type: FlagType
    flag_components: List[Component]

    def __init__(
        self, name: str, start_time: int, end_time: int,
        severity: int, comments: str, flag_type: FlagType,
        flag_components: List[Component]=[],
        id: int=VIRTUAL_ID_PLACEHOLDER
    ):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.severity = severity
        self.comments = comments
        self.flag_type = flag_type
        self.flag_components = flag_components

        Vertex.__init__(self=self, id=id, category="flag")


###############################################################################
#                                   EDGES                                     #
###############################################################################


class ConnectionComponent(Edge):
    """Representation of a "cxn_component" edge.

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

    start_time: float
    end_time: float
    start_uid: str
    end_uid: str
    start_edit_time: float
    end_edit_time: float
    start_comments: str
    end_comments: str
    permanent: bool

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex, start_time: float, 
        start_uid: str, start_edit_time: float, start_comments: str="",
        end_time: float=EXISTING_CONNECTION_END_PLACEHOLDER, end_uid: str="", 
        end_edit_time: float=EXISTING_CONNECTION_END_EDIT_PLACEHOLDER, 
        end_comments: str="", permanent: bool=False,
        id: int=VIRTUAL_ID_PLACEHOLDER
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

        self.permanent = permanent

        if permanent:
            self.end_time = EXISTING_CONNECTION_END_PLACEHOLDER
            self.end_uid = ""
            self.end_edit_time = EXISTING_CONNECTION_END_EDIT_PLACEHOLDER
            self.end_comments = ""

        else:
            self.end_time = end_time
            self.end_uid = end_uid
            self.end_edit_time = end_edit_time
            self.end_comments = end_comments
        

        Edge.__init__(self=self, id=id, inVertex=inVertex, outVertex=outVertex,
        category="cxn_component")


    def end_connection(
        self, end_time: float, 
        end_uid: str, end_edit_time: float, end_comments: str=""
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
        self.end_time = end_time
        self.end_uid = end_uid
        self.end_edit_time = end_edit_time
        self.end_comments = end_comments


class ConnectionProperty(Edge):
    """Representation of a "cxn_property" edge.

    :ivar start_time: The start time of the connection.
    :ivar end_time: The end time of the connection. 
    :ivar start_uid: The ID of the user that started the connection.
    :ivar end_uid: The ID of the user that ended the connection.
    :ivar start_edit_time: The time that the connection was started at.
    :ivar end_edit_time: The time that the connection was ended at.
    :ivar start_comments: Comments about starting the connection.
    :ivar end_comments: Comments about ending the connection.
    """

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
        start_uid: str, start_edit_time: float, start_comments: str="",
        end_time: float=EXISTING_CONNECTION_END_PLACEHOLDER, end_uid: str="", 
        end_edit_time: float=-1, end_comments: str="",
        id: int=VIRTUAL_ID_PLACEHOLDER
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
        defaults to EXISTING_CONNECTION_END_EDIT_PLACEHOLDER
        :type end_edit_time: float, optional
        :param end_comments: Comments regarding the ending of 
        the connection, defaults to ""
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
        outVertex=outVertex, category="cxn_property")


    def end_connection(
        self, end_time: float, 
        end_uid: str, end_edit_time: float, end_comments: str=""
    ):
        """End the connection.

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
        self.end_time = end_time
        self.end_uid = end_uid
        self.end_edit_time = end_edit_time
        self.end_comments = end_comments


class ConnectionRevision(Edge):
    """
    Representation of a "cxn_revision" edge.
    """ 

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int=VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(self=self, id=id,
        inVertex=inVertex, outVertex=outVertex, category="cxn_revision")

    def add(self):
        """Add this connection to the serverside.
        """

        Edge.add(self, attributes={})


class ConnectionRevisionAllowedType(Edge):
    """
    Representation of a "cxn_revision_allowed_type" edge.
    """ 

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int=VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(self=self, id=id,
            inVertex=inVertex, outVertex=outVertex, 
            category="cxn_revision_allowed_type"
        )

    def add(self):
        """Add this connection to the serverside.
        """

        Edge.add(self, attributes={})


class ConnectionComponentType(Edge):
    """
    Representation of a "cxn_component_type" edge.
    """ 

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex, 
        id: int=VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(self=self, id=id,
        inVertex=inVertex, outVertex=outVertex, category="cxn_component_type")

    def add(self):
        """Add this connection to the serverside.
        """

        Edge.add(self, attributes={})


class ConnectionPropertyType(Edge):
    """
    Representation of a "cxn_property_type" edge.
    """ 

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int=VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex, category="cxn_property_type"
        )


class ConnectionPropertyAllowedType(Edge):
    """
    Representation of a "cxn_property_allowed_type" edge.
    """ 

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int=VIRTUAL_ID_PLACEHOLDER
    ):
        super.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex, 
            category="cxn_property_allowed_type"
        )



class ConnectionFlagComponent(Edge):
    """
    Representation of a "cxn_flag_component" edge.
    """ 

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex, 
        id: int=VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex, 
            category="cxn_flag_component"
        )


class ConnectionFlagType(Edge):
    """
    Representation of a "cxn_flag_type" edge.
    """ 

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex, 
        id: int=VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex, category="cxn_flag_type"
        )