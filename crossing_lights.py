#
# crossing_lights.py
#

# This probably needs to run as a coroutine - TBA

import pindefs_pico02 as pindefs
from machine import Pin

import aiorepl
import logger

_OPTO_OFF = (const) 0
_OPTO_ON = (const) 1
_YELLOW_ON_TIME = (const) 4000
_RED_ON_TIME = (const) 500
_flashing - false

class crossing_lights():
    
    _crossing_start = asyncio.threadsafeflag()
    _crossing_stop = asyncio.threadsafeflag()
    
    def __init__(self):
        super().__init__()
        self.logger = logger.logger()

    def initialise(self):
        self.lights_off()
        
        
    def lights_off(self):
        warning_yellow = Pin(PIN_WRN_YEL,Pin.OUT,value=_OPTO_OFF)
        warning_red =    Pin(PIN_WRN_RED,Pin.OUT,value=_OPTO_OFF)
        warning_blue =   Pin(PIN_WRN_BLU,Pin.OUT,value=_OPTO_OFF)
        warning_green =  Pin(PIN_WRN_GRN,Pin.OUT,value=_OPTO_OFF)
 
    def _yellow(self):
        warning_yellow = Pin(PIN_WRN_YEL,Pin.OUT,value=_OPTO_ON)
        warning_red =    Pin(PIN_WRN_RED,Pin.OUT,value=_OPTO_OFF)
        warning_blue =   Pin(PIN_WRN_BLU,Pin.OUT,value=_OPTO_OFF)         warning_green =  Pin(PIN_WRN_GRN,Pin.OUT,value=_OPTO_OFF)       
        warning_green =  Pin(PIN_WRN_GRN,Pin.OUT,value=_OPTO_ON)

    def _red_left(self):
        warning_yellow = Pin(PIN_WRN_YEL,Pin.OUT,value=_OPTO_OFF)
        warning_red =    Pin(PIN_WRN_RED,Pin.OUT,value=_OPTO_ON)
        warning_blue =   Pin(PIN_WRN_BLU,Pin.OUT,value=_OPTO_ON)        
        warning_green =  Pin(PIN_WRN_GRN,Pin.OUT,value=_OPTO_OFF)


    def _red_right(self):
        warning_yellow = Pin(PIN_WRN_YEL,Pin.OUT,value=OPTO_OFF)
        warning_red =    Pin(PIN_WRN_RED,Pin.OUT,value=OPTO_OFF)
        warning_green =  Pin(PIN_WRN_GRN,Pin.OUT,value=OPTO_ON)
        warning_blue =   Pin(PIN_WRN_BLU,Pin.OUT,value=OPTO_ON)
        

    def _red_both(self):
        warning_yellow = Pin(PIN_WRN_YEL,Pin.OUT,value=OPTO_OFF)
        warning_red =    Pin(PIN_WRN_RED,Pin.OUT,value=OPTO_ON)
        warning_green =  Pin(PIN_WRN_GRN,Pin.OUT,value=OPTO_ON)
        warning_blue =   Pin(PIN_WRN_BLU,Pin.OUT,value=OPTO_ON)    # *** Yellow warning phase
    # ***
    
    def yellow_lights(self):
        self.logger.log('yellow_warning start')
        self._yellow()
        await asyncio.sleep_ms(_YELLOW_ON_TIME)
        
    # *** Flash red lights
    # *** 
    def red_lights(self):
        # Set flashing flag immediately, to catch early stop cases
        _flashing = True        
        self.logger.log('blink_red_warning start')
        
        # Brief phase of both red LEDS
        self._red_both()
        await asyncio.sleep_ms(_RED_ON_TIME)
        
        while _flashing
            self._red_left()
            await asyncio.sleep_ms(_RED_ON_TIME)
            self._red_right()           
            await asyncio.sleep_ms(_RED_ON_TIME)
            if (_crossing_stop.state == true) _flashing = False
        self._lights_off()
            

    def stop_red_lights(self):
        _flashing = false
        
    def start_crossing_lights(self):
        _crossing_start.set()
    
    def stop_crossing_lights(self):
        _crossing_stop.set()    
        
async def crossing_light_task_coro(self) -> None:
    while True:
       _crossing_start.wait()
       _yellow_lights()
       _red_lights()
    