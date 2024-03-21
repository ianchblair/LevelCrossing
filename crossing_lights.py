#
# crossing_lights.py
#
# Ian Nlair
#
# Designed to use MERG CBUS Library (Duncan Greenwood and others)
# Class for coroutine to control warning lights
#

import pindefs_Pico02 as pindefs
from machine import Pin,Timer
import uasyncio as asyncio

import aiorepl
import logger

_OPTO_OFF = const(0)
_OPTO_ON = const(1)
_YELLOW_ON_TIME = const(4000)
_RED_ON_TIME = const(500)
_FLASHING_RED_ON_TIME = const(500)

class crossing_lights():
    
    def __init__(self):
        super().__init__()
        self.logger = logger.logger()
        self._warning_yellow = Pin(pindefs.PIN_WRN_YEL,Pin.OUT)
        self._warning_red =    Pin(pindefs.PIN_WRN_RED,Pin.OUT)
        self._warning_green =  Pin(pindefs.PIN_WRN_GRN,Pin.OUT)
        self._warning_blue =   Pin(pindefs.PIN_WRN_BLU,Pin.OUT)
        self._flasher = Timer()
        self._now_left = False
        
    # def initialise(self):
        # self._lights_off()
        # ***
        # ***
                
    def _lights_off(self):
        self._warning_yellow.value(_OPTO_OFF)
        self._warning_red.value(_OPTO_OFF)
        self._warning_blue.value(_OPTO_OFF)
        self._warning_green.value(_OPTO_OFF)
 
    def _yellow(self):
        self._warning_yellow.value(_OPTO_ON)
        self._warning_red.value(_OPTO_OFF)
        self._warning_blue.value(_OPTO_OFF)
        self._warning_green.value(_OPTO_ON)

    def _red_left(self):
        self._warning_yellow.value(_OPTO_OFF)
        self._warning_red.value(_OPTO_ON)
        self._warning_blue.value(_OPTO_ON)
        self._warning_green.value(_OPTO_OFF)

    def _red_right(self):
        self._warning_yellow.value(_OPTO_OFF)
        self._warning_red.value(_OPTO_OFF)
        self._warning_blue.value(_OPTO_ON)
        self._warning_green.value(_OPTO_ON)        

    def _red_both(self):
        self._warning_yellow.value(_OPTO_OFF)
        self._warning_red.value(_OPTO_ON)
        self._warning_blue.value(_OPTO_ON)
        self._warning_green.value(_OPTO_ON)          

    # ***
    # *** coroutines that run in parallel
    # ***
    
    def yellow_lights(self):
        self.logger.log('yellow_warning start')
        self._yellow()
        
    # *** Flash red lights
    # *** 
    def red_lights(self):
        # Start flashing on left
        self._now_left = True        
        self.logger.log('red warning start')     
        # Brief phase of both red LEDS
        self._red_both()
#        await asyncio.sleep_ms(_RED_ON_TIME)
        
    def swap_red_lights(self):
        if (self._now_left == True):
            self._red_left()
            self._now_left = False
        else:
            self._red_right()
            self._now_left = True

    def flashing_red_lights(self):
        self.logger.log('flashing red_warning start')
        # For flashing lights we establish a callback
        self._flasher.init(period=_FLASHING_RED_ON_TIME, mode=Timer.PERIODIC, callback=self.swap_red_lights)

    def stop_red_lights(self):
            self._lights_off()
            self._flasher.deinit()
                            
print('*** End of crossing lights file ***')
