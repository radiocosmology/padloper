# HIRAX Layout DB

A repository containing Python interface for accessing the HIRAX Layout DB, as well as the code for the web interface.

## How to start everything up

**N.B.**: It is possible to run everything in Docker: scroll to the end of this README for instructions on this option. The information in this and subsequent sections is for installing everything by hand, which is probaby best for development environments and perhaps for some production environments.

Assuming that JanusGraph, Flask, and React are installed and configured (see sections below), we can start the JanusGraph server, followed by the Flask server, and then the React server for testing.

To start the JanusGraph server, do
```
cd janusgraph-full-0.x.xx/
bin/janusgraph.sh start
```

Once the JanusGraph server is started, we start the Flask server (using port 4300, which is currently the default port that the React server communicates with):
```
cd flask-interface/
flask run --no-debugger -p 4300
```

Once that is finished, open up another terminal and start the Oauth server
```
cd oauth-proxy-server
npm install # For the first time running the project
npm start
```

Finally, we start the React server:
```
cd web-interface/
npm start
```

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

**Important**: You should follow all the steps below for proper functioning of
padloper.

* Add `schema.default=none` to the graph properties, i.e., to `conf/janusgraph-cql-es.properties`. This will only allow vertices/edges of the right type to be added and will throw an exception if you break the schema.
* The default memory settings can cause the JanusGraph to use quite a bit of RAM. Here are the parameters you can/should tune:
  * With the default settings, the biggest hog is the Cassandra backend (which uses 25% of the RAM or 8GB, whichever is less!). For something more reasonable, edit the `MAX_HEAP_SIZE` setting in `cassandra/conf/cassandra-env.sh`. You can set it to something like `512M` or `1024M`. So far 512 MB has proven perfectly adequate.
  * You can also set the JVM heap size for JanusGraph and the ElasticSearch backend. The relevant parameters are `-Xms` and `-Xmx` in each of `elasticsearch/config/jvm.options`, `conf/jvm-8.options` and `conf/jvm-11.options`. These represent the initial and maximum heap size allowed, respectively, and you should set them to the same value. For instance, for a heap size of 1 GB, set them to `-Xms1g` and `-Xmx1g`; for 512 MB, `-Xms512m` and `-Xmx512m`. If you put these settings in each of the configuration files listed earlier, then a total of 2 GB would be used.
* From here, start the JanusGraph server by running
  ```
  bin/janusgraph.sh start
  ```
* Finally, you need to define the schema. Open the Gremlin console as described in the next session, and execute the commands in the `index_setup.txt` file. This will tell JanusGraph which vertex/edge properties are allowed, their type and will also create indices for faster searching.

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
which will enable sending all queries directly to the JanusGraph server and avoid the need of `:>`.


### Gremlin-Python

We can also access the JanusGraph server from a Python interface. First, we install the `gremlinpython` Python module by running
```
pip install gremlinpython
```

*Important*: make sure the version of `gremlinpython` is supported by your version of Janusgraph. For instance, for v0.6.2 of Janusgraph, more recent versions of `gremlinpython` are not supported and you have to do:
```
pip install gremlinpython==3.5.3
```

Now, we may create a Python file to connect to and query the graph:
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

## Recommendation (deprecated): Update Netty version

*As of at least Janusgraph 0.6.2, this recommendation is deprecated, but is left here in case a similar issue arises in the future.*

> Using JanusGraph 0.5.3 or later versions, it is possible that a Netty version between 4.1.44 and 4.1.46 is used. To check, navigate to `lib/` and check the version numbers of `netty-all`, `netty-common`, `netty-buffer`, `netty-codec`, `netty-handler`, `netty-resolver`, and `netty-transport` files. These versions have a bug that may cause intermittent Apache Cassandra exceptions that become more frequent as the number of vertices and edges gets larger. Read [this GitHub issue](https://github.com/netty/netty/issues/10070) for more details.
> 
> If your Netty version is newer than 4.1.46, this section may be skipped. 
> 
> Otherwise, head to the [Maven repository for Netty](https://mvnrepository.com/artifact/io.netty) and download the latest (stable) versions for `netty-all`, `netty-common`, `netty-buffer`, `netty-codec`, `netty-handler`, `netty-resolver`, and `netty-transport`, and replace the old .jar files in `lib/` with these new files.

## Installing Flask

To install Flask, run the following command:
```
pip install -Iv Flask==2.0.1 
pip install -Iv python-dotenv==0.19.0
```
This will install `Flask` version 2.0.1 and `python-dotenv` version 0.19.0 (see the TODOs, updating these will make Flask not work), which will read the `.flaskenv` file in the flask-interface folder to configure the Flask server.

## Setting up React

In `web-interface`, run `npm install` to install all dependencies. However, `react-scripts` must be set to version `4.0.3` (see the TODOs). 


## Running Padloper in Docker

We've recently added a way for developers to launch the application in a set of Docker containers (for testing on a common platform and deployment). Ensure that you have an up-to-date
docker version that supports Docker Compose V2 (i.e. you can run `docker compose up`).

You can setup the containers by simply running

```
docker compose up -d
```

The default address for the web interface is `localhost:4301`, and is configurable in the `docker-compose.yml` file.

If you wish to add some sample data, you should exec into the flask-interface container and
run the setup scripts since currently, they are not able to synchronize with the janusgraph
database. For instance, to put in the toy model of a database included with
Padloper, run:

```
docker exec -it flask-interface sh -c "export PYTHONPATH=$PYTHONPATH:/; python3 padloper/scripts/init_simple-db.py"
```

### Brief explanation of Nginx and Gunicorn

For the dockerization, we added Gunicorn so that the backend is able to handle multiple requests
simultaneously since the built-in `flask` server is single-threaded is meant for development purposes.

Nginx provides provides another layer of managing requests and load balancing, in addition to providing a layer of security by hiding the Gunicorn server from the public internet.
