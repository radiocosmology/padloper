import padloper as p

# TODO: if all methods need basic authentication, default user 
# need to be create
# p.set_user(...)

# Start fresh by deleting instances of these groups from previous runs.
print("Dropping old user groups.")
p.g.t.V().has("name", 'Protected').has('category', p.UserGroup.category).drop().iterate()
p.g.t.V().has("name", 'General').has('category', p.UserGroup.category).drop().iterate()
p.g.t.V().has("name", 'Default').has('category', p.UserGroup.category).drop().iterate()
print("\tDone.")

print("Creating default user group.")
protected_group = p.UserGroup('Default', ['*'])
protected_group._add()
print("\tDone.")

# protected
protected_permissions = [
    # Component:
    'Component;add',
    'Component;replace',
    'Component;unset_property',
    'Component;replace_property',
    'Component;disable_property',
    'Component;disconnect',
    'Component;disable_connection',
    'Component;disable_subcomponent',
    'Component;subcomponent_connect',

    # ComponentType
    'ComponentType;add',
    'ComponentType;replace',

    # ComponentVersion
    'ComponentVersion;add',
    'ComponentVersion;replace',

    # PropertyType
    'PropertyType;add',
    'PropertyType;replace',

    # Property
    'Property;_add',

    # FlagSeverity
    'FlagSeverity;add',
    'FlagSeverity;replace',

    # Flag
    'Flag;replace',
]

print("Creating protected user group.")
protected_group = p.UserGroup('Protected', protected_permissions)
protected_group._add()
print("\tDone.")

# general
general_permissions = [
    # Component
    'Component;connect',
    'Component;set_property',

    # Flag
    'Flag;add',
    'Flag;end_flag',
]

print("Creating general user group")
general_group = p.UserGroup('General', general_permissions)
general_group._add()
print("\tDone.")


# unprotected
# unecessary, just check for user basic permissions