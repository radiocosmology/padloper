# Padloper Flask API

This service provides the HTTP API used by the web UI to read and modify Padloper graph data (components, properties, connections, flags, users, and groups).

Quick start
- Local: `flask run --no-debugger`
- With Compose: the service runs as `flask-interface` and is reverse‑proxied by nginx to the web app.

Authentication and sessions
- The UI authenticates via a GitHub OAuth proxy, then calls `POST /api/login` to establish a server‑side session: `session['user']` and `session['perms']`.
- On first login, if a `User` does not exist, it is auto‑created and added to the `readonly` group (no permissions).
- Each request sets the acting Padloper user from the session to enable permission checks and write stamping.

Permissions model
- Padloper enforces permissions on write operations using class/method keys such as `Component;add`.
- The backend sets `session['perms']` from the database. If the current user lacks the required permission for a call, Padloper raises an error.
- Admin group: seeded with all known permissions; use it to grant full access. Readonly group: no permissions.

Roles and defaults
- `readonly`: default for new users; they can only read. UI shows a banner indicating read‑only mode.
- `admin`: full privileges; can manage users/groups and all data.

Routes and required permissions

Authentication
- POST `/api/login` — establish session for a GitHub login. No Padloper permission.
- POST `/api/logout` — end session. No Padloper permission.

Components: types and versions
- POST `/api/set_component_type` — create type. Requires `ComponentType;add`.
- POST `/api/replace_component_type` — replace type. Requires `ComponentType;replace`.
- POST `/api/set_component_version` — create version. Requires `ComponentVersion;add`.
- POST `/api/replace_component_version` — replace version. Requires `ComponentVersion;replace` (route currently returns a placeholder error).
- GET  `/api/component_type_list` — list types (read‑only).
- GET  `/api/component_type_count` — count types (read‑only).
- GET  `/api/component_version_list` — list versions (read‑only).
- GET  `/api/component_version_count` — count versions (read‑only).

Components: instances
- POST `/api/set_component` — create component(s). Requires `Component;add`.
- POST `/api/replace_component` — replace component. Requires `Component;replace`.
- GET  `/api/disable_component` — disable component. Requires `Component;disable`.
- GET  `/api/components_name/<name>` — component details (read‑only).
- GET  `/api/component_list` — list components (read‑only).
- GET  `/api/component_count` — count components (read‑only).

Property types
- POST `/api/set_property_type` — create property type. Requires `PropertyType;add`.
- POST `/api/replace_property_type` — replace property type. Requires `PropertyType;replace`.
- GET  `/api/property_type_list` — list property types (read‑only).
- GET  `/api/property_type_count` — count property types (read‑only).

Component properties
- POST `/api/component_set_property` — set property. Requires `Component;set_property`.
- GET  `/api/component_end_property` — end property. Requires `Component;unset_property`.
- GET  `/api/component_replace_property` — replace property. Requires `Component;replace_property`.
- GET  `/api/component_disable_property` — disable property. Requires `Component;disable_property` (route currently short‑circuited with a placeholder error).

Connections and subcomponents
- POST `/api/component_add_connection` — add connection. Requires `Component;connect`.
- GET  `/api/component_end_connection` — end connection. Requires `Component;disconnect`.
- GET  `/api/component_disable_connection` — disable a connection edge. Requires `RelationConnection;disable`.
- POST `/api/component_add_subcomponent` — add subcomponent. Requires `Component;subcomponent_connect`.
- GET  `/api/component_disable_subcomponent` — disable subcomponent link. Requires `Component;disable_subcomponent` (route currently short‑circuited with a placeholder error).
- GET  `/api/get_connections` — list connections at time (read‑only).
- GET  `/api/get_subcomponents` — list subcomponents (read‑only).

Flags
- POST `/api/set_flag_type` — create flag type. Requires `FlagType;add`.
- POST `/api/replace_flag_type` — replace flag type. Requires `FlagType;replace`.
- POST `/api/set_flag_severity` — create flag severity. Requires `FlagSeverity;add`.
- POST `/api/replace_flag_severity` — replace flag severity. Requires `FlagSeverity;replace`.
- POST `/api/set_flag` — add flag. Requires `Flag;add`.
- POST `/api/unset_flag` — end a flag. Requires `Flag;set_end`.
- POST `/api/replace_flag` — replace a flag. Requires `Flag;replace`.
- GET  `/api/disable_flag` — disable flag. Requires `Flag;disable`.
- GET  `/api/flag_list` — list flags (read‑only).
- GET  `/api/flag_count` — count flags (read‑only).
- GET  `/api/flag_type_list` — list flag types (read‑only).
- GET  `/api/flag_type_count` — count flag types (read‑only).
- GET  `/api/flag_severity_list` — list severities (read‑only).

Users and groups
- POST `/api/new_user` — create user (auto‑assigns `readonly`). Requires `User;add`.
- POST `/api/new_usergroup` — create group. Requires `UserGroup;add`.
- POST `/api/new_set_usergroup` — add user(s) to group(s). Admin‑only at route level and requires `User;add_group` at Padloper level.
- GET  `/api/get_user_list` — list users (read‑only).
- GET  `/api/get_user_groups` — list groups for a user (read‑only).
- GET  `/api/get_user_group_list` — list all groups (read‑only).
- GET  `/api/get_permissions` — list effective permissions for a username (read‑only).
- GET  `/api/get_all_permissions` — list all known permission keys (read‑only).

Deprecated/legacy endpoints
- POST `/api/set_user` and `/api/set_user_group` — legacy forms for user/group creation; use `/api/new_user` and `/api/new_usergroup` instead. If used, they require `User;add` and `UserGroup;add` respectively.
- POST `/api/set_permission` — legacy; a first‑class Permission vertex is not part of the data model; prefer group permissions management via `UserGroup.permissions`.

Notes
- Some write operations use GET (e.g., disable_* routes). They still enforce permissions via Padloper, but new write endpoints should prefer POST.
- Padloper permission keys live in `padloper/_base.py` (`permissions_set`) and are enforced via `@authenticated` on methods.

