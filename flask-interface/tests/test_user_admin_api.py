"""API tests for user / group administration.

These run against a *scratch* JanusGraph (never the production graph): they
create users and groups and exercise membership, permission and delete routes.
`master` must exist as the only member of 'admin', which is what
index_setup.groovy seeds on a fresh instance.

Example, using the compose images and an isolated network::

    docker network create padloper-scratch
    docker run -d --name jg-scratch --network padloper-scratch \
        --tmpfs /var/lib/janusgraph:size=8g \
        -e JANUS_PROPS_TEMPLATE=berkeleyje-lucene padloper_chord-janusgraph
    # wait for "Channel started" and for the init script to finish, then:
    docker run --rm --network padloper-scratch -e DB_HOST=ws://jg-scratch \
        -e PYTHONPATH=/ -e PYTHONDONTWRITEBYTECODE=1 -e SECRET_KEY=test \
        -v $PWD/flask-interface:/flask-interface:ro -v $PWD/padloper:/padloper:ro \
        -w /tmp padloper_chord-flask-interface \
        python3 -m pytest -q -p no:cacheprovider /flask-interface/tests
    docker rm -f jg-scratch && docker network rm padloper-scratch

The flask app is imported the same way gunicorn does ('flask-interface.app'),
so the repository root must be importable.
"""
import importlib
import re
import os
import sys
import uuid

import pytest

# Repository root (parent of flask-interface/), so 'flask-interface.app' and
# 'padloper' import the same way they do under gunicorn.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
app_module = importlib.import_module('flask-interface.app')
app = app_module.app
import padloper as p  # noqa: E402
import _global as g_top  # noqa: E402

SUF = uuid.uuid4().hex[:6]
U1, U2 = f"zz_u1_{SUF}", f"zz_u2_{SUF}"
G1 = f"zz_group_{SUF}"
PERMS_A = ['Component;add', 'Component;connect']
PERMS_B = ['Component;replace']


def client_as(user, perms):
    app.config['TESTING'] = True
    c = app.test_client()
    with c.session_transaction() as s:
        s['user'] = user
        s['perms'] = perms
    return c


@pytest.fixture(scope='module')
def admin():
    return client_as('master', sorted(p.permissions_set))


def ok(res):
    assert res.status_code == 200, (res.status_code, res.get_data(as_text=True))
    data = res.get_json()
    assert 'error' not in data, data
    return data


def groups_of(c, user):
    return sorted(gr['name'] for gr in ok(c.get(f'/api/get_user_groups?username={user}'))['result'])


def group_row(c, name):
    rows = [gr for gr in ok(c.get('/api/get_user_group_list'))['result'] if gr['name'] == name]
    assert len(rows) <= 1, rows
    return rows[0] if rows else None


def user_row(c, name):
    rows = [u for u in ok(c.get('/api/get_user_list'))['result'] if u['name'] == name]
    assert len(rows) <= 1, rows
    return rows[0] if rows else None


# --- sanity ------------------------------------------------------------------

def test_module_identity():
    # app.py's p_global must be the same module object _base uses, otherwise
    # cache/user globals would be split across two module instances.
    assert app_module.p_global is g_top


def test_requires_login():
    c = app.test_client()
    assert c.get('/api/get_user_list').status_code == 401
    assert c.post('/api/remove_user_group', data={'user': 'x', 'group': 'y'}).status_code == 401


# --- setup via existing routes -------------------------------------------------

def test_create_users_and_group(admin):
    for u in (U1, U2):
        ok(admin.post('/api/new_user', data={'username': u, 'institution': ''}))
        assert groups_of(admin, u) == ['readonly']
    ok(admin.post('/api/new_usergroup', data={'name': G1, 'permissions': ','.join(PERMS_A)}))
    row = group_row(admin, G1)
    assert row is not None and sorted(row['permissions']) == sorted(PERMS_A)
    # Duplicate names are refused, unknown permissions are refused.
    assert admin.post('/api/new_usergroup', data={'name': G1, 'permissions': ''}).status_code == 409
    assert admin.post('/api/new_usergroup', data={'name': G1 + 'x', 'permissions': 'Nope;nope'}).status_code == 400
    assert group_row(admin, G1 + 'x') is None


def test_add_members(admin):
    ok(admin.post('/api/new_set_usergroup', data={'user': U1, 'group': G1}))
    ok(admin.post('/api/new_set_usergroup', data={'user': U2, 'group': G1}))
    assert groups_of(admin, U1) == sorted([G1, 'readonly'])
    assert groups_of(admin, U2) == sorted([G1, 'readonly'])


def test_add_member_unknown_group_is_404(admin):
    res = admin.post('/api/new_set_usergroup', data={'user': U1, 'group': 'zz_nope_' + SUF})
    assert res.status_code == 404


# --- remove from group -----------------------------------------------------------

def test_remove_member(admin):
    ok(admin.post('/api/remove_user_group', data={'user': U1, 'group': G1}))
    assert groups_of(admin, U1) == ['readonly']
    assert groups_of(admin, U2) == sorted([G1, 'readonly']), "other member must be unaffected"
    # The list endpoint (get_list path) must agree with from_db.
    assert sorted(gr['name'] for gr in user_row(admin, U1)['groups']) == ['readonly']
    # The edge is kept but disabled, with who/when recorded.
    uid_disabled = g_top.t.V().has('category', 'user').has('name', U1) \
        .bothE('rel_user_group').has('active', False).values('uid_disabled').toList()
    assert uid_disabled == ['master']


def test_remove_member_twice_is_404(admin):
    res = admin.post('/api/remove_user_group', data={'user': U1, 'group': G1})
    assert res.status_code == 404


def test_readd_member_has_no_duplicates(admin):
    ok(admin.post('/api/new_set_usergroup', data={'user': U1, 'group': G1}))
    assert groups_of(admin, U1) == sorted([G1, 'readonly'])
    active_edges = g_top.t.V().has('category', 'user').has('name', U1) \
        .bothE('rel_user_group').has('active', True).otherV().has('name', G1).count().next()
    assert active_edges == 1


def test_remove_missing_fields_is_400(admin):
    assert admin.post('/api/remove_user_group', data={'user': U1}).status_code == 400
    assert admin.post('/api/remove_user_group', data={'user': 'zz_nobody_' + SUF, 'group': G1}).status_code == 404


# --- permissions -------------------------------------------------------------------

def test_replace_permissions(admin):
    data = ok(admin.post('/api/set_usergroup_permissions',
                         data={'name': G1, 'permissions': ','.join(PERMS_B)}))
    assert data['permissions'] == PERMS_B
    assert sorted(group_row(admin, G1)['permissions']) == PERMS_B
    # Effective permissions of a member follow the group.
    assert sorted(ok(admin.get(f'/api/get_permissions?username={U1}'))['result']) == PERMS_B


def test_replace_permissions_dedupes_and_validates(admin):
    data = ok(admin.post('/api/set_usergroup_permissions',
                         data={'name': G1, 'permissions': 'Component;add, Component;add,Flag;add'}))
    assert data['permissions'] == ['Component;add', 'Flag;add']
    res = admin.post('/api/set_usergroup_permissions', data={'name': G1, 'permissions': 'Nope;nope'})
    assert res.status_code == 400
    # A failed update must leave the previous permissions intact.
    assert sorted(group_row(admin, G1)['permissions']) == ['Component;add', 'Flag;add']
    assert admin.post('/api/set_usergroup_permissions',
                      data={'name': 'zz_nope_' + SUF, 'permissions': ''}).status_code == 404


def test_session_permissions_refresh_without_relogin(admin):
    # U1 is a member of G1; log in as U1 with stale (empty) session perms.
    c = client_as(U1, [])
    ok(c.get('/api/get_user_list'))
    with c.session_transaction() as s:
        assert sorted(s['perms']) == ['Component;add', 'Flag;add']


def test_clear_permissions(admin):
    data = ok(admin.post('/api/set_usergroup_permissions', data={'name': G1, 'permissions': ''}))
    assert data['permissions'] == []
    assert group_row(admin, G1)['permissions'] == []


# --- authorisation -----------------------------------------------------------------

def test_non_admin_is_forbidden(admin):
    c = client_as(U2, [])
    assert c.post('/api/remove_user_group', data={'user': U1, 'group': G1}).status_code == 403
    assert c.post('/api/set_usergroup_permissions', data={'name': G1, 'permissions': ''}).status_code == 403
    assert c.post('/api/disable_usergroup', data={'name': G1}).status_code == 403
    assert c.post('/api/new_set_usergroup', data={'user': U2, 'group': 'admin'}).status_code == 403
    # Nothing changed.
    assert groups_of(admin, U1) == sorted([G1, 'readonly'])


def test_admin_group_is_protected(admin):
    res = admin.post('/api/disable_usergroup', data={'name': 'admin'})
    assert res.status_code == 400
    # master is the only admin member: removing them must be refused.
    res = admin.post('/api/remove_user_group', data={'user': 'master', 'group': 'admin'})
    assert res.status_code == 400
    assert 'admin' in groups_of(admin, 'master')


def test_second_admin_can_be_removed(admin):
    ok(admin.post('/api/new_set_usergroup', data={'user': U2, 'group': 'admin'}))
    assert 'admin' in groups_of(admin, U2)
    ok(admin.post('/api/remove_user_group', data={'user': U2, 'group': 'admin'}))
    assert 'admin' not in groups_of(admin, U2)
    assert 'admin' in groups_of(admin, 'master')


# --- delete group ------------------------------------------------------------------

def test_disable_group(admin):
    ok(admin.post('/api/disable_usergroup', data={'name': G1}))
    assert group_row(admin, G1) is None
    assert groups_of(admin, U1) == ['readonly']
    assert groups_of(admin, U2) == ['readonly']
    # Every membership edge of the disabled group was disabled too.
    live = g_top.t.V().has('category', 'user_group').has('name', G1).has('active', False) \
        .bothE().has('active', True).count().next()
    assert live == 0
    disabled_by = g_top.t.V().has('category', 'user_group').has('name', G1).has('active', False) \
        .values('uid_disabled').toList()
    assert disabled_by == ['master']
    assert admin.post('/api/disable_usergroup', data={'name': G1}).status_code == 404


def test_group_name_can_be_reused_after_delete(admin):
    ok(admin.post('/api/new_usergroup', data={'name': G1, 'permissions': 'Flag;add'}))
    row = group_row(admin, G1)
    assert row is not None and row['permissions'] == ['Flag;add']
    assert groups_of(admin, U1) == ['readonly'], "old memberships must not carry over"
    ok(admin.post('/api/disable_usergroup', data={'name': G1}))
    assert group_row(admin, G1) is None


# --- deactivate / reactivate -----------------------------------------------------

def test_deactivate_user(admin):
    # U2 is active and in readonly; put them in a group first so we can check
    # that reactivation does not restore it.
    ok(admin.post('/api/new_usergroup', data={'name': G1, 'permissions': ''}))
    ok(admin.post('/api/new_set_usergroup', data={'user': U2, 'group': G1}))
    assert groups_of(admin, U2) == sorted([G1, 'readonly'])

    # A logged-in session for U2 works before, and is ended after.
    c2 = client_as(U2, [])
    ok(c2.get('/api/get_user_list'))

    ok(admin.post('/api/disable_user', data={'username': U2}))
    assert user_row(admin, U2) is None, "deactivated users leave the default list"
    res = c2.get('/api/get_user_list')
    assert res.status_code == 401 and 'deactivated' in res.get_json()['error']
    with c2.session_transaction() as sess:
        assert 'user' not in sess, "the stale session must be cleared"
    assert app_module._user_is_deactivated(U2) is True
    assert app_module._user_is_deactivated(U1) is False

    rows = [u for u in ok(admin.get('/api/get_user_list?include_disabled=1'))['result'] if u['name'] == U2]
    assert len(rows) == 1 and rows[0]['active'] is False and rows[0]['uid_disabled'] == 'master'
    assert rows[0]['groups'] == []
    # Membership edges were ended too.
    live = g_top.t.V().has('category', 'user').has('name', U2).has('active', False) \
        .bothE('rel_user_group').has('active', True).count().next()
    assert live == 0
    assert admin.post('/api/disable_user', data={'username': U2}).status_code == 404


def test_deactivate_guards(admin):
    assert admin.post('/api/disable_user', data={'username': 'master'}).status_code == 400, "not yourself"
    assert admin.post('/api/disable_user', data={'username': ''}).status_code == 400
    assert admin.post('/api/disable_user', data={'username': 'zz_nobody_' + SUF}).status_code == 404
    c1 = client_as(U1, [])
    assert c1.post('/api/disable_user', data={'username': 'master'}).status_code == 403
    assert c1.post('/api/enable_user', data={'username': U2}).status_code == 403
    # Deactivating the only other admin is fine; deactivating the last one is not.
    ok(admin.post('/api/new_set_usergroup', data={'user': U1, 'group': 'admin'}))
    c1 = client_as(U1, [])
    assert c1.post('/api/disable_user', data={'username': 'master'}).status_code == 200
    # master is now deactivated and U1 is the last admin; a fresh master session is dead.
    assert admin.get('/api/get_user_list').status_code == 401
    assert c1.post('/api/disable_user', data={'username': U1}).status_code == 400, "not yourself"
    # Reactivate master via U1, give admin back, and leave master as the only
    # admin again so later tests (and reruns) see the seeded state.
    ok(c1.post('/api/enable_user', data={'username': 'master'}))
    ok(c1.post('/api/new_set_usergroup', data={'user': 'master', 'group': 'admin'}))
    ok(c1.post('/api/remove_user_group', data={'user': U1, 'group': 'admin'}))
    assert 'admin' not in groups_of(client_as('master', []), U1)


def test_reactivate_user():
    admin = client_as('master', [])
    ok(admin.post('/api/enable_user', data={'username': U2}))
    assert groups_of(admin, U2) == ['readonly'], "comes back in readonly only"
    row = user_row(admin, U2)
    assert row is not None and row['active'] is True and row['time_disabled'] == -1
    assert g_top.t.V().has('category', 'user').has('name', U2).has('active', True) \
        .properties('uid_disabled').count().next() == 0, "restored to the never-disabled state"
    assert admin.post('/api/enable_user', data={'username': U2}).status_code == 409
    assert admin.post('/api/enable_user', data={'username': 'zz_nobody_' + SUF}).status_code == 404
    # Their session works again.
    ok(client_as(U2, []).get('/api/get_user_list'))
    ok(admin.post('/api/disable_usergroup', data={'name': G1}))


# --- component sequences are permission-gated ----------------------------------

def test_sequences_require_permission():
    admin = client_as('master', [])
    ct = {'name': 'zz_type_' + SUF, 'comments': ''}
    ok(admin.post('/api/set_component_type', query_string=ct, data=ct))
    seq = {'name': 'zz_seq_' + SUF, 'component_type': 'zz_type_' + SUF, 'format': 'ZZ-{}', 'increment': 'true', 'next_seq': '1'}
    # A read-only user is refused (the route reports errors in the body).
    c1 = client_as(U1, [])
    res = c1.post('/api/set_sequence', query_string=seq)
    assert 'error' in res.get_json() and 'permissions' in res.get_json()['error']
    # The seeded admin group predates these permissions; grant them, then it works.
    perms = group_row(admin, 'admin')['permissions'] + ['ComponentSequence;add', 'ComponentSequence;update', 'ComponentSequence;delete']
    ok(admin.post('/api/set_usergroup_permissions', data={'name': 'admin', 'permissions': ','.join(perms)}))
    ok(admin.post('/api/set_sequence', query_string=seq))
    res = c1.post(f"/api/delete_sequence/{seq['name']}")
    assert 'error' in res.get_json()
    ok(admin.post(f"/api/delete_sequence/{seq['name']}"))


# --- system diagram ---------------------------------------------------------------

def test_system_dot_is_pure_and_nests_containers():
    inv = {'components': [{'name': 'S', 'type': 'Site'}, {'name': 'D', 'type': 'Dish'},
                          {'name': 'L', 'type': 'LNA'}, {'name': 'Q"x', 'type': 'Odd'}],
           'containment': [('D', 'S'), ('ghost', 'S')],       # unknown names are ignored
           'connections': [('D', 'L'), ('L', 'ghost')],
           'at_time': 0}
    dot = p.system_dot(inv)
    assert dot.startswith('graph padloper {') and dot.rstrip().endswith('}')
    assert 'as of 1970-01-01 00:00 UTC' in dot
    assert len(re.findall(r'subgraph cluster_\d+ ', dot)) == 1   # containers only; the legend is cluster_legend
    assert dot.index('label="S  (Site)"') < dot.index('"D" [') < dot.index('"D" -- "L";')
    assert '"L" [' in dot and 'ghost' not in dot
    assert '"Q\\"x" [' in dot, "quotes in names are escaped"
    # Legend table with one row per type, colours matching the summary.
    summary = p.system_summary(inv)
    assert [t['name'] for t in summary['types']] == ['Dish', 'LNA', 'Odd', 'Site']
    assert summary['components'] == 4 and summary['connections'] == 1
    for t in summary['types']:
        assert f'<TD BGCOLOR="{t["colour"]}">{t["name"]}</TD>' in dot
    assert '"__legend__" [' in dot and '4 components, 1 connection<' in dot


def test_system_diagram_routes():
    admin = client_as('master', [])   # earlier tests signed the shared client out
    res = admin.get('/api/system_diagram.dot')
    assert res.status_code == 200 and res.mimetype == 'text/vnd.graphviz'
    assert res.get_data(as_text=True).startswith('graph padloper {')
    res = admin.get('/api/system_diagram.svg')
    assert res.status_code == 200, res.get_data(as_text=True)
    assert res.mimetype == 'image/svg+xml' and b'<svg' in res.data
    res = admin.get('/api/system_diagram.json')
    assert res.status_code == 200 and res.is_json
    body = res.get_json()
    assert {'types', 'components', 'connections', 'at_time'} <= set(body)
    assert all({'name', 'colour', 'count'} <= set(t) for t in body['types'])
    assert admin.get('/api/system_diagram.png').status_code == 404
    assert admin.get('/api/system_diagram.dot?time=0').status_code == 200
    assert app.test_client().get('/api/system_diagram.svg').status_code == 401
