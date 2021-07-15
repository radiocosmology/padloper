"""
graph_interface.py

Contains methods for connecting to Gremlin server and setting up a test graph.

Anatoly Zavyalov, 2021
"""


from local_graph import LocalGraph

from graph_interface import GraphInterface

from structure import *

import logging


class HIRAXInterface:
    """
    The interface that the user interacts with in order to access the
    graph database, as well as create local subgraphs and handle clientside 
    components and so on.

    :ivar _gi: A GraphInterface instance that will interface with the
    graph database.
    
    :ivar _local_graph: A LocalGraph instance for subgraphing.

    # TODO: Consider multiple LocalGraphs in a HIRAXInterface?

    """

    _gi = GraphInterface

    _local_graph: LocalGraph

    def __init__(self, port: int=8182, traversal_source: str='g',
    log_file: str='interface.log') -> None:
        """
        Constructor class.

        :param port: The port on which the Gremlin server is located on
        localhost, defaults to 8182

        :type port: int, optional
        
        :param traversal_source: The traversal source configured in the 
        Gremlin server for the graph 
        (see https://github.com/JanusGraph/janusgraph/issues/1051 for more), 
        defaults to 'g'

        :type traversal_source: str, optional

        :param log_file: The file to write the log to, 
        defaults to 'interface.log'

        :type log_file: str
        """

        self._init_logging(log_file=log_file)

        logging.info("Instantiating graph interface.")

        self._gi = GraphInterface(port=port, traversal_source=traversal_source)          


    def add_component(self, component: Component) -> None:
        """
        Add a vertex of category 'component' using information stored in 
        :param component:. Additionally, mutate :param component: by changing
        its ID attribute to reflect the ID of the JanusGraph vertex just added.

        # TODO: enforce uniqueness through JanusGraph.

        :param component: A Component instance to add to the JanusGraph graph.
        :type component: Component
        """

        # attributes = {
        #     'name': component.name
        # }

        # v = self._add_vertex_to_graph(
        #     category=component.category,
        #     attributes=attributes
        # )

        # component.set_id(id=v.id)

        raise NotImplementedError

    
    def get_component(self, name: str) -> Component:
        """Return a Component representation of the serverside vertex with
        name :param name:.

        :param name: The 'name' property of the vertex.
        :type name: str
        :return: A component instance with a name property :param name:, as well
        as the appropriate ID, component type, and (optional) component revision
        :rtype: Component
        """

        raise NotImplementedError


    def add_component_type(self, component_type: ComponentType) -> None:
        """
        Add a vertex of category 'component_type' using information stored in 
        :param component_type:. Additionally, mutate :param component_type: 
        by changing its ID attribute to reflect the ID 
        of the JanusGraph vertex just added.

        :param component_type: A ComponentType instance to add to the
        JanusGraph graph.
        :type component_type: ComponentType
        """

        # attributes = {
        #     'name': component_type.name,
        #     'comments': component_type.comments
        # }

        # v = self._add_vertex_to_graph(
        #     category=component_type.category,
        #     attributes=attributes
        # )

        # component_type.set_id(id=v.id)

        raise NotImplementedError


    def get_component_type(self, name: str) -> ComponentType:
        """Return a ComponentType representation of the serverside component 
        type with name :param name:.

        :param name: The 'name' property of the component type.
        :type name: str
        :return: A component type instance with appropriate name and comments
        as per the serverside component type.
        :rtype: ComponentType
        """

        raise NotImplementedError


    def add_component_revision(
            self, component_revision: ComponentRevision
        ) -> None:
        """
        Add a vertex of category 'component_revision' using information stored 
        in :param component_revision:. 
        Additionally, mutate :param component_type: by changing its ID attribute
        to reflect the ID of the JanusGraph vertex just added.

        :param component_revision: A ComponentRevision instance to add to the
        JanusGraph graph.
        :type component_revision: ComponentRevision
        """

        raise NotImplementedError


    def get_component_revision(
            self, name: str, component_type: ComponentRevision
        ) -> ComponentRevision:
        """Return a ComponentType representation of the serverside component 
        revision with name :param name: and 
        component type :param component_type:

        :param name: The 'name' property of the component revision.
        :type name: str
        :param component_type: The ComponentType
        :return: A component type instance with appropriate name and comments
        as per the serverside component type.
        :rtype: ComponentType
        """

        raise NotImplementedError
    

    def add_property(
        self, property: Property, component: Component
    ) -> None:
        """

        # TODO: Probably don't even need this method?
        # can do something like component.add_property(property) instead?

        Add a vertex of category 'property' using information stored 
        in :param property: and connect it to component in :param component:. 
        Additionally, mutate :param property: by changing its ID attribute
        to reflect the ID of the JanusGraph vertex just added.

        :param property: Property to add to a component
        :type property: Property
        :param component: The component to add the property to
        :type component: Component
        """

        # component.add_property(property) # ???????

        raise NotImplementedError

    
    def add_property_type(
        self, property_type: PropertyType
    ) -> None:
        """
        Add a PropertyType to the serverside.

        :param property_type: The property type to add
        :type property_type: PropertyType
        """

        # property_type.add()    # ?

        raise NotImplementedError


    def get_property_type(
        self, name: str
    ) -> PropertyType:
        """Return a PropertyType representation of the serverside property 
        type with name :param name:.

        :param name: The 'name' property of the property type.
        :type name: str
        :return: A PropertyType instance with appropriate name and comments
        as per the serverside component type.
        :rtype: PropertyType
        """

        raise NotImplementedError


    def add_flag(
        self, flag: Flag
    ) -> None:
        """
        Add a vertex of category 'flag' using information stored 
        in :param flag: with a unique name.
        Additionally, mutate :param flag: by changing its ID attribute
        to reflect the ID of the JanusGraph vertex just added.

        :param flag: The Flag instance to add to the serverside.
        :type flag: Flag
        """

        # flag.add()    # ?????????????

        raise NotImplementedError


    def get_flag(
        self, name: str
    ) -> Flag:
        """Return a Flag representation of the serverside flag with name
        :param name:.

        :param name: The 'name' property of the serverside flag.
        :type name: str
        :return: A Flag instance with appropriate attributes and ID as per the
        serverside flag.
        :rtype: Flag
        """

        raise NotImplementedError


    def add_flag_type(
        self, flag_type: FlagType
    ) -> None:
        """
        Add a vertex of category 'flag_type' using information stored 
        in :param flag_type: with a unique name.
        Additionally, mutate :param flag_type: by changing its ID attribute
        to reflect the ID of the JanusGraph vertex just added.

        :param flag_type: The FlagType instance to convert to the serverside.
        :type flag_type: FlagType
        """

        # flag_type.add()   # ???????


    def get_flag_type(
        self, name: str
    ) -> FlagType:
        """Return a FlagType representation of the serverside flag with name
        :param name:.

        :param name: The 'name' property of the serverside flag.
        :type name: str
        :return: A Flag instance with appropriate attributes and ID as per the
        serverside flag.
        :rtype: Flag
        """


    def _init_logging(self, log_file: str) -> None:
        """
        Instantiate the logging package to log to file.

        :param log_file: the location of the log file
        :type log_file: str
        """

        logging.basicConfig(filename=log_file, level=logging.INFO)