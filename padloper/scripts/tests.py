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
type_a  = p.ComponentType(name=tnm("type_A"), comments="Comment A").add()
type_b  = p.ComponentType(name=tnm("type_b"), comments="Comment B").add()
type_c  = p.ComponentType(name=tnm("type_c"), comments="Comment C").add()
ver_a_a   = p.ComponentVersion(name=tnm("ver_A-a"), type=type_a,
                               comments="Comment A").add()
ver_a_b   = p.ComponentVersion(name=tnm("ver_a-b"), type=type_a,
                               comments="Comment A").add()
comp_a1 = p.Component(name=tnm("comp_A1"), type=type_a, version=ver_a_a).add()
comp_a2 = p.Component(name=tnm("comp_a2"), type=type_a, version=ver_a_b).add()
comp_b = p.Component(name=tnm("comp_b"), type=type_b).add()
comp_b_sub = p.Component(name=tnm("comp_b_sub"), type=type_c).add()
comp_b_super = p.Component(name=tnm("comp_b_super"), type=type_c).add()

# Test replacing a component/types/versions.
orig_type_a = type_a
type_a = type_a.replace(p.ComponentType(name=tnm("type_a"),
                                        comments="Comment A (rev)"))
print("Should not be able to use a deactivated component_type! To be fixed.")
ver_a_a = ver_a_a.replace(p.ComponentVersion(name=tnm("ver_a-a"),
                                             type=type_a, 
                                             comments="Comment A (rev)"))
orig_comp_a1 = comp_a1
comp_a1 = comp_a1.replace(p.Component(name=tnm("comp_a1"), type=type_a, 
                                      version=ver_a_a))

# Check that you can't add two things with the same name.
try:
    p.Component(name=tnm("comp_a1"), type=type_a, 
                         version=ver_a_a).add(strict_add=True)
    raise RuntimeError("Should not be able to add the same component again!")
except p.VertexAlreadyAddedError:
    pass

# Check retrieval.
type_a_copy = p.ComponentType.from_db(tnm("type_a"))
assert(orig_type_a != type_a_copy) # Should fail, since type_a was replaced.
assert(type_a == type_a_copy)
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
try:
    comp_b.connect(orig_comp_a1, t1)
    print(orig_comp_a1.name)
    raise RuntimeError("Should not be able to connect a deactivated component!")
except p.ComponentNotAddedError:
    pass
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

print("Testing as_dict().")
print("    ", str(type_a.as_dict()).replace(test_prefix, ""))
print("    ", str(ver_a_a.as_dict()).replace(test_prefix, ""))
print("    ", str(comp_a1.as_dict(bare=True)).replace(test_prefix, ""))
print("    ", str(comp_a1.as_dict()).replace(test_prefix, ""))

# Test retreiving connexions.
print("Retrieving all connexions.")
conn = comp_b.get_connections()
for c in conn:
    print("    ", str(c).replace(test_prefix, ""))
print("Retrieving connexions with comp_a1.")
conn = comp_b.get_connections(comp=comp_a1)
for c in conn:
    print("    ", str(c).replace(test_prefix, ""))
print("Retrieving connexions with comp_a1 and comp_a2:")
conn = comp_b.get_connections(comp=[comp_a1, comp_a2])
for c in conn:
    print("    ", str(c).replace(test_prefix, ""))
print("Retrieving connexions with comp_a1 and comp_a2 at t4:")
conn = comp_b.get_connections(comp=[comp_a1, comp_a2], at_time=t4)
for c in conn:
    print("    ", str(c).replace(test_prefix, ""))
print("Retrieving all connexions between t1 and t4:")
conn = comp_b.get_connections(from_time=t1, to_time=t4)
for c in conn:
    print("    ", str(c).replace(test_prefix, ""))
print("Retrieving all connexions between t1 and t4, excluding subcomponents:")
conn = comp_b.get_connections(from_time=t1, to_time=t4,
                              exclude_subcomps=True)
for c in conn:
    print("    ", str(c).replace(test_prefix, ""))

# Test disabling connexions.
comp_b.get_connections(comp=comp_a1, at_time=t1)[0].disable()
if len(comp_b.get_connections(comp=comp_a1, at_time=t1)) > 0:
    raise RuntimeError("Connection should not be available after being "\
                       "disabled.")

# Test replacing connexions, components, etc.

# Test properties.
ptype_1 = p.PropertyType(name=tnm("ptype_ONE"), units="cm", n_values=2,
                         allowed_types=[type_a, type_b]).add()
ptype_1 = ptype_1.replace(p.PropertyType(name=tnm("ptype_1"), units="cm",
                                         n_values=2,
                                         allowed_types=[type_a, type_b]))
ptype_2 = p.PropertyType(name=tnm("ptype_2"), units="cm", n_values=2,
                         allowed_regex="^\d+\.[1-9]$",
                         allowed_types=[type_a]).add()
ptype_3 = p.PropertyType(name=tnm("ptype_3"), units="cm", n_values=1,
                         allowed_types=[type_c]).add()

ptype_1_copy = ptype_1.from_db(tnm("ptype_1"))
assert(ptype_1 == ptype_1_copy)
print("Testing as_dict().")
print("    ", str(ptype_1.as_dict()).replace(test_prefix, ""))

prop_1a = p.Property(type=ptype_1, values=["123", "124"])
if prop_1a.in_db():
    raise RuntimeError("Property should not be in the DB!")
prop_1a.add()
prop_1b = p.Property(type=ptype_1, values=["15.5", "17.5"]).add()
prop_2 = p.Property(type=ptype_2, values=["11.2", "12.1"]).add()
prop_3 = p.Property(type=ptype_3, values="19").add()
try:
    p.Property(type=ptype_3, values=["1", "2"]).add()
    raise RuntimeError("Should not have been able to add with wrong number "\
                       "of values!")
except TypeError:
    pass
try:
    p.Property(type=ptype_2, values=["11", "13.4"]).add()
    raise RuntimeError("Should not have been able to add property that does "\
                       "not respect regex!")
except ValueError:
    pass
prop_1a_bis = p.Property(type=ptype_1, values=["123", "124"])
if not prop_1a_bis.in_db():
    raise RuntimeError("Property should be in DB.")

comp_a1.set_property(prop_1a, t1, end=t3)
comp_a1.set_property(prop_2, t1)
try:
    comp_a1.set_property(prop_1b, t2)
    raise RuntimeError("Should not have been able to set property that is "\
                       "already set.")
except p.PropertyIsSameError:
    pass
try:
    comp_a1.set_property(prop_3, t1)
    raise RuntimeError("Should not be able to set property with wrong "\
                       "allowed component type.")
except p.PropertyWrongType:
    pass

comp_a2 = p.Component.from_db(tnm("comp_a2")) # Because type_a was replaced …
comp_a2.set_property(prop_1a, t2)
comp_a2.unset_property(prop_1a, t2)
comp_a2.set_property(prop_1b, t3)
comp_a2.set_property(prop_1a, t5) # Unsets prop_1b and sets prop_1a at t4.
try:
    comp_a2.set_property(prop_1a, t4)
    raise RuntimeError("Should not be able to set a property when another "\
                       "property is already set with an end time.")
except p.PropertyIsSameError:
    pass

# Test flags.
ftype_severe = p.FlagType(name="severe", comments="Something's broken!!")
ftype_comment = p.FlagType(name="comment")
CONTINUE HERE: flask needs to be checked.
