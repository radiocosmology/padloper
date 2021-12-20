from structure import *

t = ComponentType(name="CTYPE-1")
r = ComponentRevision(name="CREV", allowed_type=t)
c = Component(name="COMP-1", component_type=t, revision=r)

pt = PropertyType(
    name="PTYPE-1", units="m", 
    allowed_regex=".*", n_values=3,
    allowed_types=[t]
)

pt.add()

p = Property(values=['1', '2', '3'], property_type=pt)

c.add()

c.add_property(property=p, time=123, uid="Anatoly")