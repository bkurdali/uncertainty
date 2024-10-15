import time
import board
import digitalio
from analogio import AnalogIn
import pwmio


class Hardware:
    """ Try to keep board specific/magic values and functions in one place """
    pwm_freq = 1000000
    pins = ["D1", "D2", "D3", "D6", "D10", "D9", "D8", "D7"] # Board specific
    adc_pin = "A0" # Board specific
    OUTPUT, INPUT = (digitalio.Direction.OUTPUT, digitalio.Direction.INPUT)

    adc = AnalogIn(getattr(board, adc_pin))

    def _set_digital_IO(pin_id, direction=OUTPUT):
        """ Sets an on/off pin (in or out based on direction)"""
        pin = digitalio.DigitalInout(getattr(board, pin_id))
        pin = direction
        return pin

    def _set_pwm_out(pin_id, frequency=pwm_frequency, duty_cycle=0):
        """ Sets a PWM output pin"""
        return pwmio.PWMOut(
            getattr(board, pin_id),
            frequency=frequency, duty_cycle=duty_cycle)


class Uncertainty(Hardware):

    def __init__(self, outputMode='digital', loop=None):
        # self.adc = AnalogIn(getattr(board, self.adc_pin))
        if (outputMode == 'digital'):
            self.outs = [self._set_digital_IO(pin) for pin in self.pins]
        elif (outputMode == 'pwm'):
            self.outs = [self._set_pwm_out(pin) for pin in self.pins]
        self.high_thresh = 50000 # just under 3v
        self.low_thresh = 40000 # around 1v
        self.triggers = [False, False] # [Falling, Rising]

    def check_gate(self, high=True):
        if high:
            return self.adc.value > self.high_thresh
        return self.adc.value < self.low_thresh

    def _detect_edge(self, high=True):
        """ Detect a high(True) or low(False) edge """
        if not self.check_gate(high=high): # didn't trigger
            self.triggers[high] = False
            return False
        if self.triggers[high]: # already triggered
            return False
        # new edge
        self.triggers[high] = True
        return True

    def gaterator(self):
        while True:
            yield self._detect_edge(high=True)

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
        return self._check_level(high=False)

    def lights_out(self):
        for out in self.outs:
            out.value = 0
