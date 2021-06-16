"""
local_graph.py

Contains the LocalGraph class, which contains an igraph.Graph instance and some methods to access and modify it.
Used for subgraphs in a GraphInterface.

Anatoly Zavyalov, 2021
"""

from log_to_file import log_to_file
from datetime import datetime

import igraph

class LocalGraph():
    """

    A wrapper class for an igraph.Graph instance.

    :ivar graph: Contains the igraph Graph.
    """

    graph: igraph.Graph


    def __init__(self) -> None:
        """
        Instantiate an empty igraph.Graph instance.        
        """

        self.graph = igraph.Graph()


    def create_from_connections_undirected(self, vertex_connections: list) -> None:
        """
        Instantiate a simple undirected igraph.Graph given pairs of vertices to connect.

        :param vertex_connections: A list of the format [(name1, name2), (name3, name4), ...] where name# represents the names of the vertices.
        :type vertex_connections: list[tuple[str, str]]
        """

        # See https://igraph.org/python/doc/tutorial/tutorial.html#setting-and-retrieving-attributes for help regarding igraph vertex/edge attributes.

        now = datetime.now()


        # vertex_names[i] denotes the name of the i'th vertex in the local graph.
        vertex_name_arr = []

        # Dictionary of style {..., vertex_names[i]: i, ...}.   
        vertex_name_to_ind = {}

        # List of 2-tuples containing the indices of the pairs of vertices to be added (instead of the names).
        vertex_index_connections = []

        for pair in vertex_connections:

            indices = []

            for i in range(len(pair)):

                if pair[i] not in vertex_name_to_ind:
                    vertex_name_to_ind[pair[i]] = len(vertex_name_arr)
                    vertex_name_arr.append(pair[i])

                indices.append(vertex_name_to_ind[pair[i]])

            vertex_index_connections.append(tuple(indices))

        log_to_file(message="Making local graph.")

        self.graph = igraph.Graph(vertex_index_connections)

        self.graph.vs['name'] = vertex_name_arr

        self.graph.vs['label'] = self.graph.vs['name']

        log_to_file(message=f"Done making local graph, that took {(datetime.now() - now).total_seconds()} seconds.")
        

    def find_shortest_paths(self, name1: str, name2: str):
        """
        Given two vertices labelled with <name1> and <name2>, return the SHORTEST paths between the vertices.

        See https://igraph.org/python/doc/api/igraph._igraph.GraphBase.html#get_all_shortest_paths for documentation.

        :param name1: name property of the vertex to start the traversal at
        :type name1: str
        :param name2: name property of the vertex to end the traversal at
        :type name2: str
        """

        # TODO: maybe perform a check to see if the vertices exist?

        return self.graph.get_all_shortest_paths(name1, to=name2, weights=None, mode='all')
        

    def visualize_graph(self, target: str) -> None:
        """
        Export the graph as an image to :param target:.

        :param target: File location to export the file to. Should be in PNG, PDF, SVG or PostScript format.
        :type target: str
        """

        igraph.plot(self.graph, target=target)
    