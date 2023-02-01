from datetime import datetime
from structure import *

# In this example, make a graph for a few computers connected on a network.
uid = "ahincks"

# Add/initialise component types.
try:
    ComponentType("computer", "a personal computer").add()
    ComponentType("router").add()
    ComponentType("switch", "a network switch").add()
    ComponentType("ethernet-port", "USB port on a device").add()
    ComponentType("keyboard").add()
    ComponentType("monitor").add()
    ComponentType("mouse").add()
    ComponentType("ethernet-cable", "an ethernet cable").add()
except VertexAlreadyAddedError:
    pass # If the elements have already been added, don't complain.
t_computer = ComponentType.from_db("computer")
t_router = ComponentType.from_db("router")
t_switch = ComponentType.from_db("switch")
t_ethernet_port = ComponentType.from_db("ethernet-port")
t_keyboard = ComponentType.from_db("keyboard")
t_monitor = ComponentType.from_db("monitor")
t_mouse = ComponentType.from_db("mouse")
t_ethernet_cable = ComponentType.from_db("ethernet-cable")

# Add/initialise component versions.
try:
    ComponentVersion("cat5", t_ethernet_cable, comments="up to 100 Mbps").add()
    ComponentVersion("cat6", t_ethernet_cable, comments="up to 1 Gbps").add()
except VertexAlreadyAddedError:
    pass # If the elements have already been added, don't complain.
v_cat5 = ComponentVersion.from_db("cat5", t_ethernet_cable)
v_cat6 = ComponentVersion.from_db("cat6", t_ethernet_cable)

# Add/initialise property types.
try:
    PropertyType("OS", "", ".*", 1, [t_computer], comments="operating system") \
        .add()
except VertexAlreadyAddedError:
    pass # If the elements have already been added, don't complain.
p_os = PropertyType.from_db("OS")

# Make a router and two four-port switches.
try:
    Component("link-master-a1234", t_router).add()
    Component("switch-wiz-snABC", t_switch).add()
    Component("switch-wiz-snDEF", t_switch).add()
    Component("eth_0000", t_ethernet_cable, v_cat6).add()
    Component("eth_0009", t_ethernet_cable, v_cat6).add()
except VertexAlreadyAddedError:
    pass
router = Component.from_db("link-master-a1234")
switch1 = Component.from_db("switch-wiz-snABC")
switch2 = Component.from_db("switch-wiz-snDEF")
eth_0000 = Component.from_db("eth_0000")
eth_0009 = Component.from_db("eth_0009")
switch1_port = []
switch2_port = []
for i in range(6):
    try:
        Component("switch-wiz6-snABC_p%02d" % i, t_ethernet_port).add()
        Component("switch-wiz6-snDEF_p%02d" % i, t_ethernet_port).add()
    except VertexAlreadyAddedError:
        pass
    switch1_port.append(Component.from_db("switch-wiz6-snABC_p%02d" % i))
    switch2_port.append(Component.from_db("switch-wiz6-snDEF_p%02d" % i))
    try:
        switch1.subcomponent_connect(switch1_port[-1])
        switch2.subcomponent_connect(switch2_port[-1])
    except ComponentIsSubcomponentOfOtherComponentError:
        pass

# Connect switches to each other and to the router.
t = int(datetime(2023, 1, 30, 11, 0, 0).timestamp())
try:
    router.connect(eth_0000, t, uid)
    eth_0000.connect(switch1_port[0], t, uid)
    switch1_port[1].connect(eth_0009, t, uid)
    eth_0009.connect(switch2_port[0], t, uid)
except ComponentsAlreadyConnectedError:
    pass

# Make two servers.
try:
    Component("accu-server-4001", t_computer).add()
    Component("eth_0011", t_ethernet_cable, v_cat6).add()
    Component("sharp-serve_2987", t_computer).add()
    Component("eth_0321", t_ethernet_cable, v_cat6).add()
except VertexAlreadyAddedError:
    pass
accu_server = Component.from_db("accu-server-4001")
eth_0011 = Component.from_db("eth_0011")
sharp_server = Component.from_db("sharp-serve_2987")
eth_0321 = Component.from_db("eth_0321")

# Connect servers to network
t = int(datetime(2023, 1, 30, 12, 0, 0).timestamp())
try:
    accu_server.connect(eth_0011, t, uid)
    eth_0011.connect(switch1_port[2], t, uid)
    sharp_server.connect(eth_0321, t, uid)
    eth_0321.connect(switch1_port[3], t, uid)
except ComponentsAlreadyConnectedError:
    pass

# Make a PC and connect it up.
t = int(datetime(2023, 1, 30, 18, 0, 0).timestamp())
try:
    Component("simons-pc1", t_computer).add()
    Component("point-doctor_1", t_mouse).add()
    Component("type-guru_1", t_keyboard).add()
    Component("crystal-clear_1600x900", t_monitor).add()
    Component("eth_aa02", t_ethernet_cable, v_cat5).add()
except VertexAlreadyAddedError:
    pass
pc = Component.from_db("simons-pc1")
mouse = Component.from_db("point-doctor_1")
kb = Component.from_db("type-guru_1")
monitor = Component.from_db("crystal-clear_1600x900")
eth_aa02 = Component.from_db("eth_aa02")
try:
    pc.connect(mouse, t, uid)
    pc.connect(kb, t, uid)
    pc.connect(monitor, t, uid)
    pc.connect(eth_aa02, t, uid)
    eth_aa02.connect(switch2_port[1], t, uid)
except ComponentsAlreadyConnectedError:
    pass

# Install some OS on the PC …
os1 = Property("Zubuntu 2022-10", p_os)
os2 = Property("Zubuntu 2023-01", p_os)
t1 = int(datetime(2023, 1, 1, 0, 0, 0).timestamp())
t2 = int(datetime(2023, 1, 30, 0, 0, 0).timestamp())
try:
    pc.set_property(os1, t1, uid)
    pc.set_property(os2, t2, uid)
except PropertyIsSameError:
    pass
