"""
edges.py

Defines all the edge types used by Padloper.
"""
import _global as g
from _base import TimestampedEdge, Edge, Vertex

class RelationConnection(TimestampedEdge):
    """Representation of a "rel_connection" edge.
    """
    category: str = "rel_connection"

class RelationProperty(TimestampedEdge):
    """Representation of a "rel_property" edge.
    """
    category: str = "rel_property"

class RelationVersion(Edge):
    """
    Representation of a "rel_version" edge.
    """

    category: str = "rel_version"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(self=self, id=id,
                      inVertex=inVertex, outVertex=outVertex)

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationVersionAllowedType(Edge):
    """
    Representation of a "rel_version_allowed_type" edge.
    """

    category: str = "rel_version_allowed_type"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(self=self, id=id,
                      inVertex=inVertex, outVertex=outVertex,
                      )

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationComponentType(Edge):
    """
    Representation of a "rel_component_type" edge.
    """

    category: str = "rel_component_type"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(self=self, id=id,
                      inVertex=inVertex, outVertex=outVertex)

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationSubcomponent(Edge):
    """
    Representation of a "rel_subcomponent" edge.
    """

    category: str = "rel_subcomponent"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(self=self, id=id,
                      inVertex=inVertex, outVertex=outVertex)

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationPropertyType(Edge):
    """
    Representation of a "rel_property_type" edge.
    """

    category: str = "rel_property_type"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationPropertyAllowedType(Edge):
    """
    Representation of a "rel_property_allowed_type" edge.
    """

    category: str = "rel_property_allowed_type"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationFlagComponent(Edge):
    """
    Representation of a "rel_flag_component" edge.
    """

    category: str = "rel_flag_component"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside."""

        Edge.add(self, attributes={})


class RelationFlagType(Edge):
    """
    Representation of a "rel_flag_type" edge.
    """

    category: str = "rel_flag_type"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside."""

        Edge.add(self, attributes={})


class RelationFlagSeverity(Edge):
    """
    Representation of a "rel_flag_severity" edge.
    """

    category: str = "rel_flag_severity"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside."""

        Edge.add(self, attributes={})

class RelationUserGroup(Edge):
    """
    Representation of a "rel_user_group" edge
    """

    category: str = "rel_user_group"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(self=self, id=id,
                      inVertex=inVertex, outVertex=outVertex)
    
    def _add(self):
        """Add this relation to the serverside
        """
        Edge.add(self, attributes={})


class RelationUserAllowedGroup(Edge):
    """
    Representation of a "rel_user_group" edge.
    """

    category: str = "rel_user_group"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})


class RelationGroupAllowedPermission(Edge):
    """
    Representation of a "rel_group_permission" edge.
    """

    category: str = "rel_group_permission"

    def __init__(
        self, inVertex: Vertex, outVertex: Vertex,
        id: int = g._VIRTUAL_ID_PLACEHOLDER
    ):
        Edge.__init__(
            self=self, id=id,
            inVertex=inVertex, outVertex=outVertex
        )

    def add(self):
        """Add this relation to the serverside.
        """

        Edge.add(self, attributes={})
