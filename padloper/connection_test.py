import gremlin_python.structure.graph as gremlin_graph
from gremlin_python.driver.driver_remote_connection \
        import DriverRemoteConnection
import time

if __name__ == "__main__":
    
    graph = gremlin_graph.Graph()

    start = time.time()
    g = graph.traversal().withRemote(
        DriverRemoteConnection('ws://localhost:8182/gremlin', 'g')
    )
    end = time.time()
    print(end - start)

    start = time.time()
    profile1 = g.V().profile().next()
    end = time.time()
    print("First query:", end - start)

    start = time.time()
    profile2 = g.V().profile().next()
    end = time.time()
    print("Second query:", end - start)