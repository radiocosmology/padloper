"""
_component_nodes.py

Classes for manipulating components, component types and component versions.
"""
import time
import _global as g
from gremlin_python.process.traversal import Order, P, TextP
from gremlin_python.process.graph_traversal import __, constant

from _exceptions import *
from _base import strictraise, Edge, Timestamp, Vertex, VertexAttr,\
                  _parse_time
from _edges import RelationVersionAllowedType, RelationVersion,\
                   RelationComponentType, RelationSubcomponent,\
                   RelationProperty, RelationPropertyType,\
                   RelationFlagComponent, RelationConnection
from _permissions import Permission, check_permission
from padloper.method_decorators import authenticated

class ComponentType(Vertex):
    """
    The representation of a component type.

    :ivar comments: The comments associated with the component type.
    :ivar name: The name of the component type.
    """

    category: str = "component_type"
    _vertex_attrs: list = [
        VertexAttr("name", str), 
        VertexAttr("comments", str, optional=True, default="")
    ]
    primary_attr: str = "name"

    @classmethod
    def get_names_of_types_and_versions(cls, permissions = None):
        """
        Return a list of dictionaries, of the format
        {'type': <ctypename>, 'versions': [<revname>, ..., <revname>]}

        where <ctypename> is the name of the component type, and
        the corresponding value of the 'versions' key is a list of the names
        of all of the versions.

        Used for updating the filter panels.

        :return: a list of dictionaries, of the format
        {'type': <ctypename>, 'versions': [<revname>, ..., <revname>]}
        :rtype: list[dict]
        """

        ts = g.t.V().has('active', True)\
                .has('category', ComponentType.category) \
                .order().by('name', Order.asc) \
                .project('name', 'versions') \
                .by(__.values('name')) \
                .by(__.both(RelationVersionAllowedType.category) \
                      .has("active", True) \
                      .order().by('name', Order.asc).values('name').fold()
                ).toList()

        return ts

    def __repr__(self):
        return f"{self.category}: {self.name} ({self._id})"


class ComponentVersion(Vertex):
    """
    The representation of a component version.

    :ivar comments: The comments associated with the component type.
    :ivar name: The name of the component type.
    :ivar type: The ComponentType instance representing the allowed
    type of the component version.
    """

    category: str = "component_version"

    _vertex_attrs: list = [
        VertexAttr("name", str), 
        VertexAttr("comments", str, optional=True, default=""),
        VertexAttr("type", ComponentType, edge_class=RelationVersionAllowedType)
    ]
    primary_attr: str = "name"

    def __repr__(self):
        return f"{self.category}: {self.name}"


class Component(Vertex):
    """
    The representation of a component. 
    Contains a name attribute, ComponentType instance, can contain a
    ComponentVersion and can contain a Flag

    :ivar name: The name of the component
    :ivar type: The ComponentType instance representing the 
    type of the component.
    :ivar version: Optional ComponentVersion instance representing the
    version of the component.

    """

    category: str = "component"
    _vertex_attrs: list = [
        VertexAttr("name", str), 
        VertexAttr("type", ComponentType, edge_class=RelationComponentType),
        VertexAttr("version", ComponentVersion, edge_class=RelationVersion,
                   optional=True)
    ]
    primary_attr: str = "name"

    def __str__(self):

        if self.version is None:
            version_text = "no version"

        else:
            version_text = 'version "{self.version.name}"'

        return f'Component of name "{self.name}", \
            type "{self.type.name}", \
            {version_text}, id {self.id()}'

    def get_property(self, type, at_time: int, permissions = None):
        """
        Given a property type, get a property of this component active at time
        :param time:. 

        :param type: The type of the property to extract
        :type type: PropertyType
        :param at_time: The time to check the active property at.
        :type at_time: int

        :rtype: Property or None
        """
        from _property_nodes import Property

        if not self.in_db(strict_check=False, permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not type.in_db(strict_check=False, permissions=permissions):
            raise PropertyTypeNotAddedError(
                f"Property type {type.name} of component " +
                 "{self.name} " +
                "has not yet been added to the database."
            )

        # list of property vertices of this property type
        # and active at this time
        vs = g.t.V(self.id()).bothE(RelationProperty.category) \
                .has('active', True) \
                .has('start_time', P.lte(at_time)) \
                .has('end_time', P.gt(at_time)).otherV().as_('v') \
                .both(RelationPropertyType.category) \
                .has('name', type.name) \
                .select('v').toList()

        # If no such vertices found
        if len(vs) == 0:
            return None

        # There should be only one!

        assert len(vs) == 1

        return Property.from_id(vs[0].id)

    @authenticated
    def get_all_properties(self, permissions = None):
        """Return all properties, along with their edges of this component as
        a tuple of the form (Property, RelationProperty)

        :rtype: tuple[Property, RelationProperty]
        """
        from _property_nodes import Property

        if not self.in_db(strict_check=False, permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # list of property vertices of this property type
        # and active at this time
        query = g.t.V(self.id()).bothE(RelationProperty.category)\
                   .has('active', True) \
                   .as_('e').valueMap().as_('edge_props') \
                   .select('e').otherV().id_().as_('vertex_id') \
                   .select('edge_props', 'vertex_id').toList()

        # Build up the result of format (property vertex, relation)
        result = []

        for q in query:
            prop = Property.from_id(q['vertex_id'])
            edge = RelationProperty(
                inVertex=prop,
                outVertex=self,
                start=Timestamp._from_dict(q["edge_props"], "start_"),
                end=Timestamp._from_dict(q["edge_props"], "end_"),
            )
            result.append((prop, edge))

        return result

    @authenticated
    def get_all_properties_of_type(
        self, type,
        from_time: int = -1,
        to_time: int = g._TIMESTAMP_NO_ENDTIME_VALUE,
        permissions = None
    ):
        """
        Given a property type, return all edges that connected them between time
        :param from_time: and to time :param to_time: as a list.

        :param type: The property type of the desired properties to consider.
        :type component: PropertyType
        :param from_time: Lower bound for time range to consider properties, 
        defaults to -1
        :type from_time: int, optional
        :param to_time: Upper bound for time range to consider properties, 
        defaults to _TIMESTAMP_NO_ENDTIME_VALUE
        :type to_time: int, optional

        :rtype: list[RelationProperty]
        """

        if not self.in_db(strict_check=False, permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not type.in_db(strict_check=False):
            raise PropertyTypeNotAddedError(
                f"Property type {type.name} of component {self.name} " +
                "has not yet been added to the database."
            )

        edges = g.t.V(self.id()).bothE(RelationProperty.category) \
                   .has('active', True) \
                   .has('end_edit_time', g._TIMESTAMP_NO_EDITTIME_VALUE)

        if to_time < g._TIMESTAMP_NO_ENDTIME_VALUE:
            edges = edges.has('start_time', P.lt(to_time))

        edges = edges.has('end_time', P.gt(from_time)) \
            .as_('e').otherV().as_('v') \
            .both(RelationPropertyType.category) \
            .has('name', type.name) \
            .select('e').order().by(__.values('start_time'), Order.asc) \
            .project('properties', 'id').by(__.valueMap()).by(__.id_()).toList()

        print("Warning: RelationProperty not initialised properly! "\
              "outVertex should not = type but the property vertex …")
        return [RelationProperty(
            inVertex=self, outVertex=type,
            start=Timestamp._from_dict(q["properties"], "start_"),
            end=Timestamp._from_dict(q["properties"], "end_"),
            id=e['id']['@value']['relationId']  # weird but you have to
        ) for e in edges]

    @authenticated
    def get_all_flags(self, permissions = None):
        """Return all flags connected to this component of the form (Flag)

        :rtype: [Flag]
        """

        if not self.in_db(strict_check=False, permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # list of flag vertices of this flag type and flag severity and active at this time.

        query = g.t.V(self.id()).bothE(RelationFlagComponent.category)\
                   .has('active', True).otherV().id_().toList()

        # Build up the result of format (flag vertex)
        result = []

        for q in query:
            flag = Flag.from_id(q)
            result.append((flag))

        return result

    @authenticated
    def get_subcomponents(self, permissions = None):
        """Return all subcomponents connected to this component.

        :rtype: [Component]
        """

        if not self.in_db(strict_check=False, permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        query = g.t.V(self.id()).inE(RelationSubcomponent.category) \
                   .has('active', True).otherV().id_()

        return [Component.from_id(q, permissions=permissions) for q in query.toList()]

    @authenticated
    def get_supercomponents(self, permissions = None):
        """Return all supercomponents connected to this component of the form
        (Component)

        :rtype: [Component]
        """

        if not self.in_db(strict_check=False, permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # Relation as a subcomponent stays the same except now
        # we have outE to distinguish from subcomponents
        query = g.t.V(self.id()).outE(RelationSubcomponent.category) \
                   .has('active', True).otherV().id_()

        return [Component.from_id(q, permissions=permissions) for q in query.toList()]

    @authenticated
    def set_property(
        self, property, start: Timestamp, end: Timestamp = None, 
        force_property: bool = False,
        strict_add: bool = False,
        permissions = None,
    ):
        """
        Given a property :param property:, MAKE A _VIRTUAL COPY of it,
        add it, then connect it to the component self at start time
        :start_time:. Return the Property instance that was added.

        """
        # print('perms: ', permissions)
        from _property_nodes import Property
        # # TODO: check permissions here
        # # test
        # perms = Permission(['set_property', 'edit_component', 'add_component'], "j")
        # permission_group_pass = ['set_property', 'edit_component']
        # permission_group_fail = ['set_property', 'edit_component', 'admin']
        # if not check_permission(perms, permission_group_fail):
        #     raise NoPermissionsError(
        #         "User does not have the required permissions to perform this action."
        #         )
        # print(kwargs['method_name'])
        # print(self.__class__.__name__)

        if not self.in_db(strict_check=False, permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if (self.type not in property.type.allowed_types):
            raise PropertyWrongType(
                f"Property type {property.type.name} is not applicable to "\
                f"component type {self.type.name}."
            )

        current_property = self.get_property(
            type=property.type, at_time=start.time,
            permissions=permissions
        )

        if current_property is not None:
#    TODO: see if behaviour is correct (when this trips in
#            init_simple-db.py).
            if current_property.values == property.values:
                strictraise(strict_add, PropertyIsSameError, 
                    "An identical property of type " +
                    f"{property.type.name} for component {self.name} " +
                    f"is already set with values {property.values}."
                )
                return

#            elif current_property.end.time != g._TIMESTAMP_NO_ENDTIME_VALUE:
#                raise PropertyIsSameError(
#                    "Property of type {property.type.name} for component "\
#                    "{self.name} is already set at this time with an end "\
#                    "time after this time."
#                )
            else:
                # end that property.
                self.unset_property(current_property, start,
                permissions=permissions)

        else:

            existing_properties = self.get_all_properties_of_type(
                type=property.type,
                from_time=start.time,
                permissions=permissions
            )

            if len(existing_properties) > 0:
                if force_property:
                    if end != None:
                        raise ComponentPropertiesOverlappingError(
                            "Trying to set property of type " +
                            f"{property.type.name} for component " +
                            f"{self.name} " +
                            "before an existing property of the same type " +
                            "but with a specified end time; " +
                            "replace the property instead."
                        )

                    else:
                        end = Timestamp(existing_properties[0].start_time,
                                        start.comments)
                else:
                    raise ComponentSetPropertyBeforeExistingPropertyError(
                        "Trying to set property of type " +
                        f"{property.type.name} for component " +
                        f"{self.name} " +
                        "before an existing property of the same type; " +
                        "set 'force_property' parameter to True to bypass."
                    )

        e = RelationProperty(inVertex=property, outVertex=self, start=start,
                             end=end)
        e.add()

        return property #_copy

    @authenticated
    def unset_property(self, property, end: Timestamp, permissions = None):
        """
        Given a property that is connected to this component,
        set the "end" attributes of the edge connecting the component and
        the property to indicate that this property has been removed from the
        component.

        :param property: The property vertex connected by an edge to the 
        component vertex.
        :type property: Property

        :param at_time: The time at which the property was removed (real time). This value has to be provided.
        :type at_time: int

        :param uid: The user that removed the property
        :type uid: str

        :param edit_time: The time at which the 
        user made the change, defaults to int(time.time())
        :type edit_time: int, optional

        :param comments: Comments about the property removal, defaults to ""
        :type comments: str, optional
        """

        if not self.in_db(strict_check=False, permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not property.in_db(strict_check=False, permissions=permissions):
            raise PropertyNotAddedError(
                f"Property of component {self.name} " +
                f"of values {property.values} being unset " +
                "has not been added to the database."
            )

        # Check to see if the property already has an end time.
        vs = g.t.V(self.id()).bothE(RelationProperty.category) \
                .has('active', True) \
                .has('start_time', P.lte(end.time)) \
                .has('end_time', P.gt(end.time)) \
                .as_('e').valueMap().as_('edge_props').select('e') \
                .otherV().as_('v').both(RelationPropertyType.category) \
                .has('name', property.type.name) \
                .select('edge_props').toList()
        if len(vs) == 0:
            raise PropertyNotAddedError(
                f"Property of type {property.type.name} cannot be unset for "\
                f"component {self.name} because it has not been set prior "\
                f"to this time."
            )
        assert(len(vs) == 1)
        if vs[0]['end_time'] < g._TIMESTAMP_NO_ENDTIME_VALUE:
            raise PropertyIsSameError(
                f"Property of type {property.type.name} cannot be unset for "\
                f"component {self.name} because it is set at this time and "\
                f"already has an end time."
            )
#        print("slkdjflskdjfslkdjfslkdfjslkdjf")

        g.t.V(property.id()).bothE(RelationProperty.category).as_('e')\
           .otherV() \
           .hasId(self.id()).select('e') \
           .has('end_time', g._TIMESTAMP_NO_ENDTIME_VALUE) \
           .property('end_time', end.time).property('end_uid', end.uid) \
           .property('end_edit_time', end.edit_time) \
           .property('end_comments', end.comments).iterate()

    @authenticated
    def replace_property(self, propertyTypeName: str, property, at_time: int,
                         uid: str, start: Timestamp, comments="", permissions = None):
        """Replaces the Component property vertex in the serverside.

        :param propertyTypeName: The name of the property type being replaced.
        :type propertyTypeName: str

        :param property: The new property that is replacing the old property.
        :type property: Property

        :param at_time: The time at which the property was added (real time)
        :type at_time: int

        :param uid: The ID of the user that added the property
        :type uid: str

        :param comments: Comments to add with property change, defaults to ""
        :type comments: str, optional

        :param disable_time: When this vertex was disabled in the database
          (UNIX time).
        :type disable_time: int
        """
        from _property_nodes import Property

        # id of the property being replaced.
        print("This method needs to be updated to use the Timestamp class.")
        id = g.t.V(self.id()).bothE(RelationProperty.category)\
                .has('active', True)\
                .has('end_edit_time', g._TIMESTAMP_NO_EDITTIME_VALUE)\
                .otherV().where(\
                  __.outE().otherV().properties('name').value()\
                  .is_(propertyTypeName)\
                ).id_().next()

        property_vertex = Property.from_id(id)

        property_vertex.disable()

        # Sets a new property
        self.set_property(
            property=property,
            start=start,
            permissions=permissions
        )

    @authenticated
    def disable_property(self, propertyTypeName,
                         disable_time: int = int(time.time()),                         
                         permissions = None):
        """Disables the property in the serverside

        :param propertyTypeName: The name of the property type being replaced.
        :type propertyTypeName: str

        :param disable_time: When this vertex was disabled in the database
            (UNIX time).
        :type disable_time: int

        """

        g.t.V(self.id()).bothE(RelationProperty.category)\
           .has('active', True)\
           .has('end_edit_time', g._TIMESTAMP_NO_EDITTIME_VALUE)\
           .where(__.otherV().bothE(RelationPropertyType.category).otherV()\
           .properties('name').value().is_(propertyTypeName))\
           .property('active', False).property('time_disabled', disable_time)\
           .next()

    @authenticated
    def connect(
        self, comp, start: Timestamp, end: Timestamp = None,
        strict_add: bool = True, is_replacement: bool = False,
        permissions = None
    ):
        """Given another Component :param comp:,
        connect the two components.

        :param comp: Another component to connect this component to.
        :type comp: Component
        :param start: The starting timestamp for the connection.
        :type start: Timestamp
        :param end: The ending timestamp for the connection; if omitted, the
           connection is into the indefinite future.
        :type end: Timestamp or None
        :param strict_add: If connexion already exists, raise an error if True;
          otherwise print a warning and return.
        :type strict_add: bool
        :param is_replacement: Disable current connexion and replace it with
           this one.
        :type is_replacement: bool
        """

        if is_replacement:
            raise RuntimeError(f"Is_replacement feature not implemented yet. {is_replacement}")

        if not self.in_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not comp.in_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {comp.name} has not yet " +
                "been added to the database."
            )

        if self.name == comp.name:
            raise ComponentConnectToSelfError(
                f"Trying to connect component {self.name} to itself."
            )

        curr_conn = self.get_connections(comp=comp,
                                         at_time=start.time,
                                         permissions=permissions)
        # If this doesn't pass, something is very broken!
        assert(len(curr_conn) <= 1)

        if len(curr_conn) == 1 and is_replacement == False:
            # Already connected!
            strictraise(strict_add, ComponentsAlreadyConnectedError, 
                f"Components {self.name} and {comp.name} " +
                "are already connected."
            )
            return
        elif len(curr_conn) == 0 and is_replacement == True:
            # Not connected, but expected them to be connected.
            strictraise(strict_add, ComponentsAlreadyConnectedError,
                f"Trying to replace connection between {self.name} and " +
                "{comp.name}, but it does not exist."
            )
            return

        all_conn = self.get_connections(comp=comp,
                                        from_time=start.time,
                                        permissions=permissions)

        if len(all_conn) > 0:
            if end == None:
                raise ComponentsOverlappingConnectionError(
                    "Trying to connect components " +
                    f"{self.name} and {comp.name} " +
                    "before an existing connection but without a " +
                    "specified end time. Specify an end time or " +
                    "replace the connection instead."
                    )
            elif end.time >= all_conn[0].start.time:
                raise ComponentsOverlappingConnectionError(
                    "Trying to connect components " +
                    f"{self.name} and {comp.name} " +
                    "but existing connection between these components " +
                    "overlaps in time."
                )

        if is_replacement:
            raise RuntimeError(f"Is_replacement feature not implemented yet. {is_replacement}")

        curr_conn = RelationConnection(
            inVertex=self,
            outVertex=comp,
            start=start,
            end=end
        )

        curr_conn.add()
#        print(f'connected: {self} -> {comp}  ({start.uid} {start.time})')

    @authenticated
    def disconnect(self, comp, end, permissions = None):
        """Given another Component :param component:, disconnect the two
        components at time :param time:.

        :param comp: Another Component to disconnect this component from.
        :type comp: Component
        :param end: The starting timestamp for the connection.
        :type end: Timestamp
        """

        # Done for troubleshooting (so you know which component is not added?)
        if not self.in_db(strict_check=False, permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not comp.in_db(strict_check=False, permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {comp.name} has not yet " +
                "been added to the database."
            )

        curr_conn = self.get_connections(comp=comp,
                                         at_time = end.time,
                                         permissions=permissions)
        assert(len(curr_conn) <= 1)

        if len(curr_conn) == 0:
            # Not connected yet!
            raise ComponentsAlreadyDisconnectedError(
                f"Components {self.name} and {comp.name} " +
                "are already disconnected at this time."
            )

        else:
            curr_conn[0]._end(end)

    @authenticated
    def disable_connection(self, comp, disable_time: int = int(time.time()),
                           permissions = None):
        """Disables the connection in the serverside

        :param comp: Component that this component has connection with.
        :type comp: Component
        :param disable_time: When this edge was disabled in the database.
        :type disable_time: int    
        """
        raise RuntimeError("Deprecated!")

    @authenticated
    def get_connections(self, comp = None, at_time = None,
                        from_time = None, to_time = None,
                        exclude_subcomponents: bool = False,
                        permissions = None):
        """
        Get connections to another component, or all other components, at a
        time, at all times or in a time range, depending on the parameters.

        :param comp: The other component(s) to check the connections with; 
            if None then find connections with all other components.
        :type comp: Component or list of Components, optional
        :param at_time: Time to check connections at. If this parameter is set,
            then :from_time: and :to_time: are ignored.
        :type at_time: int, optional
        :param from_time: Lower bound for time range to consider connections, 
            defaults to -1
        :type from_time: int, optional
        :param to_time: Upper bound for time range to consider connections, 
            defaults to _TIMESTAMP_NO_ENDTIME_VALUE
        :type to_time: int, optional
        :param exclude_subcomps: If True, then do not return connections
            to subcomponents or supercomponents.
        :type exclude_subcomps: bool, optional

        :rtype: list[RelationConnection]
        """
        if not self.in_db(strict_check=False, permissions=perimssions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )
        if comp:
            if not isinstance(comp, list):
                comp = [comp]
            comp_id = [c.id() for c in comp]
            for c in comp:
                if not c.in_db(strict_check=False, permissions):
                    raise ComponentNotAddedError(
                        f"Component {c.name} has not yet " +
                        "been added to the database."
                    )
 
        at_time = _parse_time(at_time) 
        from_time = _parse_time(from_time)
        to_time = _parse_time(to_time)

        # Build up the result of format (property vertex, relation)
        result = []

        if not exclude_subcomps:
            for inout in ("in", "out"):
                query = g.t.V(self.id())
                if inout == "in":
                    query = query.inE(RelationSubcomponent.category)
                else:
                    query = query.outE(RelationSubcomponent.category)
                query = query.has('active', True).as_('e').otherV()
                if comp:
                    query = query.hasId(*comp_id)
                query = query.id_().as_('vertex_id') \
                             .select('e').id_().as_('edge_id') \
                             .select('vertex_id', 'edge_id')
                for q in query.toList():
                    c = Component.from_id(q['vertex_id'])
                    if inout == "in":
                        inV, outV = self, c
                    else:
                        inV, outV = c, self
                    edge = RelationSubcomponent(
                        inVertex=inV,
                        outVertex=outV,
                        id=q['edge_id']['@value']['relationId']
                    )
                    result.append(edge)

        # List of property vertices of this property type and active at this
        # time
        query = g.t.V(self.id()).bothE(RelationConnection.category) \
                   .has('active', True)
        if at_time:
            query = query.has('start_time', P.lte(at_time)) \
                         .has('end_time', P.gt(at_time))
        else:
            if to_time:
                query = query.has('start_time', P.lt(to_time))
            if from_time:
                query = query.has('end_time', P.gt(from_time))
        query = query.as_('e').valueMap().as_('edge_props') \
                     .select('e').otherV()
        if comp:
            query = query.hasId(*comp_id)
        query = query.id_().as_('vertex_id') \
                     .select('e').id_().as_('edge_id') \
                     .select('edge_props', 'vertex_id', 'edge_id')

        for q in query.toList():
            c = Component.from_id(q['vertex_id'])
            edge = RelationConnection(
                inVertex=c,
                outVertex=self,
                start=Timestamp._from_dict(q["edge_props"], "start_"),
                end=Timestamp._from_dict(q["edge_props"], "end_"),
                # weird but you have to
                id=q['edge_id']['@value']['relationId']
            )
            result.append(edge)

        return result

    @authenticated
    def get_all_connections_at_time(
        self, at_time: int, exclude_subcomponents: bool = False,
        permissions = None
    ):
        """
        Given a component, return all connections between this Component and 
        all other components.

        :param at_time: Time to check connections at. 
        :param exclude_subcomponents: If True, then do not return connections
            to subcomponents or supercomponents.

        :rtype: list[RelationConnection/RelationSubcomponent]
        """
        raise RuntimeError("Deprecated! Use get_connections().")

        if not self.in_db(strict_check=False):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # Build up the result of format (property vertex, relation)
        result = []

        if not exclude_subcomponents:
            # First do subcomponents.
            for q in g.t.V(self.id()).inE(RelationSubcomponent.category) \
                        .has('active', True).as_('e') \
                        .otherV().id_().as_('vertex_id') \
                        .select('e').id_().as_('edge_id') \
                        .select('vertex_id', 'edge_id').toList():
                c = Component.from_id(q['vertex_id'])
                edge = RelationSubcomponent(
                    inVertex=self,
                    outVertex=c,
                    id=q['edge_id']['@value']['relationId']
                )
                result.append(edge)

            # Now supercomponents.
            for q in g.t.V(self.id()).outE(RelationSubcomponent.category) \
                        .has('active', True).as_('e') \
                        .otherV().id_().as_('vertex_id') \
                        .select('e').id_().as_('edge_id') \
                        .select('vertex_id', 'edge_id').toList():
                c = Component.from_id(q['vertex_id'])
                edge = RelationSubcomponent(
                    inVertex=c,
                    outVertex=self,
                    id=q['edge_id']['@value']['relationId']
                )
                result.append(edge)

        # List of property vertices of this property type and active at this
        # time
        query = g.t.V(self.id()).bothE(RelationConnection.category) \
                   .has('active', True) \
                   .has('start_time', P.lte(at_time)) \
                   .has('end_time', P.gt(at_time)) \
                   .as_('e').valueMap().as_('edge_props') \
                   .select('e').otherV().id_().as_('vertex_id') \
                   .select('e').id_().as_('edge_id') \
                   .select('edge_props', 'vertex_id', 'edge_id').toList()

        for q in query:
            c = Component.from_id(q['vertex_id'])
            edge = RelationConnection(
                inVertex=c,
                outVertex=self,
                start=Timestamp._from_dict(q["edge_props"], "start_"),
                end=Timestamp._from_dict(q["edge_props"], "end_"),
                # weird but you have to
                id=q['edge_id']['@value']['relationId']
            )
            result.append(edge)

        return result

    @authenticated
    def get_all_connections_with(
        self, component, from_time: int = -1,
        to_time: int = g._TIMESTAMP_NO_ENDTIME_VALUE,
        permissions = None
    ):
        """
        Given two components, return all edges that connected them between time
        :param from_time: and to time :param to_time: as a list.

        :param component: The other component to check the connections with.
        :type component: Component
        :param from_time: Lower bound for time range to consider connections, 
        defaults to -1
        :type from_time: int, optional
        :param to_time: Upper bound for time range to consider connections, 
        defaults to _TIMESTAMP_NO_ENDTIME_VALUE
        :type to_time: int, optional

        :rtype: list[RelationConnection]
        """
        raise RuntimeError("Deprecated! Use get_connections().")
        # Done for troubleshooting (so you know which component is not added?)
        if not self.in_db(strict_check=False):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not component.in_db(strict_check=False):
            raise ComponentNotAddedError(
                f"Component {component.name} has not yet " +
                "been added to the database."
            )

        edges = g.t.V(self.id()).bothE(RelationConnection.category)\
                   .has('active', True)

        if to_time < g._TIMESTAMP_NO_ENDTIME_VALUE:
            edges = edges.has('start_time', P.lt(to_time))

        edges = edges.has('end_time', P.gt(from_time)) \
            .as_('e').otherV() \
            .hasId(component.id()).select('e') \
            .order().by(__.values('start_time'), Order.asc) \
            .project('properties', 'id').by(__.valueMap()).by(__.id_()).toList()

        return [RelationConnection(
            inVertex=self, outVertex=component,
            start=Timestamp._from_dict(e["properties"], "start_"),
            end=Timestamp._from_dict(e["properties"], "end_"),
            id=e['id']['@value']['relationId']  # weird but you have to
        ) for e in edges]

    @authenticated
    def get_connection(
        self, component, at_time: int,
        permissions = None
    ):
        """Given two components, return the edge that connected them at
        time :param at_time:.

        :param component: The other component to check the connections with.
        :type component: Component
        :param at_time: The time to check
        :type at_time: int
        """
        raise RuntimeError("Deprecated! Use get_connections().")

        # Done for troubleshooting (so you know which component is not added?)
        if not self.in_db(strict_check=False):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not component.in_db(strict_check=False):
            raise ComponentNotAddedError(
                f"Component {component.name} has not yet " +
                "been added to the database."
            )

        e = g.t.V(self.id()).bothE(RelationConnection.category)\
               .has('active', True) \
               .has('start_time', P.lte(at_time)) \
               .has('end_time', P.gt(at_time)) \
               .as_('e').otherV() \
               .hasId(component.id()).select('e') \
               .project('properties', 'id')\
               .by(__.valueMap())\
               .by(__.id_()).toList()

        if len(e) == 0:
            return None

        assert len(e) == 1

        return RelationConnection(
            inVertex=self, outVertex=component,
            start=Timestamp._from_dict(e[0]["properties"], "start_"),
            end=Timestamp._from_dict(e[0]["properties"], "end_"),
            id=e[0]['id']['@value']['relationId']  # weird but you have to
        )

    def get_all_connections(self):
        """Return all connections between this Component and all other
        components, along with their edges of this component as
        a tuple of the form (Component, RelationConnection)

        :rtype: tuple[Component, RelationConnection]
        """
        raise RuntimeError("Deprecated! Use get_connections().")

        if not self.in_db(strict_check=False):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        # list of property vertices of this property type
        # and active at this time
        query = g.t.V(self.id()).bothE(RelationConnection.category)\
                   .has('active', True) \
                   .as_('e').valueMap().as_('edge_props') \
                   .select('e').otherV().id_().as_('vertex_id') \
                   .select('edge_props', 'vertex_id').toList()

        # Build up the result of format (property vertex, relation)
        result = []

        for q in query:
            prop = Component.from_id(q['vertex_id'])
            edge = RelationConnection(
                inVertex=prop,
                outVertex=self,
                start=Timestamp._from_dict(q["edge_props"], "start_"),
                end=Timestamp._from_dict(q["edge_props"], "end_")
            )
            result.append((prop, edge))

        return result

    @authenticated
    def subcomponent_connect(
            self, comp, strict_add=False, permissions = None):
        """
        Given another Component :param comp:, make it a subcomponent of the current component.

        :param comp: Another component that is a subcomponent of the current component.
        :type comp: Component
        """

        if not self.in_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not comp.in_db(permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {comp.name} has not yet" +
                "been added to the database."
            )

        if self.name == comp.name:
            raise ComponentSubcomponentToSelfError(
                f"Trying to make {self.name} subcomponent to itself."
            )

        current_subcomp = self.get_subcomponent(comp=comp,
                                                permissions=permissions)
        comp_to_subcomp = component.get_subcomponent(comp=self,
                                                     permissions=permissions)

        if comp_to_subcomp is not None:
            strictraise(strict_add,
                        ComponentIsSubcomponentOfOtherComponentError,
               f"Component {comp.name} is already a subcomponent of {self.name}"
            )
            return
        if current_subcomp is not None:

            # Already a subcomponent!
            strictraise(strict_add, ComponentAlreadySubcomponentError,
                f"component {self.name} is already a subcomponent of component {comp.name}"
            )
            return
        else:
            current_subcomp = RelationSubcomponent(
                inVertex=self,
                outVertex=comp
            )

            current_subcomp.add()
#            print(f'subcomponent connected: {self} -> {comp}')

    @authenticated
    def get_subcomponent(self, comp, permissions = None):
        """Given the component itself and its subcomponent, return the edge between them.

        :param comp: The other component which is the subcomponent of the current component.
        :type comp: Component
        """

        # Done for troubleshooting (so you know which component is not added?)
        if not self.in_db(strict_check=False, permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {self.name} has not yet been added to the database."
            )

        if not comp.in_db(strict_check=False, permissions=permissions):
            raise ComponentNotAddedError(
                f"Component {comp.name} has not yet" +
                "been added to the database."
            )

        e = g.t.V(self.id()).bothE(RelationSubcomponent.category)\
               .has('active', True)\
               .as_('e').otherV()\
               .hasId(comp.id())\
               .select('e').project('id').by(__.id_()).toList()

        if len(e) == 0:
            return None

        assert len(e) == 1

        return RelationSubcomponent(
            inVertex=self, outVertex=comp,
            id=e[0]['id']['@value']['relationId']
        )

    @authenticated
    def disable_subcomponent(self, otherComponent,
                             disable_time: int = int(time.time()),
                             permissions = None):
        """Disabling an edge for a subcomponent

        :param otherComponent: Another Component that this component has 
          connection 'rel_subcomponent' with.
        :type othercomponent: Component

        :param disable_time: When this edge was disabled in the database (UNIX
          time).
        :type disable_time: int
        """

        g.t.V(self.id()).bothE(RelationSubcomponent.category)\
           .where(__.otherV().hasId(otherComponent.id()))\
           .property('active', False)\
           .property('time_disabled', disable_time).next()

    def as_dict(self, at_time: int = None, bare = False, permissions = None):
        """Return a dictionary representation of this Component at time
        :param at_time: The time to check the component at. Pass `None` to get
          properties/flags/connexions at all times.
        :type at_time: int or None

        :param bare: If True, then only return a dictionary with the name and
        type and version and comments; if False, then also return all the
        properties, flags and connexions.
        :type bare: bool

        :return: A dictionary representation of this Components's attributes.
        :rtype: dict
        """
        # TODO: at_time has not yet been implemented!
        assert(at_time == None)
        
        base = super().as_dict()

        if not bare:
            prop_dicts = [{**prop.as_dict(), **rel.as_dict()} \
                for (prop, rel) in self.get_all_properties(permissions=permissions)
            ]

            conn_dicts = [{**{"name": conn.other_vertex(self).name},
                           **conn.as_dict()} \
                for conn in self.get_connections(exclude_subcomps=True,
                                                 permissions=permissions)
            ]

            flag_dicts = [flag.as_dict() for \
                          flag in self.get_all_flags(permissions=permissions)]

            subcomp_dicts = [{"name": subcomps.name} \
                for subcomps in self.get_subcomponents(permissions=permissions)
            ]
        
            supercomp_dicts = [{"name": supercomps.name} \
                for supercomps in \
                    self.get_supercomponents(permissions=permissions)
            ]
            extra = {
                'properties': prop_dicts,
                'connections': conn_dicts,
                'flags': flag_dicts,
                'subcomps': subcomp_dicts,
                'supercomps': supercomp_dicts
            }
        else:
            extra = {}

        return {**base, **extra}

    def __repr__(self):
        return f"{self.category} {self.type.name}: {self.name} ({self._id})"
