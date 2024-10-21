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


class Trigger:
    __slots__ = "gate_on", "edge_rising", "edge_falling"


class Uncertainty(Hardware):

    def __init__(self, outputMode='digital'):
        if (outputMode == 'digital'):
            self.outs = [self._set_digital_IO(pin) for pin in self.pins]
        elif (outputMode == 'pwm'):
            self.outs = [self._set_pwm_out(pin) for pin in self.pins]
        self.high_thresh = 50000 # just under 3v
        self.low_thresh = 40000 # around 1v

        self.saw_falling = self.saw_rising = False
        Trigger.gate_on = Trigger.edge_rising = Trigger.edge_falling = False

    def state(self):
        while True:
            level = self.adc.value
            if level > self.high_thresh:
                Trigger.gate_on = True
                Trigger.edge_falling = False
                Trigger.edge_rising = not self.saw_rising

                self.saw_falling = False
                self.saw_rising = True

            elif level < self.low_thresh:
                Trigger.gate_on = False
                Trigger.edge_rising = False
                Trigger.edge_falling = not self.saw_falling

                self.saw_rising = False
                self.saw_falling = True
            yield Trigger

    def lights_out(self):
        for out in self.outs:
            out.value = 0
