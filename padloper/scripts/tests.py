import padloper as p
from gremlin_python.process.traversal import TextP

def tnm(name):
    # A wrapper to give all the elements added in the test the same prefix which
    # is hopefully unique.
    return "padloper-scripts-tests_%s" % name

p.set_user("test")

# Start fresh by deleting any elements from the last test that may still be in
# the database.
p.g.t.V().has("name", TextP.startingWith(tnm(""))).drop().iterate()

# Test creating and retreiving.
type_a  = p.ComponentType(tnm("type_a"), "Comment A").add()
type_b  = p.ComponentType(tnm("type_b"), "Comment B").add()
ver_a_a   = p.ComponentVersion(tnm("ver_a-a"), type_a, "Comment A").add()
ver_a_b   = p.ComponentVersion(tnm("ver_a-b"), type_a, "Comment A").add()
type_a_copy = p.ComponentType.from_db(tnm("type_a"))
assert(type_a == type_a_copy)
comp_a1 = p.Component(tnm("comp_a1"), type_a, ver_a_a).add()
comp_a2 = p.Component(tnm("comp_a2"), type_a, ver_a_b).add()
comp_b = p.Component(tnm("comp_b"), type_b).add()

# Test making connections, and ensure that errors are properly thrown if
# components are already connected.
t1 = p.Timestamp.from_cal(2023, 7, 1, 12, 0, 0)
t2 = p.Timestamp.from_cal(2023, 7, 2, 12, 0, 0)
t3 = p.Timestamp.from_cal(2023, 7, 3, 12, 0, 0)
t4 = p.Timestamp.from_cal(2023, 7, 4, 12, 0, 0)
t5 = p.Timestamp.from_cal(2023, 7, 5, 12, 0, 0)
t6 = p.Timestamp.from_cal(2023, 7, 6, 12, 0, 0)
comp_b.connect(comp_a1, t1)
try:
    comp_b.connect(comp_a1, t3)
    raise RuntimeError("Should not be able to connect since already connected!")
except p.ComponentsAlreadyConnectedError:
    pass
comp_b.disconnect(comp_a1, t2)
comp_b.connect(comp_a1, t3, end=t5)
try:
    comp_b.connect(comp_a1, t4)
    raise RuntimeError("Should not be able to connect since already connected!")
except p.ComponentsAlreadyConnectedError:
    pass
comp_b.connect(comp_a1, t6)

# Test replacing connexions, components, etc.
