#
# crossing_barriers.py
#
# Module for crossing barriers.
# This module only includes non-blocking I/O calls
# Timings are kept in main module, which uses (u)asyncio
#

import pindefs_Pico02 as pindefs
from machine import Pin

import aiorepl
import logger

from machine import PWM

class crossing_barriers():
    def __init__(self):
        super().__init__()
        self.logger = logger.logger()
        
    def initialise_barriers(self, pulse_width):        
        self.barrier_nrs0 = PWM(Pin(pindefs.PIN_BAR_NRS0), freq=50, duty_ns=pulse_width)
        self.barrier_nrs1 = PWM(Pin(pindefs.PIN_BAR_NRS1), freq=50, duty_ns=pulse_width)
        self.barrier_ofs0 = PWM(Pin(pindefs.PIN_BAR_OFS0), freq=50, duty_ns=pulse_width)
        self.barrier_ofs1 = PWM(Pin(pindefs.PIN_BAR_OFS1), freq=50, duty_ns=pulse_width)

    def nearside_barriers(self, pulse_width):
        self.barrier_nrs0.duty_ns(pulse_width)
        self.barrier_nrs1.duty_ns(pulse_width)
            
    def offside_barriers(self, pulse_width):
        self.barrier_ofs0.duty_ns(pulse_width)
        self.barrier_ofs1.duty_ns(pulse_width)        
        
    def bothside_barriers(self, pulse_width):    
        self.barrier_nrs0.duty_ns(pulse_width)
        self.barrier_nrs1.duty_ns(pulse_width)
        self.barrier_ofs0.duty_ns(pulse_width)
        self.barrier_ofs1.duty_ns(pulse_width)

        
 