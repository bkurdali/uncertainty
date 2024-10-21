prob = [99,91,67,50,33,13,5,1]

from oam import Uncertainty
import random
import time
unc = Uncertainty() 

while True:
    if unc.gate_off:
        unc.lights_out()
    elif unc.rising_edge:
        for i in range(8):
            flip = random.randrange(100) < prob[i]
            unc.outs[i].value = flip
