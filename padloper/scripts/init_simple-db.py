from datetime import datetime
from padloper import *

# In this example, make a graph for a few computers connected on a network.
uid = "ahincks"

# Add/initialise component types.
t_computer         = ComponentType("computer", "a personal computer").add()
t_router           = ComponentType("router").add()
t_switch           = ComponentType("switch", "a network switch").add()
t_ethernet_port    = ComponentType("ethernet-port", "USB port on a device").add()
t_keyboard         = ComponentType("keyboard").add()
t_monitor          = ComponentType("monitor").add()
t_mouse            = ComponentType("mouse").add()
t_ethernet_cable   = ComponentType("ethernet-cable", "an ethernet cable").add()

# Add/initialise component versions.
v_cat5 = ComponentVersion("cat5", t_ethernet_cable, comments="up to 100 Mbps").add()
v_cat6 = ComponentVersion("cat6", t_ethernet_cable, comments="up to 1 Gbps").add()

# Add/initialise property types.
p_os = PropertyType("OS", "", ".*", 1, [t_computer], comments="operating system") \
        .add()

# Make a router and two four-port switches.
router   = Component("link-master-a1234", t_router).add()
switch1  = Component("switch-wiz-snABC", t_switch).add()
switch2  = Component("switch-wiz-snDEF", t_switch).add()
eth_0000 = Component("eth_0000", t_ethernet_cable, v_cat6).add()
eth_0009 = Component("eth_0009", t_ethernet_cable, v_cat6).add()

switch1_port = []
switch2_port = []
for i in range(6):
    switch1_port.append( Component("switch-wiz6-snABC_p%02d" % i, t_ethernet_port).add() )
    switch2_port.append( Component("switch-wiz6-snDEF_p%02d" % i, t_ethernet_port).add() )

    switch1.subcomponent_connect(switch1_port[-1])
    switch2.subcomponent_connect(switch2_port[-1])

# Connect switches to each other and to the router.
t = int(datetime(2023, 1, 30, 11, 0, 0).timestamp())
router.connect(eth_0000, t, uid)
eth_0000.connect(switch1_port[0], t, uid)
switch1_port[1].connect(eth_0009, t, uid)
eth_0009.connect(switch2_port[0], t, uid)


accu_server  = Component("accu-server-4001", t_computer).add()
eth_0011     = Component("eth_0011", t_ethernet_cable, v_cat6).add()
sharp_server = Component("sharp-serve_2987", t_computer).add()
eth_0321     = Component("eth_0321", t_ethernet_cable, v_cat6).add()

# Connect servers to network
t = int(datetime(2023, 1, 30, 12, 0, 0).timestamp())
accu_server.connect(eth_0011, t, uid)
eth_0011.connect(switch1_port[2], t, uid)
sharp_server.connect(eth_0321, t, uid)
eth_0321.connect(switch1_port[3], t, uid)

# Make a PC and connect it up.
t = int(datetime(2023, 1, 30, 18, 0, 0).timestamp())
pc       = Component("simons-pc1", t_computer).add()
mouse    = Component("point-doctor_1", t_mouse).add()
kb       = Component("type-guru_1", t_keyboard).add()
monitor  = Component("crystal-clear_1600x900", t_monitor).add()
eth_aa02 = Component("eth_aa02", t_ethernet_cable, v_cat5).add()

pc.connect(mouse, t, uid)
pc.connect(kb, t, uid)
pc.connect(monitor, t, uid)
pc.connect(eth_aa02, t, uid)
eth_aa02.connect(switch2_port[1], t, uid)

# Install some OS on the PC …
os1 = Property("Zubuntu 2022-10", p_os)
os2 = Property("Zubuntu 2023-01", p_os)
t1 = int(datetime(2023, 1, 1, 0, 0, 0).timestamp())
t2 = int(datetime(2023, 1, 30, 0, 0, 0).timestamp())

pc.set_property(os1, t1, uid)
pc.set_property(os2, t2, uid)
