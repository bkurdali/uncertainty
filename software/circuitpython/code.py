prob = [99,91,67,50,33,13,5,1]

from oam import Uncertainty
import random
import time

unc = Uncertainty()

for trigger in unc.state():
    if not trigger.gate_on:
        unc.lights_out()
    elif trigger.edge_rising:
        for i in range(8):
            flip = random.randrange(100) < prob[i]
            unc.outs[i].value = flip

