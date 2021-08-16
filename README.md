# HIRAX Layout DB

A repository containing Python interface for accessing the HIRAX Layout DB, as well as the code for the web interface.

## JanusGraph Installation Instructions

The following steps outline how to install [JanusGraph](https://janusgraph.org/) along with the [Apache Cassandra](https://cassandra.apache.org/) storage backend and the [Elasticsearch](https://www.elastic.co/elasticsearch/) indexing backend, as well as setting up [Gremlin-Python](https://pypi.org/project/gremlinpython/), which is used for querying the JanusGraph backend from a Python interface. The operating system used is Windows 10 running Windows Subsystem for Linux using Ubuntu 20.04.2 LTS, however the following instructions will work for native Ubuntu 20.04.2 LTS.

### Installing Java

JanusGraph is built on top of Apache TinkerPop, which, in turn, is built on top of Java and hence requires Java SE 8. The implementation of Java that we will install is OpenJDK 1.8. First, refresh the list of available packages:
```
sudo apt update
```

Next, install OpenJDK 1.8:
```
sudo apt install openjdk-8-jdk
```

To verify that the correct version has been installed, run `java -version`. A version similar to `openjdk version "1.8.0_292"` should be displayed.

### Setting the `$JAVA_HOME` environment variable

Head to `/usr/lib/jvm/` and locate the installation fo the JDK. It should look similar to `/usr/lib/jvm/java-8-openjdk-amd64`. Set the `$JAVA_HOME` environment variable to the point to the installation of the JDK:
```
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
```

### Setting up JanusGraph

From the [JanusGraph Releases](https://github.com/JanusGraph/janusgraph/releases), download the .zip of the "full" installation of the latest JanusGraph version (the file name should resemble `janusgraph-full-X.X.X.zip`, where `X.X.X` is the version number), and extract the contents. This "full" installation includes pre-configured JanusGraph, Apache Cassandra and Elasticsearch.

From here, start the JanusGraph server by running
```
bin/janusgraph.sh start
```

## Connecting to JanusGraph

### Gremlin Console

Once connected to the JanusGraph server, we can open the Gremlin console by running
```
bin/gremlin.sh
```

Next, we may create a remote connection to the JanusGraph server. To use the variables when remotely accessing the Gremlin server using Gremlin console, we can connect to the server with a session:
```
:remote connect tinkerpop.server conf/remote.yaml session
```

From here, we can send commands to the JanusGraph server by preceding them with `:>`. We can avoid this by running
```
:remote console
```
which will enable sending all queries directly to the JanusGraph server and avoid teh need of `:>`.


### Gremlin-Python

We can also access the JanusGraph server from a Python interface. First, we install the `gremlinpython` Python module by running
```
pip install gremlinpython
```

Note that a minimum `gremlinpython` version of `3.4.7` must be used for full functionality. Now, we may create a Python file to connect to and query the graph:
```py
# Import full gremlinpython functionality
from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

# Instantiate a Gremlin Graph clientside
graph = Graph()

# Connect to the server, instantiate traversal of graph. Note that the server is opened on port 8182 by default.
g = graph.traversal().withRemote(DriverRemoteConnection('ws://localhost:8182/gremlin','g'))

# Get the vertices of the graph as a list, and print them.
print(g.V().toList())
```

This code will print a list of the vertices of the graph.

## RECOMMENDED: Update Netty version

Using JanusGraph 0.5.3 or later versions, it is possible that a Netty version between 4.1.44 and 4.1.46 is used. To check, navigate to `lib/` and check the version numbers of `netty-all`, `netty-common`, `netty-buffer`, `netty-codec`, `netty-handler`, `netty-resolver`, and `netty-transport` files. These versions have a bug that may cause intermittent Apache Cassandra exceptions that become more frequent as the number of vertices and edges gets larger. Read [this GitHub issue](https://github.com/netty/netty/issues/10070) for more details.

If your Netty version is newer than 4.1.46, this section may be skipped. 

Otherwise, head to the [Maven repository for Netty](https://mvnrepository.com/artifact/io.netty) and download the latest (stable) versions for `netty-all`, `netty-common`, `netty-buffer`, `netty-codec`, `netty-handler`, `netty-resolver`, and `netty-transport`, and replace the old .jar files in `lib/` with these new files.

## More Setup

### RECOMMENDED: Set up indexing

To make certain queries faster, it is recommended that graph indexes are added. Follow the [JanusGraph documentation](https://docs.janusgraph.org/index-management/index-performance/#mixed-index) for more details. To add a composite index (extremely efficient for equality checks), first we connect to **a fresh installation** of the Gremlin server through the Gremlin console. Then, we perform the following queries to create a composite index for a "name" String vertex property and a mixed index for the "start" and "end" Long edge properties.
```
mgmt = graph.openManagement()

name = mgmt.makePropertyKey('name').dataType(String.class).make()

start = mgmt.makePropertyKey('start').dataType(Long.class).make()

end = mgmt.makePropertyKey('end').dataType(Long.class).make()

mgmt.buildIndex('byNameComposite', Vertex.class).addKey(name).buildCompositeIndex()

mgmt.buildIndex('startAndEndMixed', Edge.class).addKey(start).addKey(end).buildMixedIndex("search")

mgmt.commit()

mgmt = graph.openManagement()

mgmt.updateIndex(mgmt.getGraphIndex("byNameComposite"), SchemaAction.REINDEX).get()

mgmt.updateIndex(mgmt.getGraphIndex("startAndEndMixed"), SchemaAction.REINDEX).get()

mgmt.commit()
```
