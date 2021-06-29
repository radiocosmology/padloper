"""
graph_interface.py

Contains methods for connecting to Gremlin server and setting up a test graph.

Anatoly Zavyalov, 2021
"""

from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.driver.driver_remote_connection \
        import DriverRemoteConnection
from gremlin_python.driver import client

 # Import predicates (gt, gte, lt, lte, etc.)
from gremlin_python.process.traversal import P

 # Import Cardinality such as list_, set_ and single.
from gremlin_python.process.traversal import Cardinality 

# Gremlin server error
from gremlin_python.driver.protocol import GremlinServerError

# Pop.all_ in select(Pop.all_, 'v')
from gremlin_python.process.traversal import Pop
from gremlin_python.process.strategies import SubgraphStrategy
from gremlin_python.process.graph_traversal import GraphTraversalSource

from local_graph import LocalGraph

import logging

class GraphInterface:
    """
    A wrapper class for a graph interface, containing methods to intantiate the 
    graph, load a HIRAX-style graph structure, and more.

    :ivar ALLOWED_VERTEX_LABELS: Contains the allowed labels for vertices 
    in the graph.
    :ivar EXISTING_CONNECTION_END_PLACEHOLDER: The value of the 'end'
    property of a currently existing connection.
    :ivar g: A GraphTraversalSource element that allows to query the graph 
    stored in the Gremlin Server.


    """

    ALLOWED_VERTEX_LABELS: tuple = ('component', 'type')

    EXISTING_CONNECTION_END_PLACEHOLDER = 2**63 - 1

    g: GraphTraversalSource

    local_graph: LocalGraph

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

        self.graph = Graph()

        self.local_graph = LocalGraph()

        try:
            self.g = self.graph.traversal() \
                    .withRemote(DriverRemoteConnection(
                        f'ws://localhost:{port}/gremlin', traversal_source)
                    )
        except GremlinServerError as e:
            logging.critical("GremlinServerError when trying"
                + "to instantiate graph traversal. {e}")            


    def add_vertex(self, label: str, name: str, allow_duplicates: bool=False,
                   enforce_label_scheme: bool=True) -> None:
        """
        Add a vertex to the graph with the label :param label: 
        and 'name' property of :param name:.

        :param label: What to label the vertex. 'component' or 'type'.
        :type label: str
        
        :param name: The 'name' property of the vertex.
        :type name: str

        :param allow_duplicates: Whether to allow vertices of the same label
        and name to be added, defaults to False
        :type allow_duplicates: bool, optional
        
        :param enforce_label_scheme: Whether to enforce that the :param label:
        is in self.ALLOWED_VERTEX_LABELS, defaults to True
        :type enforce_label_scheme: bool, optional
        """

        if not enforce_label_scheme:
            logging.warn(f"Adding vertex with label {label}, name {name}"
                + "without enforcing label naming scheme.")

        elif label not in self.ALLOWED_VERTEX_LABELS:
            logging.error(f"Vertex label {label} is not in allowed vertex"
            + f"labels {self.ALLOWED_VERTEX_LABELS}")

            # TODO: Make own exception (?), raise it here.
            return

        try:
            if allow_duplicates \
                    or self.g.V().has('name', name).count().next() == 0:
                self.g.addV().property('category', label) \
                    .property('name', name).iterate()

            else:
                logging.error(f"Vertex of name {name} already exists.")

        except GremlinServerError as e:
            logging.error(f"Failed to add component of name {name}. {e}")


    def add_component(self, name: str) -> None:
        """
        Add a vertex with label 'component' to the graph with a 'name' property 
        of :param name: if one with this name does not already exist.

        :param name: Value of the 'name' property to assign the vertex to.
        :type name: str
        """

        self.add_vertex(label='component', name=name)


    def add_type(self, type_: str) -> None:
        """
        Add a vertex with label 'type' to the graph with a 'name' property 
        of :param type_:.

        # TODO: figure out better naming for :param type_:.

        :param type_: Value of the 'name' property to assign the vertex to.
        :type type_: str
        """

        self.add_vertex(label='type', name=type_)


    def set_type(self, name: str, type_: str) -> None:
        """
        Connect the component vertex with name property :param name: to a type 
        vertex labelled :param type_: with an edge going into the :param type_: 
        vertex labelled with "type".

        # TODO: figure out better naming for :param type_:.

        :param name: Value of the 'name' property of the component vertex to 
        connect to the type vertex.
        :type name: str
        
        :param type_: Value of the 'name' property of the type vertex.
        :type type_: str
        """

        try:
            self.g.V().has('category', 'component').has('name', name).as_("a") \
                .V().has('category', 'type').has('name', type_).as_("b") \
                .addE("type").from_("a").to("b").iterate()

        except GremlinServerError as e:
            logging.error(f"Failed to set type of component {name} to type"
                + f"{type_}. {e}")


    def set_connection(self, name1: str, name2: str, time: float, 
            connection: bool) -> None:
        """
        Given two vertices labelled with :param name1: and :param name2:, 
        create a new connection or terminate their existing connection, 
        based on the value of :param connection:. Label with time :param time:.

        :param name1: Value of the 'name' property of the first vertex.
        :type name1: str
        :param name2: Value of the 'name' property of the second vertex.
        :type name2: str
        :param time: Time at which the connection was altered.
        :type time: float
        :param connection: True if a connection was created, False otherwise.
        :type connection: bool
        """

        try:
            if connection:
                # Add an edge labelled 'connection' 
                # with a start time of :param time:
                self.g.V().has('category', 'component').has('name', name1) \
                    .as_("a").not_( 
                    __.bothE('connection').as_('e') \
                        .bothV().has('category', 'component').has('name', name2)
                        .select('e') \
                        .has('start', P.lte(time)).has('end', P.gt(time))
                ).V().has('category', 'component').has('name', name2).as_("b") \
                    .addE('connection').from_("a").to("b") \
                    .property('start', time) \
                    .property('end', self.EXISTING_CONNECTION_END_PLACEHOLDER) \
                    .iterate()

            else:
                # For all edges between v1 and v2 labelled 'connection' 
                # (there should only be one) that do not have an 'end'
                # property, create an end property of :param time:.
                self.g.V().has('category', 'component').has('name', name1) \
                    .bothE('connection').as_('e').bothV() \
                    .has('category', 'component').has('name', name2) \
                    .select('e') \
                    .has('end', self.EXISTING_CONNECTION_END_PLACEHOLDER) \
                    .property('end', time).iterate()

        except GremlinServerError as e:
            logging.error(f"Failed to set {connection} connection"
                + f"between components {name1} and {name2} at time {time}. {e}")

    
    # This will put it in V-E-V-E-V-...-V form as a list per path.
    def find_paths(self, name1: str, name2: str, 
        avoid_type: str, time: float) -> list:
        """
        Given two vertices labelled with <name1> and <name2>, 
        return the paths that connect the vertices by edges 
        that were active at <time> as a list.

        Avoid vertices of type avoid_type.

        :param name1: Name parameter of the component vertex to traverse from.
        :type name1: str

        :param name2: Name parameter of the component vertex 
        to terminate the traversal.
        :type name2: str
        
        :param avoid_type: Type of the component vertex to avoid 
        when traversing.
        :type avoid_type: str
        
        :param time: Time to check the edges at.
        :type time: float
        :return: A list of paths of vertices and edges going 
        from vertex with name :param name1: to vertex with name :param name2:
        :rtype: list
        """
        
        try:
            return self.g.V().has('category', 'component').has('name', name1) \
                .repeat(
                __.bothE('connection').has('start', P.lte(time)) \
                    .has('end', P.gt(time)).otherV().not_(
                        __.outE('type').inV().has('category', 'type') \
                            .has('name', avoid_type)
                        ).simplePath()
            ).until(
                    __.has('category', 'component').has('name', name2)
                    ).path().toList()
        
        except GremlinServerError as e:
            logging.error(f"Could not find paths between {name1} and " \
            + f"{name2} at time {time} avoiding {avoid_type}. {e}")


    # This will put it in V-E-V-E-V-...-V form as a list per path.
    def find_shortest_path(self, name1: str, name2: str, 
        avoid_type: str, time: float) -> list:
        """
        Given two vertices labelled with <name1> and <name2>, 
        return the shortest path that connect the vertices by edges 
        that were active at <time> as a list (one element max).
        Avoid vertices of type avoid_type.

        :param name1: Name parameter of the component vertex to traverse from.
        :type name1: str

        :param name2: Name parameter of the component vertex 
        to terminate the traversal.
        :type name2: str
        
        :param avoid_type: Type of the component vertex to avoid 
        when traversing.
        :type avoid_type: str
        
        :param time: Time to check the edges at.
        :type time: float
        :return: A list of paths of vertices and edges going 
        from vertex with name :param name1: to vertex with name :param name2:
        :rtype: list
        """
        
        try:
            return self.g.V().has('category', 'component').has('name', name1) \
                .repeat(
                __.bothE('connection').has('start', P.lte(time)) \
                    .has('end', P.gt(time)).otherV().not_(
                        __.outE('type').inV().has('category', 'type') \
                            .has('name', avoid_type)
                        ).limit(1).simplePath()
            ).until(
                    __.has('category', 'component').has('name', name2)
                    ).path().toList()
        
        except GremlinServerError as e:
            logging.error(f"Could not find shortest path between {name1}"
                    + f"and {name2} at time {time} avoiding {avoid_type}. {e}")


    def get_subgraph_iterators(self, time: float) -> tuple:
        """
        Return a pair of iterators, where the first one is the iterator
        pointing to the collection of vertices, represented by
        {'properties'={...}, type=<str>},
        and the second iterator is pointing to the collection of edges
        active at time :param time:, represented by
        {'a': <str>, 'b': <str>}

        :param time: Time to check
        :type time: float
        :return: A 2-tuple with the 1st element being an iterator 
        of vertices, and the second being an iterator of edges
        represented by pairs of the names of vertices.
        :rtype: tuple[ list[tuple[str, str]], dict[str, list[str]] ]
        """

        vertices_iter = self.g.V().has('category', 'component').as_('v') \
                .valueMap().as_('properties') \
                .select('v').out('type').values('name').as_('type') \
                .select('properties', 'type')

        edges_iter = self.g.E().hasLabel('connection') \
                .has('start', P.lte(time)).has('end', P.gt(time)).as_('edge') \
                .inV().values('name').as_('a') \
                .select('edge').outV().values('name').as_('b') \
                .select('a', 'b')
       
        return (vertices_iter, edges_iter)


    def export_graph(self, file_name: str) -> None:
        """
        Export the graph to :param file_name:.

        :param file_name: A file path.
        :type file_name: str
        """

        logging.info(message=f"Exporting graph to {file_name}.")

        try:
            self.g.io(file_name).write().iterate()
        except GremlinServerError as e:
            logging.error(f"Failed to export graph to {file_name}. {e}")

    def _init_logging(self, log_file: str) -> None:
        """
        Instantiate the logging package to log to file.

        :param log_file: the location of the log file
        :type log_file: str
        """

        logging.basicConfig(filename=log_file, level=logging.INFO)