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

ANT_1 = Component(name="ANT0001", type=ANT, revision=ANT_A)
ANT_1.add()

DPF_1 = Component(name="DPF0001", type=DPF, revision=DPF_A)
DPF_1.add()

BLN_1, BLN_2 =  Component(name="BLN0001", type=BLN, revision=BLN_A), \
                Component(name="BLN0002", type=BLN, revision=BLN_A)
BLN_1.add()
BLN_2.add()

RFT_1, RFT_2 =  Component(name="RFT0001", type=RFT, revision=RFT_A), \
                Component(name="RFT0002", type=RFT, revision=RFT_A)
RFT_1.add()
RFT_2.add()

OPF_1, OPF_2 =  Component(name="OPF0001", type=OPF, revision=OPF_A), \
                Component(name="OPF0002", type=OPF, revision=OPF_A)
OPF_1.add()
OPF_2.add()

RFR_1, RFR_2 =  Component(name="RFR0001", type=RFR, revision=RFR_A), \
                Component(name="RFR0002", type=RFR, revision=RFR_A)
RFR_1.add()
RFR_2.add()

ADC_1, ADC_2 =  Component(name="ADC0001", type=ADC, revision=ADC_A), \
                Component(name="ADC0002", type=ADC, revision=ADC_A)
ADC_1.add()
ADC_2.add()

COR_1 = Component(name="COR0001", type=COR, revision=COR_A)
COR_1.add()

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

# when to connect all of them, just choose arbitrary time to be lazy.
time = 1646849156
name = "Anatoly"

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