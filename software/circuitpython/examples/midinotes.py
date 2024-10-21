midi_notes = [60, 61, 62, 63, 64, 65, 66, 67]


import time
import board
import digitalio
from analogio import AnalogIn
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange
from adafruit_midi.pitch_bend import PitchBend

from oam import Uncertainty

unc = Uncertainty()

midi = adafruit_midi.MIDI(
    midi_in=usb_midi.ports[0],
    midi_out=usb_midi.ports[1],
    in_channel=0,
    out_channel=0,
    debug=False,
)

old_cv = 0
last_cc_val = 0

cv_min = 5900
cv_max = 64300
usable_rangle = cv_max - cv_min

def play_note(note, state):
    for i in range(0, len(midi_notes)):
        if midi_notes[i] == note:
            unc.outs[i].value = state
            return

while True:

    #get the midi from usb and send it out as eurorack gates
    msg = midi.receive()
    if msg is not None:
        if isinstance(msg, NoteOn):
            if msg.note in midi_notes:
                play_note(msg.note, msg.velocity > 0)

        if isinstance(msg, NoteOff):
            if msg.note in midi_notes:
                play_note(msg.note, False)

    # get the cv in from eurorack and send it as a midi controller
        # lets only do this stuff if the raw data has actually by a significant amount
    new_cv = unc.adc.value
    if abs(old_cv - new_cv) > 256:
        # convert the 16-bit incoming value to a 7-bit value for midi control changes
        cv_raw = min(max(new_cv, cv_min), cv_max)

        ctl_val = int((((cv_raw - cv_min) * 127) / usable_rangle) + 0)

        if ctl_val is not last_cc_val:
            cc = ControlChange(1, ctl_val)
            midi.send(cc)

        # store old values for next cycle
        old_cv = new_cv
        last_cc_val = ctl_val
