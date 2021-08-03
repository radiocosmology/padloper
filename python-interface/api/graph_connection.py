"""
graph_connection.py

Contains declarations and methods for graph connections.
"""

from gremlin_python.process.graph_traversal import GraphTraversalSource
import gremlin_python.structure.graph as gremlin_graph
from gremlin_python.driver.driver_remote_connection \
        import DriverRemoteConnection

_conn: DriverRemoteConnection

_graph = gremlin_graph.Graph()

g: GraphTraversalSource

def start_connection(port: int=8182, traversal_source: str='g') -> None:
    """Start a connection on localhost with port :param port: 
    with traversal source :traversal_source:.

    :param port: The port to connect to on localhost, defaults to 8182
    :type port: int, optional
    :param traversal_source: The serverside traversal source to query, 
    defaults to 'g' (don't change this unless you also change it serverside)
    :type traversal_source: str, optional
    """

    global _conn
    global g

    _conn = DriverRemoteConnection(
        f'ws://localhost:{port}/gremlin', 
        traversal_source
    )

    g = _graph.traversal().withRemote(_conn)


def end_connection() -> None:
    """Close the _conn connection.

    Calling this will get rid of the RuntimeError that at the end of
    the Python sessions.
    """

    global _conn

    _conn.close()


# Start the default connection when this module is loaded.
start_connection()