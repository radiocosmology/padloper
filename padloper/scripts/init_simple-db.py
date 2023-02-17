from datetime import datetime
from padloper.structure import *

# In this example, make a graph for a few computers connected on a network.
uid = "ahincks"

# Add/initialise component types.
t_computer         = ComponentType("computer", "a personal computer").tryadd()
t_router           = ComponentType("router").tryadd()
t_switch           = ComponentType("switch", "a network switch").tryadd()
t_ethernet_port    = ComponentType("ethernet-port", "USB port on a device").tryadd()
t_keyboard         = ComponentType("keyboard").tryadd()
t_monitor          = ComponentType("monitor").tryadd()
t_mouse            = ComponentType("mouse").tryadd()
t_ethernet_cable   = ComponentType("ethernet-cable", "an ethernet cable").tryadd()

# Add/initialise component versions.
v_cat5 = ComponentVersion("cat5", t_ethernet_cable, comments="up to 100 Mbps").tryadd()
v_cat6 = ComponentVersion("cat6", t_ethernet_cable, comments="up to 1 Gbps").tryadd()

# Add/initialise property types.
p_os = PropertyType("OS", "", ".*", 1, [t_computer], comments="operating system") \
        .tryadd()

# Make a router and two four-port switches.
router   = Component("link-master-a1234", t_router).tryadd()
switch1  = Component("switch-wiz-snABC", t_switch).tryadd()
switch2  = Component("switch-wiz-snDEF", t_switch).tryadd()
eth_0000 = Component("eth_0000", t_ethernet_cable, v_cat6).tryadd()
eth_0009 = Component("eth_0009", t_ethernet_cable, v_cat6).tryadd()

switch1_port = []
switch2_port = []
for i in range(6):
    switch1_port.append( Component("switch-wiz6-snABC_p%02d" % i, t_ethernet_port).tryadd() )
    switch2_port.append( Component("switch-wiz6-snDEF_p%02d" % i, t_ethernet_port).tryadd() )

    switch1.try_subcomponent_connect(switch1_port[-1])
    switch2.try_subcomponent_connect(switch2_port[-1])

# Connect switches to each other and to the router.
t = int(datetime(2023, 1, 30, 11, 0, 0).timestamp())
router.tryconnect(eth_0000, t, uid)
eth_0000.tryconnect(switch1_port[0], t, uid)
switch1_port[1].tryconnect(eth_0009, t, uid)
eth_0009.tryconnect(switch2_port[0], t, uid)


accu_server  = Component("accu-server-4001", t_computer).tryadd()
eth_0011     = Component("eth_0011", t_ethernet_cable, v_cat6).tryadd()
sharp_server = Component("sharp-serve_2987", t_computer).tryadd()
eth_0321     = Component("eth_0321", t_ethernet_cable, v_cat6).tryadd()

# Connect servers to network
t = int(datetime(2023, 1, 30, 12, 0, 0).timestamp())
accu_server.tryconnect(eth_0011, t, uid)
eth_0011.tryconnect(switch1_port[2], t, uid)
sharp_server.tryconnect(eth_0321, t, uid)
eth_0321.tryconnect(switch1_port[3], t, uid)

# Make a PC and connect it up.
t = int(datetime(2023, 1, 30, 18, 0, 0).timestamp())
pc       = Component("simons-pc1", t_computer).tryadd()
mouse    = Component("point-doctor_1", t_mouse).tryadd()
kb       = Component("type-guru_1", t_keyboard).tryadd()
monitor  = Component("crystal-clear_1600x900", t_monitor).tryadd()
eth_aa02 = Component("eth_aa02", t_ethernet_cable, v_cat5).tryadd()

pc.tryconnect(mouse, t, uid)
pc.tryconnect(kb, t, uid)
pc.tryconnect(monitor, t, uid)
pc.tryconnect(eth_aa02, t, uid)
eth_aa02.tryconnect(switch2_port[1], t, uid)

# Install some OS on the PC …
os1 = Property("Zubuntu 2022-10", p_os)
os2 = Property("Zubuntu 2023-01", p_os)
t1 = int(datetime(2023, 1, 1, 0, 0, 0).timestamp())
t2 = int(datetime(2023, 1, 30, 0, 0, 0).timestamp())

pc.try_set_property(os1, t1, uid)
pc.try_set_property(os2, t2, uid)
