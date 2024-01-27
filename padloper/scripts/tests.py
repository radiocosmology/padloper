import padloper as p
from gremlin_python.process.traversal import TextP

test_prefix = "padloper-scripts-tests_"

def tnm(name):
    # A wrapper to give all the elements added in the test the same prefix which
    # is hopefully unique.
    return test_prefix + name

def nmt(name):
    # Remove the unique prefix.
    return name[len(test_prefix):]

p.set_user("test")

# Start fresh by deleting any elements from the last test that may still be in
# the database.
print("Dropping old test vertices.")
p.g.t.V().has("name", TextP.startingWith(tnm(""))).drop().iterate()

# Test creating and retreiving.
print("Creating component types, versions and components.")
type_a  = p.ComponentType(tnm("type_a"), "Comment A").add()
type_b  = p.ComponentType(tnm("type_b"), "Comment B").add()
type_c  = p.ComponentType(tnm("type_c"), "Comment C").add()
ver_a_a   = p.ComponentVersion(tnm("ver_a-a"), type_a, "Comment A").add()
ver_a_b   = p.ComponentVersion(tnm("ver_a-b"), type_a, "Comment A").add()
type_a_copy = p.ComponentType.from_db(tnm("type_a"))
assert(type_a == type_a_copy)
comp_a1 = p.Component(tnm("comp_a1"), type_a, ver_a_a).add()
p.Component(tnm("comp_a1"), type_a, ver_a_a).add()
exit()
comp_a2 = p.Component(tnm("comp_a2"), type_a, ver_a_b).add()
comp_b = p.Component(tnm("comp_b"), type_b).add()
comp_b_sub = p.Component(tnm("comp_b_sub"), type_c).add()
comp_b_super = p.Component(tnm("comp_b_super"), type_c).add()
comp_b_copy = p.Component.from_db(tnm("comp_b"))
assert(comp_b == comp_b_copy)

# Test making connections, and ensure that errors are properly thrown if
# components are already connected, but not thrown if connections are permitted.
print("Making connections.")
comp_b.subcomponent_connect(comp_b_sub)
comp_b_super.subcomponent_connect(comp_b)
t1 = p.Timestamp.from_cal(2023, 7, 1, 12, 0, 0)
t2 = p.Timestamp.from_cal(2023, 7, 2, 12, 0, 0)
t3 = p.Timestamp.from_cal(2023, 7, 3, 12, 0, 0)
t4 = p.Timestamp.from_cal(2023, 7, 4, 12, 0, 0)
t5 = p.Timestamp.from_cal(2023, 7, 5, 12, 0, 0)
t6 = p.Timestamp.from_cal(2023, 7, 6, 12, 0, 0)
t7 = p.Timestamp.from_cal(2023, 7, 7, 12, 0, 0)
t8 = p.Timestamp.from_cal(2023, 7, 8, 12, 0, 0)
t9 = p.Timestamp.from_cal(2023, 7, 8, 12, 0, 0)
t10 = p.Timestamp.from_cal(2023, 7, 8, 12, 0, 0)
comp_b.connect(comp_a1, t1)
comp_b.connect(comp_a2, t1, end=t5)
try:
    comp_b.connect(comp_a1, t3)
    raise RuntimeError("Should not be able to connect since already connected!")
except p.ComponentsAlreadyConnectedError:
    pass
comp_b.disconnect(comp_a1, t2)
comp_b.connect(comp_a1, t3, end=t5)
try:
    comp_b.disconnect(comp_a1, t6)
    raise RuntimeError("Should not be able to disconnect since already " +\
                       "connected!")
except p.ComponentsAlreadyDisconnectedError:
    pass
try:
    comp_b.connect(comp_a1, t4)
    raise RuntimeError("Should not be able to connect since already connected!")
except p.ComponentsAlreadyConnectedError:
    pass
comp_b.connect(comp_a1, t8)
try:
    comp_b.connect(comp_a1, t6, end=t8)
    raise RuntimeError("Should not be able to connect since end time overlaps "
                       "with next start time.")
except p.ComponentsOverlappingConnectionError:
    pass
comp_b.connect(comp_a1, t6, end=t7)

# Test retreiving connexions.
print("Retrieving all connexions.")
conn = comp_b.get_connections()
for c in conn:
    print("    ", str(c).replace(test_prefix, ""))
print("Retrieving connexions with comp_a1.")
conn = comp_b.get_connections(component=comp_a1)
for c in conn:
    print("    ", str(c).replace(test_prefix, ""))
print("Retrieving connexions with comp_a1 and comp_a2:")
conn = comp_b.get_connections(component=[comp_a1, comp_a2])
for c in conn:
    print("    ", str(c).replace(test_prefix, ""))
print("Retrieving connexions with comp_a1 and comp_a2 at t4:")
conn = comp_b.get_connections(component=[comp_a1, comp_a2], at_time=t4)
for c in conn:
    print("    ", str(c).replace(test_prefix, ""))
print("Retrieving all connexions between t1 and t4:")
conn = comp_b.get_connections(from_time=t1, to_time=t4)
for c in conn:
    print("    ", str(c).replace(test_prefix, ""))
print("Retrieving all connexions between t1 and t4, excluding subcomponents:")
conn = comp_b.get_connections(from_time=t1, to_time=t4,
                              exclude_subcomponents=True)
for c in conn:
    print("    ", str(c).replace(test_prefix, ""))

# Test disabling connexions.
comp_b.get_connections(component=comp_a1, at_time=t1)[0].disable()
if len(comp_b.get_connections(component=comp_a1, at_time=t1)) > 0:
    raise RuntimeError("Connection should not be available after being "\
                       "disabled.")

# Test replacing connexions, components, etc.

# Test properties.
