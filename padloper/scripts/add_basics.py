from structure import *

t = ComponentType(name="CTYPE-1")
r = ComponentVersion(name="CREV", allowed_type=t)
c = Component(name="COMP-1", type=t, version=r)

pt = PropertyType(
    name="PTYPE-1", units="m", 
    allowed_regex=".*", n_values=3,
    allowed_types=[t]
)

pt.add()

# p = Property(values=['1', '2', '3'], property_type=pt)

c.add()

# c.set_property(property=p, time=123, uid="Anatoly")
