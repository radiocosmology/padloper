from datetime import datetime
import math
from structure import *
import random

offset = 0
n_dish = 1024
adc_per_ice = 8 # In reality it will be 32, but this makes visuals easier …
uid = "ahincks"
bulkhead_n_row = 8
bulkhead_n_col = 16
hirax_lat = -30.951720
hirax_lon = 22.009480
dish_space = 8  # Metres
dlat = 1.0 / 111319.9 * dish_space # Dish spacing in deg.
dlon = 1.0 / 111319.9 * dish_space / math.cos(hirax_lat * math.pi / 180.0)
default_pol_orientation = 13.2 # Random choice …
curr_time = int(datetime(2022, 6, 1, 12, 0, 0).timestamp())
random.seed()

if False:
    ComponentType("dish", "a radio dish").add()
    ComponentType("antenna", "a dual polarisation antenna").add()
    ComponentType("antenna-pol", "one of the polarisations of an antenna").add()
    ComponentType("coax", "coaxial cable").add()
    ComponentType("rfof-tx", "RFoF transmitter").add()
    ComponentType("fibre", "fibre optic cable").add()
    ComponentType("rfof-rx", "RFoF receiver").add()
    ComponentType("bulkhead-plug", "bulkhead feedthrough").add()
    ComponentType("adc", "analogue-to-digital converter").add()
    ComponentType("iceboard", "ICE board").add()
t_dish = ComponentType.from_db("dish")
t_ant = ComponentType.from_db("antenna")
t_pol = ComponentType.from_db("antenna-pol")
t_coax = ComponentType.from_db("coax")
t_rft = ComponentType.from_db("rfof-tx")
t_fibre = ComponentType.from_db("fibre")
t_rfr = ComponentType.from_db("rfof-rx")
t_bulk = ComponentType.from_db("bulkhead-plug")
t_adc = ComponentType.from_db("adc")
t_ice = ComponentType.from_db("iceboard")

if False:    
    ComponentVersion("A", t_ant).add()
    ComponentVersion("B", t_ant).add()
    ComponentVersion("10cm", t_coax, comments="10cm coax cable length").add()
    ComponentVersion("50cm", t_coax, comments="50cm coax cable length").add()
    ComponentVersion("L", t_fibre, comments="long run between RX and TX").add()
v_ant_a = ComponentVersion.from_db("A", t_ant)
v_ant_b = ComponentVersion.from_db("B", t_ant)
v_coax_10cm = ComponentVersion.from_db("10cm", t_coax)
v_coax_50cm = ComponentVersion.from_db("50cm", t_coax)
v_fibre_l = ComponentVersion.from_db("L", t_fibre)

if False:
    PropertyType("location", "deg", "^[\-]?\d*[.]?\d*$", 2, [t_dish],
                 comments="latitude and longitude of dish centre").add()
    PropertyType("pointing", "deg", "^[\-]?\d*[.]?\d*$", 2, [t_dish],
                 comments="alt/az of telescope pointing").add()
    PropertyType("pol-orientation", "deg", "^[\-]?\d*[.]?\d*$", 1, [t_ant],
                comments="degrees clockwise from north of H polarisation").add()
    PropertyType("pol-type", "", "[HV]", 1, [t_pol],
                comments="one of H or V").add()
    PropertyType("attenuation", "dB", "^\d*[.]?\d*$", 1,
                 [t_pol, t_rft, t_rfr, t_bulk, t_adc],
                  comments="additional attenuation of component").add()
p_loc = PropertyType.from_db("location")
p_point = PropertyType.from_db("pointing")
p_orient = PropertyType.from_db("pol-orientation")
p_pol = PropertyType.from_db("pol-type")
p_atten = PropertyType.from_db("attenuation")

# An array of signal chains. Dimensions N_dish × 2 × N_component: number of
# dishes, two polarisations per dish, and then a chain of components.
sig_chain = []
bulkhead = []
bulkhead_row = bulkhead_n_row - 1
bulkhead_col = bulkhead_n_col - 1
ice = []
adc = []
ice_col = adc_per_ice - 1
v_ant = v_ant_a

def new_ice():
    global ice, adc
    print("Adding new ICE board.")
    k = len(ice)
    c = Component("ice_%02d" % (k), t_ice)
    c.add()
    ice.append(c)
    ret = []
    for i in range(adc_per_ice):
        c = Component("adc_%02d-%02d" % (k, i), t_adc)
        c.add()
        c.connect(ice[-1], 0, uid, comments="Until subcomponent available …")
        ret.append(c)
    adc.append(ret)

def new_bulkhead():
    global bulkhead
    print("Adding new bulkhead.")
    ret = []
    k = len(bulkhead)
    for i in range(bulkhead_n_row):
        col = []
        for j in range(bulkhead_n_col):
            c = Component("bulk_%02d-r%02d-c%02d" % (k, i, j), t_bulk)
            c.add()
            col.append(c)
        ret.append(col)
    bulkhead.append(ret)

def add_dish(t, loc, point, orient):
    global sig_chain, bulkhead, bulkhead_row, bulkhead_col, ice_col, v_ant
    i_d = len(sig_chain) + offset
    dish = Component("dish_%04d" % i_d, t_dish)
    dish.add()
    dish.set_property(loc, t, uid)
    dish.set_property(point, t, uid)
    ant = Component("ant_%04d-%s" % (i_d, v_ant.name), t_ant, v_ant)
    ant.add()
    ant.set_property(orient, t, uid)
    ant.connect(dish, 0, uid, comments="Until subcomponents available …")
    i_c = i_d * 2
    i_f = i_d * 4
    sig_chain.append([])
    for p in ["H", "V"]:
        pol = Component("pol_%04d-A_%s" % (i_d, p), t_pol)
        c1 = Component("cx-10cm_%04d" % i_c, t_coax, v_coax_10cm)
        tx = Component("rfof-tx_%04d" % i_c, t_rft)
        f = Component("fibre-L_%04d" % i_c, t_fibre, v_fibre_l)
        rx = Component("rfof-rx_%04d" % i_c, t_rfr)
        c2 = Component("cx-50cm_%04d" % i_f, t_coax, v_coax_50cm)
        i_f += 1
        bulkhead_col += 1
        if bulkhead_col >= bulkhead_n_col:
            bulkhead_col = 0
            bulkhead_row += 1
            if bulkhead_row >= bulkhead_n_row:
                bulkhead_row = 0
                new_bulkhead()
        bh = bulkhead[-1][bulkhead_row][bulkhead_col]
        c3 = Component("cx-50cm_%04d" % i_f, t_coax, v_coax_50cm)
        i_f += 1
        ice_col += 1
        if ice_col >= adc_per_ice:
            ice_col = 0
            new_ice()
        a = adc[-1][ice_col]
        sig_chain[-1].append([dish, ant, pol, c1, tx, f, rx, c2, bh, c3, a])
        for i, c in enumerate(sig_chain[-1][-1]):
            if not c.added_to_db():
                c.add()
            if i > 1:   # Antenna and dish already connected.
                c.connect(sig_chain[-1][-1][i-1], t, uid)
        i_c += 1

# Start by adding two dishes.
print("Laying down two dishes.")
point = Property(["90", "0"], p_point)
lat = hirax_lat
lon = hirax_lon
orient = Property(["%f" % default_pol_orientation], p_orient)
print("Adding initial two dishes.")
for i in range(2):
    loc = Property(["%f" % lat, "%f" % lon], p_loc)
    add_dish(curr_time, loc, point, orient)
    lon += dlon

# Repoint the dishes a couple of times over the next few weeks.
print("Repointing two dishes.")
for i in range(3):
    curr_time += random.randint(86400, 86400 * 14)
    point = Property(["%d" % random.randint(30, 89), "0"], p_point)
    for s in sig_chain:
        s[0][0].set_property(point, curr_time, uid)

# Add 14 more dishes to get an array of 4×4. Upgrade the antenna first. Add them# on a bunch of successive days, randomly incrementing the day.
print("Increasing to 4×4 array.")
v_ant = v_ant_b
lat = hirax_lat
lon = hirax_lon
for i in range(4):
    for j in range(4):
        # Skip the first two since we already have two antennas down.
        if i == 0 and j < 2:
            lon += dlon
            continue
        loc = Property(["%f" % lat, "%f" % lon], p_loc)
        add_dish(curr_time, loc, point, orient)
        if random.randint(0, 1):
            curr_time += 86400 + random.randint(-2700, 2700)
        lon += dlon
    lon = hirax_lon
    lat += dlat

# Rotate all the antennas and repoint at the zenith.
print("Rotating antennas and repointing at the zenith.")
curr_time += random.randint(86400, 86400 * 10)
orient = Property(["%f" % (default_pol_orientation + 12.0)], p_orient)
point = Property(["90", "0"], p_point)
for s in sig_chain:
    s[0][1].set_property(orient, curr_time, uid)
    s[0][0].set_property(point, curr_time, uid)

# Go to a 16×16 array.
print("Increasing to 16×16 array.")
curr_time += random.randint(86400 * 365, 86400 * 500)
lat = hirax_lat
lon = hirax_lon
for i in range(16):
    for j in range(16):
        # Skip the first four since we already have the 4×4 array down.
        if i < 4 and j < 4:
            lon += dlon
            continue
        loc = Property(["%f" % lat, "%f" % lon], p_loc)
        add_dish(curr_time, loc, point, orient)
        if random.randint(0, 3):
            curr_time += 86400 + random.randint(-2700, 2700)
        lon += dlon
    lon = hirax_lon
    lat += dlat

# Repoint.
print("Repointing.")
curr_time += random.randint(86400 * 10, 86400 * 30)
point = Property(["75", "30"], p_point)
for s in sig_chain:
    s[0][0].set_property(point, curr_time, uid)

# Go to a 32×32 array.
print("Increasing to 32×32 array.")
lat = hirax_lat
lon = hirax_lon
curr_time += random.randint(86400 * 365, 86400 * 500)
for i in range(32):
    for j in range(32):
        # Skip the first four since we already have the 4×4 array down.
        if i < 16 and j < 16:
            lon += dlon
            continue
        loc = Property(["%f" % lat, "%f" % lon], p_loc)
        add_dish(curr_time, loc, point, orient)
        if random.randint(0, 5):
            curr_time += 86400 + random.randint(-2700, 2700)
        lon += dlon
    lon = hirax_lon
    lat += dlat
