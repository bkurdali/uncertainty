import time
import board
import digitalio
from analogio import AnalogIn
import pwmio


class Hardware:
    """ Try to keep board specific/magic values and functions in one place """
    pwm_freq = 10000000
    pins = ["D1", "D2", "D3", "D6", "D10", "D9", "D8", "D7"] # Board specific
    adc_pin = "A0" # Board specific
    OUTPUT, INPUT = (digitalio.Direction.OUTPUT, digitalio.Direction.INPUT)

    adc = AnalogIn(getattr(board, adc_pin))

    def _set_digital_IO(self, pin_id, direction=OUTPUT):
        """ Sets an on/off pin (in or out based on direction)"""
        pin = digitalio.DigitalInOut(getattr(board, pin_id))
        pin.direction = direction
        return pin

    def _set_pwm_out(self, pin_id, frequency=pwm_freq, duty_cycle=0):
        """ Sets a PWM output pin"""
        return pwmio.PWMOut(
            getattr(board, pin_id),
            frequency=frequency, duty_cycle=duty_cycle)


class Uncertainty(Hardware):

    def __init__(self, outputMode='digital', loop=None):
        if (outputMode == 'digital'):
            self.outs = [self._set_digital_IO(pin) for pin in self.pins]
        elif (outputMode == 'pwm'):
            self.outs = [self._set_pwm_out(pin) for pin in self.pins]
        self.high_thresh = 50000 # just under 3v
        self.low_thresh = 40000 # around 1v
        self.triggers = [False, False] # [Falling, Rising]
        self.saw_falling = self.saw_rising = False

    def state(self):
        level = self.adc.value
        if level > self.high_thresh:
            self.saw_falling = False
            high = True #call level_high function if there is one
            if not self.saw_rising:
                self.saw_rising = True
                rising = True# call rising_edge function if there is one
        elif level < self.low_thresh:
            self.saw_rising = False
            low = True# call level_low function if there is one
            if not self.saw_falling:
                self.saw_falling = True
                falling = True#call falling_edge function if there is one
        return high,rising,low,falling

    def check_gate(self, high=True):
        if high:
            return self.adc.value > self.high_thresh
        return self.adc.value < self.low_thresh

    def _detect_edge(self, high=True):
        """ Detect a high(True) or low(False) edge """
        if self.check_gate(high=not high): # opposite state
            self.triggers[high] = False
            return False
        if self.triggers[high]: # already triggered
            return False
        # new edge
        self.triggers[high] = True
        return True

    @property
    def rising_edge(self):
        return self._detect_edge(high=True)

    @property
    def falling_edge(self):
        return self._detect_edge(high=False)

    def _check_level(self, high=True):
        if self.check_gate(high):
            self.triggers[high] = True
            return True
        return False

    @property
    def gate_on(self):
        return self._check_level(high=True)

    @property
    def gate_off(self):
        if self._check_level(high=False):
            self.triggers[True] = False
            return True
        else:
            return False
        return self._check_level(high=False)

    def lights_out(self):
        for out in self.outs:
            out.value = 0
