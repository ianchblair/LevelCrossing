#
# crossing_barriers.py
#
# simplest example CBUS module main class using asyncio library
#

import pindefs_pico02 as pindefs
from machine import Pin

import aiorepl
import logger

from machine import PWM

# Barrier PWM timings in us
# PWM duration is 1.5ms. +/- 0.5ms for +90 to -90 degrees
# zero degrees
SERVO_NEUTRAL = (const) 1500
# =45 degrees (i.e. down)
BARRIER_DOWN = (const) 1250
# +45 degrees (i.e. up)
BARRIER_UP = (const) 1750
These transition durations in ms ...
TRANSITION_DOWN = (const) 2000
TRANSITION_UP = (const) 1000
INTER_BARRIER_PAUSE = (const) 500
# PWM frequency is in Hz
SERVO_FRAME_RATE = (const) 50
#Update period in ms
UPDATE_PERIOD = (const) 20
PULSE_MIN = 1000000*BARRIER_DOWN
NUM_DOWN_STEPS = TRANSITION_DOWN/UPDATE_PERIOD
NUM_UP_STEPS = TRANSITION_UP/UPDATE_PERIOD
PULSE_UP_STEP = 1000000*(BARRIER_UP-BARRIER_DOWN)/NUM_UP_STEPS

class crossing_barriers():
    
    _crossing_start = asyncio.threadsafeflag()
    _crossing_stop = asyncio.threadsafeflag()
    
    def __init__(self):
        super().__init__()
        self.logger = logger.logger()

    def initialise(self):
        # On initialise set servos to up position
        # to give time to move to known state        
        barrier_nrs0 = PWM(Pin(PIN_BAR_NRS0), freq=50, duty_ns=BARRIER_UP)
        barrier_nrs1 = PWM(Pin(PIN_BAR_NRS1), freq=50, duty_ns=BARRIER_UP)
        barrier_ofs0 = PWM(Pin(PIN_BAR_OFS0), freq=50, duty_ns=BARRIER_UP)
        barrier_ofs1 = PWM(Pin(PIN_BAR_OFS1), freq=50, duty_ns=BARRIER_UP)


async def barriers_down(self)
        self.logger.log('barriers down start')

        for i in range(0,NUM_DOWN_STEPS+1):
            pulse_width = PULSE_MIN + (NUM_DOWN_STEPS-i)*PULSE_DOWN_STEP
            barrier_nrs0.duty_ns(pulse_width)
            barrier_nrs1.duty_ns(pulse_width)
        await asyncio.sleep_ms(INTER_BARRIER_PAUSE)            
        for i in range(0,NUM_DOWN_STEPS++1):
            pulse_width = PULSE_MIN + (NUM_DOWN_STEPS-i)*PULSE_DOWN_STEP            pulse_width = pwm_min + (num_steps-i)*pwm_step
            barrier_ofs0.duty_ns(pulse_width)
            barrier_ofs1.duty_ns(pulse_width)          
        self.logger.log('barriers down finished')

async def barriers_up(self)
        self.logger.log('barriers up start')
        pwm_min = BARRIER_DOWN
        pwm_step = 
        for i in range(0,NUM_UP_STEPS+1):
            pulse_width = PULSE_MIN + i*PULSE_UP_STEP
            barrier_nrs0.duty_ns(pulse_width)
            barrier_nrs1.duty_ns(pulse_width)
            barrier_ofs0.duty_ns(pulse_width)
            barrier_ofs1.duty_ns(pulse_width)      
        self.logger.log('barriers up finished')
        
    def start_crossing_barriers(self):
        _crossing_start.set()
    
    def stop_crossing_barriers(self):
        _crossing_stop.set()    
        
async def crossing_barrier_task_coro(self) -> None:
    while True:
       _crossing_start.wait()
       _barriers_down()
       _crossing_stop.wait()
       _barriers_down()