"""
_global.py

Contains declarations and methods for graph connections. Also holds our global
variables.
"""
import os
from gremlin_python.process.graph_traversal import GraphTraversalSource
import gremlin_python.structure.graph as gremlin_graph
from gremlin_python.driver.driver_remote_connection \
        import DriverRemoteConnection
from gremlin_python.driver.serializer import GraphSONSerializersV3d0
import functools
from gremlin_python.driver import connection as _gremlin_connection


def _patch_gremlin_connection_pool() -> None:
    """Hand a pooled gremlinpython connection back when its write() fails.

    gremlin_python.driver.client.Client.submit_async() takes a Connection out
    of the client's pool and calls Connection.write(). If the socket is not
    open yet, write() first calls connect(). When connect() raises (for
    example because JanusGraph is down) the exception propagates before
    either of the driver's two return-to-pool sites runs, so that Connection
    is lost for good. After pool_size (8) such failures the next traversal
    blocks forever on pool.get() and gunicorn kills the worker on timeout.

    Upstream fixed the equivalent leak for server-side errors in
    TINKERPOP-2105; the connect-failure case is still open in TINKERPOP-3114
    (gremlinpython 3.7.3). This wrapper is that missing fix. Idempotent.
    """
    cls = _gremlin_connection.Connection
    if getattr(cls, "_padloper_pool_patch", False):
        return
    original_write = cls.write

    @functools.wraps(original_write)
    def write(self, request_message):
        try:
            return original_write(self, request_message)
        except Exception:
            if self._pool is not None:
                self._pool.put_nowait(self)
            raise

    cls.write = write
    cls._padloper_pool_patch = True


_patch_gremlin_connection_pool()

_conn: DriverRemoteConnection

_graph = gremlin_graph.Graph()

t: GraphTraversalSource

# A placeholder value for the end_time attribute for a
# relation that is still ongoing.
_TIMESTAMP_NO_ENDTIME_VALUE = 2**63 - 1

# A placeholder value for the end_edit_time attribute for a relation
# that is still ongoing.
_TIMESTAMP_NO_EDITTIME_VALUE = -1

# Placeholder for the ID of an element that does not exist serverside.
_VIRTUAL_ID_PLACEHOLDER = -1

# A cache to prevent querying the DB more than necessary.
_vertex_cache = dict()

# For storing the user for when that needs to get tracked.
_user = None



def start_connection(host: str = "ws://localhost", port: int=8182, traversal_source: str='g') -> None:
    """Start a connection with janusgraph with port :param port:
    with traversal source :traversal_source:.

    :param port: The port to connect to on localhost, defaults to 8182
    :type port: int, optional
    :param traversal_source: The serverside traversal source to query,
    defaults to 'g' (don't change this unless you also change it serverside)
    :type traversal_source: str, optional
    """

    global _conn
    global t

    _conn = DriverRemoteConnection(
        f'{host}:{port}/gremlin',
        traversal_source,
        message_serializer=GraphSONSerializersV3d0()
    )

    t = _graph.traversal().withRemote(_conn)


def end_connection() -> None:
    """Close the _conn connection.

    Calling this will get rid of the RuntimeError that at the end of
    the Python sessions.
    """

    global _conn

    _conn.close()

# Start the default connection when this module is loaded.
start_connection(host=os.environ.get('DB_HOST', 'ws://localhost'))
