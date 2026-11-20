import argparse
import padloper as p
import _global as g


PROTECTED_PERMISSIONS = [
    'Component;add',
    'Component;replace',
    'Component;unset_property',
    'Component;replace_property',
    'Component;disable_property',
    'Component;disconnect',
    'Component;disable_connection',
    'Component;disable_subcomponent',
    'Component;subcomponent_connect',
    'ComponentType;add',
    'ComponentType;replace',
    'ComponentVersion;add',
    'ComponentVersion;replace',
    'PropertyType;add',
    'PropertyType;replace',
    # Property add
    'Property;add',
    # Flags
    'FlagSeverity;add',
    'FlagSeverity;replace',
    'Flag;replace',
    # Component sequences (naming schemes for new components)
    'ComponentSequence;add',
    'ComponentSequence;update',
    'ComponentSequence;delete',
]

GENERAL_PERMISSIONS = [
    'Component;connect',
    'Component;set_property',
    'Flag;add',
    # Correct permission name per padloper.permissions_set
    'Flag;set_end',
]


def ensure_group(name, permissions):
    try:
        grp = p.UserGroup.from_db(name)
        return grp
    except Exception:
        grp = p.UserGroup(name=name, permissions=permissions)
        grp.add(permissions=[])
        return grp


def drop_group(name):
    try:
        g.t.V().has('category', p.UserGroup.category).has('name', name).drop().iterate()
    except Exception:
        pass


def ensure_user(name):
    try:
        return p.User.from_db(name)
    except Exception:
        # groups is a required attribute for User; pass empty list
        u = p.User(name=name, groups=[])
        u.add(permissions=[])
        return u


def map_user_to_group(user_name, group_name):
    user = ensure_user(user_name)
    group = ensure_group(group_name, [])
    user.add_group(group)


def main():
    ap = argparse.ArgumentParser(description='Create default user groups and/or map a user to admin group')
    ap.add_argument('--reset-default-groups', action='store_true', help='Drop and recreate readonly/Protected/General')
    ap.add_argument('--skip-default-groups', action='store_true', help='Skip ensuring readonly/Protected/General groups')
    ap.add_argument('--ensure-admin', metavar='GITHUB_LOGIN', help='Ensure admin group exists and map this user to it (user auto-created if missing)')
    ap.add_argument('--actor', default='master', help='DB user to attribute writes as (default: master)')
    args = ap.parse_args()

    # Ensure an actor is available for write stamping and permissions.
    # 1) Set a temporary stub so Vertex.add can stamp uid/time.
    #    (check_permission() treats an empty permission list as "look up the
    #    acting user", so the stub must be able to answer get_permissions().)
    g._user = type("_Stub", (), {
        "name": args.actor,
        "get_permissions": lambda self: list(p.permissions_set),
    })()
    # 2) Ensure the actor user exists (will use the stub for stamping).
    ensure_user(args.actor)
    # 3) Now switch to a real User object so authenticated checks work.
    p.set_user(args.actor)

    if args.reset_default_groups:
        for nm in ('Protected', 'General', 'readonly'):
            drop_group(nm)

    if not args.skip_default_groups:
        # Create a readonly group with no permissions
        ensure_group('readonly', [])
        ensure_group('Protected', PROTECTED_PERMISSIONS)
        ensure_group('General', GENERAL_PERMISSIONS)

    if args.ensure_admin:
        # Ensure admin group (grant all known permissions from padloper)
        ensure_group('admin', sorted(list(p.permissions_set)))
        map_user_to_group(args.ensure_admin, 'admin')


if __name__ == '__main__':
    main()
