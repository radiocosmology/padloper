"""
The number of signal chains to add.
"""
chains = 256


"""
How long it takes to create a signal chain. So if the time is 86400,
then a new signal chain is added every day.
"""
time_per_chain = 86400


"""
The Unix time to start adding the chains.
Mon Jan 01 2018 00:00:00 GMT-0500 (Eastern Standard Time)
"""
start_time = 1514782800 


"""
The ID of the user adding the connections. 
"""
name = "Anatoly"

from structure import *

ANT = ComponentType(name="ANT", comments="Antenna")
ANT.add()

DPF = ComponentType(name="DPF", comments="Dual polarization feed")
DPF.add()

BLN = ComponentType(name="BLN", comments="Balun")
BLN.add()

RFT = ComponentType(name="RFT", comments="RFoF transmitter")
RFT.add()

OPF = ComponentType(name="OPF", comments="Optical Fiber")
OPF.add()

RFR = ComponentType(name="RFR", comments="RFoF receiver")
RFR.add()

ADC = ComponentType(name="ADC", comments="Analog to Digital Converter")
ADC.add()

COR = ComponentType(name="COR", comments="Correlator")
COR.add()

# revisions

ANT_A = ComponentRevision(name="A", allowed_type=ANT, comments="ANT revision")
ANT_A.add()

DPF_A = ComponentRevision(name="A", allowed_type=DPF, comments="DPF revision")
DPF_A.add()

BLN_A = ComponentRevision(name="A", allowed_type=BLN, comments="BLN revision")
BLN_A.add()

RFT_A = ComponentRevision(name="A", allowed_type=RFT, comments="RFT revision")
RFT_A.add()

OPF_A = ComponentRevision(name="A", allowed_type=OPF, comments="OPF revision")
OPF_A.add()

RFR_A = ComponentRevision(name="A", allowed_type=RFR, comments="RFR revision")
RFR_A.add()

ADC_A = ComponentRevision(name="A", allowed_type=ADC, comments="ADC revision")
ADC_A.add()

COR_A = ComponentRevision(name="A", allowed_type=COR, comments="COR revision")
COR_A.add()

# components

for chain_num in range(1, chains + 1):

    print(chain_num)
    # add all the good stuff

    ANT_1 = Component(
        name=f"ANT{str(chain_num).zfill(4)}", 
        type=ANT, 
        revision=ANT_A
    )
    ANT_1.add()

    DPF_1 = Component(
        name=f"DPF{str(chain_num).zfill(4)}", 
        type=DPF, 
        revision=DPF_A)
    DPF_1.add()

    BLN_1, BLN_2 =  Component(
            name=f"BLN{str(chain_num * 2 - 1).zfill(4)}",
            type=BLN, 
            revision=BLN_A), \
        Component(
            name=f"BLN{str(chain_num * 2).zfill(4)}", 
            type=BLN,
            revision=BLN_A
        )
    BLN_1.add()
    BLN_2.add()

    RFT_1, RFT_2 =  Component(
            name=f"RFT{str(chain_num * 2 - 1).zfill(4)}", 
            type=RFT, 
            revision=RFT_A), \
        Component(
            name=f"RFT{str(chain_num * 2).zfill(4)}", 
            type=RFT, 
            revision=RFT_A
        )
    RFT_1.add()
    RFT_2.add()

    OPF_1, OPF_2 =  Component(
            name=f"OPF{str(chain_num * 2 - 1).zfill(4)}", 
            type=OPF, 
            revision=OPF_A), \
        Component(
            name=f"OPF{str(chain_num * 2).zfill(4)}", 
            type=OPF, 
            revision=OPF_A
        )
    OPF_1.add()
    OPF_2.add()

    RFR_1, RFR_2 =  Component(
            name=f"RFR{str(chain_num * 2 - 1).zfill(4)}", 
            type=RFR, 
            revision=RFR_A), \
        Component(
            name=f"RFR{str(chain_num * 2).zfill(4)}", 
            type=RFR, 
            revision=RFR_A
        )
    RFR_1.add()
    RFR_2.add()

    ADC_1, ADC_2 =  Component(
            name=f"ADC{str(chain_num * 2 - 1).zfill(4)}", 
            type=ADC, 
            revision=ADC_A), \
        Component(
            name=f"ADC{str(chain_num * 2).zfill(4)}", 
            type=ADC, 
            revision=ADC_A
        )
    ADC_1.add()
    ADC_2.add()

    COR_1 = Component(
            name=f"COR{str(chain_num).zfill(4)}", 
            type=COR, 
            revision=COR_A
        )
    COR_1.add()

    # the time when to add the connections.
    time = start_time + time_per_chain * (chain_num - 1)

    ANT_1.connect(component=DPF_1, time=time, uid=name)

    DPF_1.connect(component=BLN_1, time=time, uid=name)
    DPF_1.connect(component=BLN_2, time=time, uid=name)

    BLN_1.connect(component=RFT_1, time=time, uid=name)
    BLN_2.connect(component=RFT_2, time=time, uid=name)

    RFT_1.connect(component=OPF_1, time=time, uid=name)
    RFT_2.connect(component=OPF_2, time=time, uid=name)

    OPF_1.connect(component=RFR_1, time=time, uid=name)
    OPF_2.connect(component=RFR_2, time=time, uid=name)

    RFR_1.connect(component=ADC_1, time=time, uid=name)
    RFR_2.connect(component=ADC_2, time=time, uid=name)

    ADC_1.connect(component=COR_1, time=time, uid=name)
    ADC_2.connect(component=COR_1, time=time, uid=name)


# connections

# ANT_1 = Component.from_db("ANT0001")

# DPF_1 = Component.from_db("DPF0001")

# BLN_1 = Component.from_db("BLN0001")
# BLN_2 = Component.from_db("BLN0002")

# RFT_1 = Component.from_db("RFT0001")
# RFT_2 = Component.from_db("RFT0002")

# OPF_1 = Component.from_db("OPF0001")
# OPF_2 = Component.from_db("OPF0002")

# RFR_1 = Component.from_db("RFR0001")
# RFR_2 = Component.from_db("RFR0002")

# ADC_1 = Component.from_db("ADC0001")
# ADC_2 = Component.from_db("ADC0002")

# COR_1 = Component.from_db("COR0001")