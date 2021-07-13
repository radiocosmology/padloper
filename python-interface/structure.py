"""
structure.py

Contains methods for storing clientside interface information.

"""

from typing import Optional, List

# A placeholder value for the end_time attribute for a 
# connection that is still ongoing.
EXISTING_CONNECTION_END_PLACEHOLDER = 2**63 - 1
EXISTING_CONNECTION_END_EDIT_PLACEHOLDER = -1

# 
VIRTUAL_ID_PLACEHOLDER = -1

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


class Node(Element):
    """
    The representation of a node. Can contain attributes.

    :ivar category: The category of the Node.
    """

    category: str

    edges: list

    def __init__(self, id: int, category: str, edges: list=[]):
        """
        Initialize the Node.

        :param id: ID of the Node.
        :type id: int

        :param category: The category of the Node.
        :type category: str

        :param edges: The list of Edge instances that are connected to the Node.
        :type edges: List[Edge]
        """

        Element.__init__(self, id)

        self.category = category

        self.edges = edges

    def add_edge(self, edge):
        """Add an edge to self.edges

        :param edge: An Edge instance 
        :type edge: Edge
        """

        self.edges.append(edge)


class Edge(Element):
    """
    The representation of an edge connecting two Node instances.

    :ivar inNode: The Node instance that the Edge is going into.
    :ivar outNode: The Node instance that the Edge is going out of.
    :ivar category: The category of the Edge.
    """

    inNode: Node
    outNode: Node

    category: str

    def __init__(self, id: int, inNode: Node, outNode: Node, category: str):
        """
        Initialize the Edge.

        :param id: ID of the Edge.
        :type id: int

        :param inNode: A Node instance that the Edge will go into.
        :type inNode: Node

        :param outNode: A Node instance that the Edge will go out of.
        :type outNote: Node

        :param outNode: A Node instance that the Edge will go out of.
        :type outNote: Node

        :param category: The category of the Edge
        :type category: str
        """

        Element.__init__(self, id)

        self.inNode = inNode
        self.outNode = outNode

        self.category = category


###############################################################################
#                                   NODES                                     #
###############################################################################

class ComponentType(Node):
    """
    The representation of a component type.

    :ivar comments: The comments associated with the component type.
    :ivar name: The name of the component type.
    """

    comments: str
    name: str

    def __init__(self, name: str, comments: str):
        """
        Initialize the ComponentType node with a category, name,
        and comments for self.attributes.

        :param name: The name of the component type. 
        :type name: str

        :param comments: The comments attached to the component type. 
        :str comments: str  
        """

        self.name = name

        self.comments = comments

        Node.__init__(self, id=VIRTUAL_ID_PLACEHOLDER, 
            category="component_type")


class ComponentRevision(Node):
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

    def __init__(self, name: str, comments: str, allowed_type: ComponentType):
        """
        Initialize the ComponentRevision node.

        :param name: The name of the component revision. 
        :param comments: The comments attached to the component revision.    
        :param allowed_type: The ComponentType instance representing the 
        allowed component type of the revision.
        """

        self.name = name
        self.comments = comments
        self.allowed_type = allowed_type

        Node.__init__(self, id=VIRTUAL_ID_PLACEHOLDER, 
            category="component_revision")


class Component(Node):
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
        revision: ComponentRevision=None):
        """
        Initialize the ComponentRevision node.

        :param name: The name of the component revision. 
        :param type: A ComponentType instance representing the type of the
        component.
        :param revision: A ComponentRevision instance representing the 
        revision of the component, optional.
        """

        self.name = name
        self.component_type = component_type
        self.revision = revision

        Node.__init__(self, id=VIRTUAL_ID_PLACEHOLDER, category="component")


class PropertyType(Node):
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
    :ivar allowed_type: The allowed component type of the property type Node,
    as a ComponentType attribute.
    """

    name: str
    units: str
    allowed_regex: str
    n_values: int
    comments: str
    allowed_type: ComponentType

    def __init__(
        self, name: str, units: str, allowed_regex: str,
        n_values: int, comments: str, allowed_type: ComponentType
    ):
        self.name = name
        self.units = units
        self.allowed_regex = allowed_regex
        self.n_values = n_values
        self.comments = comments
        self.allowed_type = allowed_type

        Node.__init__(self, id=VIRTUAL_ID_PLACEHOLDER, category="property_type")


class Property(Node):
    """The representation of a property.
    
    :ivar values: The values contained within the property.
    :ivar property_type: The PropertyType instance representing the property
    type of this property.
    """

    values: List[str]
    property_type: PropertyType

    def __init__(
        self, values: List[str], property_type: PropertyType
    ):

        if len(values) != property_type.n_values:

            # TODO: RAISE A CUSTOM ERROR!

            raise ValueError

        self.values = values
        self.property_type = property_type

        Node.__init__(self, id=VIRTUAL_ID_PLACEHOLDER, 
            category="property")


class FlagType(Node):
    """The representation of a flag type. 

    :ivar name: The name of the flag type.
    :ivar comments: Comments about the flag type.
    """

    name: str
    comments: str

    def __init__(self, name: str, comments: str):
        self.name = name
        self.comments = comments

        Node.__init__(self, id=VIRTUAL_ID_PLACEHOLDER, category="flag_type")


class Flag(Node):
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
        flag_components: List[Component]=[]
    ):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.severity = severity
        self.comments = comments
        self.flag_type = flag_type
        self.flag_components = flag_components

        Node.__init__(self=self, id=VIRTUAL_ID_PLACEHOLDER, category="flag")


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
        self, inNode: Node, outNode: Node, start_time: float, start_uid: str,
        start_edit_time: float, start_comments: str="",
        end_time: float=EXISTING_CONNECTION_END_PLACEHOLDER, end_uid: str="", 
        end_edit_time: float=EXISTING_CONNECTION_END_EDIT_PLACEHOLDER, 
        end_comments: str="", permanent: bool=False
    ):
        """Initialize the connection.

        :param inNode: The Node that the edge is going into.
        :type inNode: Node
        :param outNode: The Node that the edge is going out of.
        :type outNode: Node
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
        

        Edge.__init__(self=self, id=-1, inNode=inNode, outNode=outNode,
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
        self, inNode: Node, outNode: Node, start_time: float, start_uid: str,
        start_edit_time: float, start_comments: str="",
        end_time: float=EXISTING_CONNECTION_END_PLACEHOLDER, end_uid: str="", 
        end_edit_time: float=-1, end_comments: str=""
    ):
        """Initialize the connection.

        :param inNode: The Node that the edge is going into.
        :type inNode: Node
        :param outNode: The Node that the edge is going out of.
        :type outNode: Node
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

        Edge.__init__(self=self, id=VIRTUAL_ID_PLACEHOLDER, inNode=inNode, 
        outNode=outNode, category="cxn_property")


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
        self, inNode: Node, outNode: Node
    ):
        Edge.__init__(self=self, id=VIRTUAL_ID_PLACEHOLDER,
        inNode=inNode, outNode=outNode, category="cxn_revision")


class ConnectionRevisionAllowedType(Edge):
    """
    Representation of a "cxn_revision_allowed_type" edge.
    """ 

    def __init__(
        self, inNode: Node, outNode: Node
    ):
        Edge.__init__(self=self, id=VIRTUAL_ID_PLACEHOLDER,
        inNode=inNode, outNode=outNode, category="cxn_revision_allowed_type")


class ConnectionComponentType(Edge):
    """
    Representation of a "cxn_component_type" edge.
    """ 

    def __init__(
        self, inNode: Node, outNode: Node
    ):
        Edge.__init__(self=self, id=VIRTUAL_ID_PLACEHOLDER,
        inNode=inNode, outNode=outNode, category="cxn_component_type")


class ConnectionPropertyType(Edge):
    """
    Representation of a "cxn_property_type" edge.
    """ 

    def __init__(
        self, inNode: Node, outNode: Node
    ):
        Edge.__init__(
            self=self, id=VIRTUAL_ID_PLACEHOLDER,
            inNode=inNode, outNode=outNode, category="cxn_property_type"
        )


class ConnectionPropertyAllowedType(Edge):
    """
    Representation of a "cxn_property_allowed_type" edge.
    """ 

    def __init__(
        self, inNode: Node, outNode: Node
    ):
        Edge.__init__(
            self=self, id=VIRTUAL_ID_PLACEHOLDER,
            inNode=inNode, outNode=outNode, category="cxn_property_allowed_type"
        )


class ConnectionFlagComponent(Edge):
    """
    Representation of a "cxn_flag_component" edge.
    """ 

    def __init__(
        self, inNode: Node, outNode: Node
    ):
        Edge.__init__(
            self=self, id=VIRTUAL_ID_PLACEHOLDER,
            inNode=inNode, outNode=outNode, category="cxn_flag_component"
        )


class ConnectionFlagType(Edge):
    """
    Representation of a "cxn_flag_type" edge.
    """ 

    def __init__(
        self, inNode: Node, outNode: Node
    ):
        Edge.__init__(
            self=self, id=VIRTUAL_ID_PLACEHOLDER,
            inNode=inNode, outNode=outNode, category="cxn_flag_type"
        )