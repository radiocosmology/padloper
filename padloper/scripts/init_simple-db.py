from datetime import datetime
import padloper as p

# In this example, make a graph for a few computers connected on a network.
p.set_user("ahincks")

# Add/initialise component types.
t_computer         = p.ComponentType("computer", "a personal computer").add()
t_router           = p.ComponentType("router").add()
t_switch           = p.ComponentType("switch", "a network switch").add()
t_ethernet_port    = p.ComponentType("ethernet-port",
                                     "USB port on a device").add()
t_keyboard         = p.ComponentType("keyboard").add()
t_monitor          = p.ComponentType("monitor").add()
t_mouse            = p.ComponentType("mouse").add()
t_ethernet_cable   = p.ComponentType("ethernet-cable",
                                     "an ethernet cable").add()

# Add/initialise component versions.
v_cat5 = p.ComponentVersion("cat5", t_ethernet_cable,
                            comments="up to 100 Mbps").add()
v_cat6 = p.ComponentVersion("cat6", t_ethernet_cable,
                            comments="up to 1 Gbps").add()

# Add/initialise property types.
p_os = p.PropertyType("OS", "", ".*", 1, [t_computer],
                      comments="operating system").add()

# Make a router and two four-port switches.
router   = p.Component("link-master-a1234", t_router).add()
switch1  = p.Component("switch-wiz-snABC", t_switch).add()
switch2  = p.Component("switch-wiz-snDEF", t_switch).add()
eth_0000 = p.Component("eth_0000", t_ethernet_cable, v_cat6).add()
eth_0009 = p.Component("eth_0009", t_ethernet_cable, v_cat6).add()

switch1_port = []
switch2_port = []
for i in range(6):
    switch1_port.append(p.Component("switch-wiz6-snABC_p%02d" % i,
                                    t_ethernet_port).add() )
    switch2_port.append(p.Component("switch-wiz6-snDEF_p%02d" % i,
                                    t_ethernet_port).add() )

    switch1.subcomponent_connect(switch1_port[-1])
    switch2.subcomponent_connect(switch2_port[-1])

# Connect switches to each other and to the router.

t = p.Timestamp.from_cal(2023, 1, 30, 11, 0, 0)
router.connect(eth_0000, t)
eth_0000.connect(switch1_port[0], t)
switch1_port[1].connect(eth_0009, t)
eth_0009.connect(switch2_port[0], t)

accu_server  = p.Component("accu-server-4001", t_computer).add()
eth_0011     = p.Component("eth_0011", t_ethernet_cable, v_cat6).add()
sharp_server = p.Component("sharp-serve_2987", t_computer).add()
eth_0321     = p.Component("eth_0321", t_ethernet_cable, v_cat6).add()

# Connect servers to network
t = p.Timestamp.from_cal(2023, 1, 30, 12, 0, 0)
accu_server.connect(eth_0011, t)
eth_0011.connect(switch1_port[2], t)
sharp_server.connect(eth_0321, t)
eth_0321.connect(switch1_port[3], t)

# Make a PC and connect it up.
t = p.Timestamp.from_cal(2023, 1, 30, 18, 0, 0)
pc       = p.Component("simons-pc1", t_computer).add()
mouse    = p.Component("point-doctor_1", t_mouse).add()
kb       = p.Component("type-guru_1", t_keyboard).add()
monitor  = p.Component("crystal-clear_1600x900", t_monitor).add()
eth_aa02 = p.Component("eth_aa02", t_ethernet_cable, v_cat5).add()

pc.connect(mouse, t)
pc.connect(kb, t)
pc.connect(monitor, t)
pc.connect(eth_aa02, t)
eth_aa02.connect(switch2_port[1], t)

# Install some OS on the PC …
os1 = p.Property("Zubuntu 2022-10", p_os)
os2 = p.Property("Zubuntu 2023-01", p_os)
t1 = p.Timestamp.from_cal(2023, 1, 1, 0, 0, 0)
t2 = p.Timestamp.from_cal(2023, 1, 30, 0, 0, 0)

pc.set_property(os1, t1)
pc.set_property(os2, t2)
