"""
local_graph.py

Contains the LocalGraph class, which contains an igraph.Graph instance and some
methods to access and modify it.

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


    def create_from_connections_undirected(self, 
            vertices_iter, edges_iter) -> tuple:
        """
        Instantiate a simple undirected igraph.Graph given an iterator of
        vertices containing their properties, and an iterator of edges
        containing the pairs of vertex names to connect.

        Return a tuple of the type 
        (time to set up vertices, time to set up edges).

        :param vertices_iter: an iterable object containing all of the vertices
        as a dictionary with a 'properties' and a 'type' key. 
        
        :param edges_iter: an iterable object containing all of the necessary
        edges as dictionaries with the values of 2 keys being the names of the
        two vertices to connect with an edge.

        :return: a tuple of the type
        (time to set up vertices, time to set up edges)
        
        :rtype: (float, float)
        """

        self.graph = igraph.Graph()

        vertex_name_to_index = {}

        
        now = datetime.now()

        for vertex_dict in vertices_iter:
            vertex = self.graph.add_vertex()
            vertex['type'] = vertex_dict['type']

            for prop in vertex_dict['properties']:
                vertex[prop] = vertex_dict['properties'][prop][0]

            vertex_name_to_index[vertex['name']] = vertex.index

        vertices_time = (datetime.now() - now).total_seconds()

        now = datetime.now()

        edges_list = [
                (vertex_name_to_index[edges_dict['a']], \
                 vertex_name_to_index[edges_dict['b']]) \
                for edges_dict in edges_iter]

        self.graph.add_edges(edges_list)

        # for edges_dict in edges_iter:
        #     pass

        edges_time = (datetime.now() - now).total_seconds()

        # self.graph.vs['label'] = self.graph.vs['name']

        return (vertices_time, edges_time)


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

        :param target: File location to export the file to. 
        Should be in PNG, PDF, SVG or PostScript format.
        
        :type target: str
        """

        igraph.plot(self.graph, target=target)
    
