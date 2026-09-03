# HIRAX Layout DB

A repository containing Python interface for accessing the HIRAX Layout DB, as well as the code for the web interface.

## How to start everything up

**N.B.**: It is possible to run everything in Docker — scroll to [Running
Padloper in Docker](#running-padloper-in-docker) for that option and a
quickstart. This and the next several sections cover running everything by
hand (no Docker), which is best for development.

Padloper has four moving parts, started in this order:

1. **JanusGraph** (with Cassandra + Elasticsearch) — the graph database, on port `8182`.
2. **Flask backend** (`flask-interface`) — the API, on port `4300`.
3. **OAuth proxy** (`oauth-proxy-server`) — GitHub OAuth helper, on port `4000`.
4. **React frontend** (`web-interface`) — the UI dev server, on port `4301`.

The installation/configuration of each is described in the sections below.
This section assumes they are already installed and configured.

### Quick setup (recommended)

The helper script `scripts/setup_local.sh` automates the dependency setup. It:

1. **checks prerequisites** (python ≥3.9, node, npm, java),
2. **validates required configuration up front** (see below) — failing *before*
   any install work if something is missing,
3. creates a Python virtualenv and installs the backend (`requirements.txt` +
   editable `padloper`),
4. runs `npm install` for both Node projects,
5. writes `.env` (generating a `SECRET_KEY` and defaulting `PROXY_SERVER_URL`
   to `http://localhost:4000/`), then prints the exact start commands.

**Provide your GitHub OAuth credentials first.** The script requires
`GITHUB_OAUTH_CLIENT_ID` and `GITHUB_OAUTH_CLIENT_SECRET` (it cannot generate
them). Supply them either by exporting them in your shell **or** by editing them
into `.env` — the script reads both and persists them to `.env`:

```
export GITHUB_OAUTH_CLIENT_ID=...
export GITHUB_OAUTH_CLIENT_SECRET=...
bash scripts/setup_local.sh
```

Other modes:

```
bash scripts/setup_local.sh --check-only        # verify prerequisites + config only (no install)
bash scripts/setup_local.sh --skip-oauth        # set up deps now, add OAuth creds later
bash scripts/setup_local.sh --with-janusgraph   # also download the JanusGraph 0.6.x bundle
```

If the OAuth credentials are missing the script tells you exactly what to set
and aborts (use `--skip-oauth` to proceed without them). The manual steps below
explain what the script does and how to run each piece by hand.

### 1. Start JanusGraph

Using the "full" JanusGraph distribution (which bundles Cassandra and
Elasticsearch — see [JanusGraph Installation](#janusgraph-installation-instructions)):
```
cd janusgraph-full-0.6.x/
bin/janusgraph.sh start
```
The first time, seed the schema and the initial `master`/`admin` accounts by
running the contents of `index_setup.txt` in the Gremlin console (see
[Connecting to JanusGraph](#connecting-to-janusgraph)).

### 2. Start the Flask backend

From the repository root, install the Python dependencies and the `padloper`
package itself (once):
```
pip install -r requirements.txt
pip install -e .            # makes `import padloper` work from anywhere
sudo apt install graphviz   # renders the System Diagram page (Visualizations menu)
```
Create a `.env` file at the repository root (see
[Environment configuration](#environment-configuration)). For a local run the
important value is:
```
PROXY_SERVER_URL=http://localhost:4000/
SECRET_KEY=<any-random-string>
```
Then start the backend (port `4300`, the port the frontend expects). The graph
connection defaults to `ws://localhost:8182`; override with the `DB_HOST` env
var if JanusGraph is elsewhere:
```
cd flask-interface/
flask run -p 4300
```

### 3. Start the OAuth proxy

```
cd oauth-proxy-server
npm install      # first run only
CLIENT_ID=<github-oauth-client-id> CLIENT_SECRET=<github-oauth-client-secret> npm start
```
**Note:** the proxy reads `CLIENT_ID` / `CLIENT_SECRET` (not the
`GITHUB_OAUTH_*` names used by Docker Compose — Compose maps them for you). It
listens on port `4000`.

### 4. Start the React frontend

```
cd web-interface/
npm install      # first run only
REACT_APP_GITHUB_CLIENT_ID=<github-oauth-client-id> REACT_APP_BASE_PATH=/padloper npm start
```
The dev server runs on port `4301` and serves the app under `/padloper`. Its
built-in dev proxy (`src/setupProxy.js`) forwards `/api` → `localhost:4300`
(Flask) and `/oauth` → `localhost:4000` (OAuth proxy), so no nginx is needed
locally. Override those targets with the `API_URL` / `OAUTH_URL` env vars if
needed. Open <http://localhost:4301/padloper> in your browser.

## JanusGraph Installation Instructions

The following steps outline how to install [JanusGraph](https://janusgraph.org/) along with the [Apache Cassandra](https://cassandra.apache.org/) storage backend and the [Elasticsearch](https://www.elastic.co/elasticsearch/) indexing backend, as well as setting up [Gremlin-Python](https://pypi.org/project/gremlinpython/), which is used for querying the JanusGraph backend from a Python interface. The operating system used is Windows 10 running Windows Subsystem for Linux using Ubuntu 20.04.2 LTS, however the following instructions will work for native Ubuntu 20.04.2 LTS.

### Installing Java

JanusGraph is built on top of Apache TinkerPop and requires Java. JanusGraph
0.6.x supports both JDK 8 and JDK 11; we recommend **OpenJDK 11**, since Java 8
no longer receives free security updates (the Docker image also uses 11). First,
refresh the list of available packages:
```
sudo apt update
```

Next, install OpenJDK 11:
```
sudo apt install openjdk-11-jdk
```

To verify that the correct version has been installed, run `java -version`. A version similar to `openjdk version "11.0.x"` should be displayed.

### Setting the `$JAVA_HOME` environment variable

Head to `/usr/lib/jvm/` and locate the installation of the JDK. It should look similar to `/usr/lib/jvm/java-11-openjdk-amd64`. Set the `$JAVA_HOME` environment variable to point to the installation of the JDK:
```
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
```

### Setting up JanusGraph

From the [JanusGraph Releases](https://github.com/JanusGraph/janusgraph/releases), download the .zip of the "full" installation of JanusGraph **0.6.x** (the file name should resemble `janusgraph-full-0.6.X.zip`), and extract the contents. This "full" installation includes pre-configured JanusGraph, Apache Cassandra and Elasticsearch, all defaulting to `localhost`. (Use 0.6.x to match the TinkerPop/gremlinpython version this codebase targets; see the Gremlin-Python note above.)

> **Note:** All `conf/...` paths in this section refer to files **inside the
> extracted JanusGraph bundle**, which default to `localhost`. The
> `conf/janusgraph-cql-es-prod.properties` file in *this repository* is used
> only by the Docker build (it points at the Compose container IPs) — do not
> use it for a by-hand install.

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
* Finally, you need to define the schema and seed an initial admin. Open the Gremlin console as described in the next section, and execute the commands in the `index_setup.txt` file (or use the Bootstrap helper described below). This will:
  * Define all required vertex/edge properties (including the `permissions` list on user groups).
  * Create indices and trigger reindexing.
  * Seed a user named `master`, a user group named `admin` with broad permissions, and connect `admin` to `master`.

  Note: Both `index_setup.txt` and `index_setup.groovy` define the full schema/indices and include seeding of the initial `master` user and `admin` group. The bootstrap helper streams `index_setup.txt` into the Gremlin console inside the JanusGraph container.

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

We can also access the JanusGraph server from a Python interface using the
`gremlinpython` module. **Normally you do not install this by hand** — it is
pinned in `requirements.txt` (along with the rest of the backend deps) and
installed via `pip install -r requirements.txt`.

*Important*: the `gremlinpython` version must be compatible with your JanusGraph
server's TinkerPop version. `requirements.txt` currently pins
`gremlinpython==3.7.3`, which has been tested against the JanusGraph 0.6.2
server (TinkerPop 3.5.x) used here, including the heavier traversals. Note that
a 3.7 client against a 3.5.x server is not *formally* supported cross-minor by
TinkerPop; if you upgrade or downgrade JanusGraph, re-check this pin.

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

## Installing the Python backend

Install all backend dependencies (Flask, gremlinpython, etc.) from the pinned
`requirements.txt`, and install the `padloper` package itself in editable mode
so `import padloper` resolves from any working directory:
```
pip install -r requirements.txt
pip install -e .
```
Run these from the repository root, ideally inside a virtual environment
(`python -m venv venv && source venv/bin/activate`). `python-dotenv` (included
in `requirements.txt`) reads the `.flaskenv` file in `flask-interface/` to
configure the Flask CLI, and the root `.env` file for application settings.

> The backend was upgraded to Flask 3.x. The previous Flask 2.0.1 / older pins
> in earlier versions of this README are no longer required; use
> `requirements.txt` as the source of truth.

## Environment configuration

Copy `.env.template` to `.env` and set values as needed:

- `PROXY_SERVER_URL` — OAuth proxy base URL the Flask backend calls. Use
  `http://oauth-proxy-server:4000/` under Docker Compose, or
  `http://localhost:4000/` for a local (non-Docker) run.
- `SECRET_KEY` — Flask secret key for sessions.
- `GITHUB_OAUTH_CLIENT_ID` — GitHub OAuth App Client ID (frontend + proxy).
- `GITHUB_OAUTH_CLIENT_SECRET` — GitHub OAuth App Client Secret (proxy only).

Notes:
- `.env` is ignored by git; do not commit secrets.
- The session cookie is `Secure` and `SameSite=Lax` by default. Set `SESSION_COOKIE_SECURE=false` for a plain-HTTP deployment (the dev compose file does this); browsers exempt `http://localhost`.
- When running via Docker Compose, the `.env` file at the repository root is injected into the `flask-interface` and `oauth-proxy-server` services automatically, and is also used for build-time args for the web interface. Compose maps `GITHUB_OAUTH_CLIENT_ID` → the proxy's `CLIENT_ID` and the web build's `REACT_APP_GITHUB_CLIENT_ID` for you.
- When running locally, the backend loads `.env` via `python-dotenv`, **but the `oauth-proxy-server` and the React dev server do not**. For a by-hand run you must pass their env vars directly (note the different names):
  - OAuth proxy: `CLIENT_ID` and `CLIENT_SECRET` (the values of `GITHUB_OAUTH_CLIENT_ID` / `_SECRET`).
  - React dev server: `REACT_APP_GITHUB_CLIENT_ID` and `REACT_APP_BASE_PATH=/padloper`.
  - See the [start-everything-up](#how-to-start-everything-up) steps for the exact commands.

## Authentication, Users, and Permissions

- Sign-in is via GitHub OAuth (the `oauth-proxy-server`). After successful OAuth in the web UI, the frontend calls the backend `/api/login` to establish a server-side session for your username and permissions.
- First login auto-provisioning: If your GitHub login does not yet exist as a `User` vertex, the backend creates it on first login so you can be assigned to groups immediately after.
- Write operations (adding/replacing vertices/edges) require an authenticated user; the backend associates your username with writes and enforces permissions.
- Initial admin: Running `index_setup.txt` seeds a `master` user and an `admin` user group with broad permissions. Use this account to bootstrap additional users/groups.
- Managing users/groups:
  - Create a user via the UI (Add Users) or POST `/api/new_user` with form data `username=...`. The current model identifies users by name.
  - Create a group via the UI (User Group Management) or POST `/api/new_usergroup` with form data `name=...` and `permissions=perm1,perm2,...` (comma-separated, since permission names themselves contain `;`).
  - Assign users to groups via the UI (User Management), which posts to `/api/new_set_usergroup`; remove them with `/api/remove_user_group`.
  - Deactivate a user via the UI (Edit user, "Deactivate this user") or POST `/api/disable_user` (`username=...`): they are signed out on their next request, cannot log in, and lose all group memberships. Reactivate from the user list ("Show deactivated users") or POST `/api/enable_user`; they come back in `readonly` only. Admin only; you cannot deactivate yourself or the last admin.
  - Edit a group's permissions with `/api/set_usergroup_permissions` (`name=...`, `permissions=perm1,perm2,...`) and delete a group with `/api/disable_usergroup`. These, like group assignment, require membership of the `admin` group.
  - Optional defaults: `padloper/scripts/init_user-groups.py` can seed the `readonly` (no permissions; new users are added to it automatically), `Protected` (structural changes: types, versions, property types, component add/replace/disable) and `General` (day-to-day: connect, set properties, add/end flags) groups, but is not required.

## Setting up React

In `web-interface`, run `npm install` to install all dependencies (a
`package-lock.json` is committed, so `npm ci` works for reproducible installs).
The frontend uses React 18 and `react-scripts` 5.x — the old "must be 4.0.3"
constraint no longer applies.

The dev server is started with `npm start` (see
[step 4 above](#4-start-the-react-frontend)). It needs two env vars:

- `REACT_APP_GITHUB_CLIENT_ID` — your GitHub OAuth App client ID (enables sign-in).
- `REACT_APP_BASE_PATH` — the URL base path; use `/padloper` to match the rest
  of the stack.

During local development, `src/setupProxy.js` proxies API and OAuth requests to
the backend (`4300`) and OAuth proxy (`4000`) so you don't need nginx. In
production (Docker), nginx handles this routing instead and the app is served
from the static build.


## Running Padloper in Docker

Padloper comes with ready-made scripts to launch the application in a set of Docker containers (for testing on a common platform and deployment). Ensure that you have an up-to-date
docker version that supports Docker Compose V2 (i.e., you can run `docker compose up`).

You can set up the containers by simply running:

```
docker compose up -d
```

The default address for the web interface is `localhost:4301` (under the `/padloper` base path), and is configurable in the `docker-compose.yml` file. When using the bundled nginx proxy you can also use `http://localhost:3000/padloper/`.

If you wish to add some sample data, exec into the `flask-interface` container and
run the setup scripts. For instance, to put in the toy model of a database included with
Padloper, run:

```
docker exec -it flask-interface sh -c "export PYTHONPATH=$PYTHONPATH:/; python3 padloper/scripts/init_simple-db.py"
```

### Bootstrap Helper

To initialize the graph schema and map your GitHub user to the `admin` group, you can use `scripts/bootstrap_graph.sh`.

- Prerequisite: start the stack first:
  - `docker compose up -d`
- Default (apply schema if missing, then map user to admin):
  - `bash scripts/bootstrap_graph.sh YOUR_GH_LOGIN`
- Schema only:
  - `bash scripts/bootstrap_graph.sh schema`
- Map user to admin only (requires schema already applied):
  - `bash scripts/bootstrap_graph.sh map-admin YOUR_GH_LOGIN`
- The script waits for JanusGraph’s Gremlin server to become ready; if schema appears to exist (seeded `master` user), it will skip reapplying it.
- Override container names if you customized compose service names:
  - `JANUS_CONTAINER=janusgraph FLASK_CONTAINER=flask-interface bash scripts/bootstrap_graph.sh YOUR_GH_LOGIN`


### Brief explanation of Nginx and Gunicorn

For the dockerization, we added Gunicorn so that the backend is able to handle multiple requests
simultaneously since the built-in `flask` server is single-threaded is meant for development purposes.

Nginx provides provides another layer of managing requests and load balancing, in addition to providing a layer of security by hiding the Gunicorn server from the public internet.

## Quickstart

The steps below bring up a fresh system with persistent data using Docker Compose, initialize the database schema, and prepare admin access via your GitHub user.

1) Prerequisites
- Docker and Docker Compose V2 installed (so you can run `docker compose`).
- A GitHub OAuth App (Client ID/Secret) for sign-in.

2) Configure environment
- Copy `.env.template` to `.env` and set:
  - `GITHUB_OAUTH_CLIENT_ID`, `GITHUB_OAUTH_CLIENT_SECRET`
  - `SECRET_KEY` (any secret string for Flask sessions)
  - Leave `PROXY_SERVER_URL` as default when using Compose.

3) Start services
```
docker compose up -d
```

4) Initialize schema and map your GitHub user to admin (one command)
- Easiest: run the helper (inside the repo, replace YOUR_GH_LOGIN):
```
bash scripts/bootstrap_graph.sh YOUR_GH_LOGIN
```

5) Use the app
- Sign in via GitHub. The header will log in to the backend and establish your session.
- Create users/groups via the UI (Manage Users) or APIs.

### Persistence across reboots
- Data persists in Docker named volumes defined in `docker-compose.yml`:
  - `cassandra_data`, `es_data`, `janusgraph_data`.
- These volumes survive container restarts and host reboots. After a reboot, run:
```
docker compose up -d
```
to bring containers back up. Avoid `docker compose down -v` unless you intend to wipe all data.

### Resetting data
Pick one based on how much you want to reset:

- Reset application containers only (keep data):
```
docker compose down
docker compose up -d --build
```

- Reset JanusGraph data (wipe graph) but keep app config:
```
docker compose down
docker volume rm padloper_user_cassandra_data padloper_user_es_data padloper_user_janusgraph_data
docker compose up -d
# Re-run schema + seeding:
bash scripts/bootstrap_graph.sh YOUR_GH_LOGIN
```

- Full reset (containers + data):
```
docker compose down -v
docker compose up -d --build
# Re-run schema + seeding as above
```

What to keep to avoid data loss:
- Do NOT remove the named volumes if you want to preserve graph data.
- Keep your `.env` file for OAuth/secret configuration.
- App images/containers can be rebuilt safely; data lives in the volumes.

### Notes on authentication
- The UI signs in via GitHub OAuth. After OAuth, it calls `/api/login` to set a server-side session (username + permissions).
- On first login, if your GitHub login does not yet exist as a `User` vertex, the backend auto‑creates it so you can be assigned to groups immediately after.
