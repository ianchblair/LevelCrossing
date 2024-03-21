#
# crossing_barriers.py
#
# simplest example CBUS module main class using asyncio library
#

import pindefs_Pico02 as pindefs
from machine import Pin
import uasyncio as asyncio

import aiorepl
import logger

from machine import PWM

# Barrier PWM timings in us
# PWM duration is 1.5ms. +/- 0.5ms for +90 to -90 degrees
# zero degrees
SERVO_NEUTRAL = const(1500)
# =45 degrees (i.e. down)
BARRIER_DOWN = const(1250)
# +45 degrees (i.e. up)
BARRIER_UP = const(1750)
# These transition durations in ms ...
BARRIER_DELAY = const(4000)
TRANSITION_DOWN = const(2000)
TRANSITION_UP = const(1000)
INTER_BARRIER_PAUSE = const(500)
# PWM frequency is in Hz
SERVO_FRAME_RATE = const(50)
#Update period in ms
UPDATE_PERIOD = const(20)
PULSE_MIN = 1000000*BARRIER_DOWN
NUM_DOWN_STEPS = TRANSITION_DOWN/UPDATE_PERIOD
NUM_UP_STEPS = TRANSITION_UP/UPDATE_PERIOD
PULSE_UP_STEP = int(1000000*(BARRIER_UP-BARRIER_DOWN)/NUM_UP_STEPS)

class crossing_barriers():
    def __init__(self):
        super().__init__()
        self.logger = logger.logger()
        self.barrier_nrs0 = PWM(Pin(pindefs.PIN_BAR_NRS0), freq=50, duty_ns=BARRIER_UP)
        self.barrier_nrs1 = PWM(Pin(pindefs.PIN_BAR_NRS1), freq=50, duty_ns=BARRIER_UP)
        self.barrier_ofs0 = PWM(Pin(pindefs.PIN_BAR_OFS0), freq=50, duty_ns=BARRIER_UP)
        self.barrier_ofs1 = PWM(Pin(pindefs.PIN_BAR_OFS1), freq=50, duty_ns=BARRIER_UP)

    def barriers_down(self):
        self.logger.log('barriers down started')
        # Delay before barriers to allow lights to do their thing
        await asyncio.sleep_ms(BARIER_DELAY)
        for i in range(0,NUM_DOWN_STEPS+1):
            pulse_width = PULSE_MIN + (NUM_DOWN_STEPS-i)*PULSE_DOWN_STEP
            self.barrier_nrs0.duty_ns(pulse_width)
            self.barrier_nrs1.duty_ns(pulse_width)
            await asyncio.sleep_ms(UPDATE_PERIOD)
        await asyncio.sleep_ms(INTER_BARRIER_PAUSE)            
        for i in range(0,NUM_DOWN_STEPS+1):
            pulse_width = PULSE_MIN + (NUM_DOWN_STEPS-i)*PULSE_DOWN_STEP
            self.barrier_ofs0.duty_ns(pulse_width)
            self.barrier_ofs1.duty_ns(pulse_width)
            await asyncio.sleep_ms(UPDATE_PERIOD)
        self.logger.log('barriers down finished')

    def barriers_up(self):
        self.logger.log('barriers up started')
        pwm_min = BARRIER_DOWN
        for i in range(0,NUM_UP_STEPS+1):
            pulse_width = PULSE_MIN + i*PULSE_UP_STEP
            self.barrier_nrs0.duty_ns(pulse_width)
            self.barrier_nrs1.duty_ns(pulse_width)
            self.barrier_ofs0.duty_ns(pulse_width)
            self.barrier_ofs1.duty_ns(pulse_width)
            await asyncio.sleep_ms(UPDATE_PERIOD)
        self.logger.log('barriers up finished')
  
        
 