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

import aiorepl
import logger

_OPTO_OFF = const(0)
_OPTO_ON = const(1)
_YELLOW_ON_TIME = const(4000)
_RED_ON_TIME = const(500)

class crossing_lights():
    def __init__(self):
        super().__init__()
        self.logger = logger.logger()

    def initialise(self):
        _lights_start = asyncio.threadsafeflag()
        _lights_stop = asyncio.threadsafeflag()
        self._flasher = Timer()
        _warning_yellow = Pin(PIN_WRN_YEL,Pin.OUT)
        _warning_red =    Pin(PIN_WRN_RED,Pin.OUT)
        _warning_green =  Pin(PIN_WRN_GRN,Pin.OUT)
        _warning_blue =   Pin(PIN_WRN_BLU,Pin.OUT)
        _self.lights_off()
        # ***
        # ***
                
    def lights_off(self):
        _warning_yellow.value =_OPTO_OFF
        _warning_red.value    =_OPTO_OFF
        _warning_blue.value   =_OPTO_OFF
        _warning_green.value  =_OPTO_OFF
 
    def _yellow(self):
        _warning_yellow.value =_OPTO_ON
        _warning_red.value    =_OPTO_OFF
        _warning_blue.value   =_OPTO_OFF
        _warning_green.value  =_OPTO_ON

    def _red_left(self):
        _warning_yellow.value =_OPTO_OFF
        _warning_red.value    =_OPTO_ON
        _warning_blue.value   =_OPTO_ON
        _warning_green.value  =_OPTO_OFF

    def _red_right(self):
        _warning_yellow.value =_OPTO_OFF
        _warning_red.value    =_OPTO_OFF
        _warning_blue.value   =_OPTO_ON
        _warning_green.value  =_OPTO_ON        

    def _red_both(self):
        _warning_yellow.value =_OPTO_OFF
        _warning_red.value    =_OPTO_ON
        _warning_blue.value   =_OPTO_ON
        _warning_green.value  =_OPTO_ON          

    # ***
    # *** coroutines that run in parallel
    # ***
    
    def yellow_lights(self):
        self.logger.log('yellow_warning start')
        self._yellow()
        await asyncio.sleep_ms(_YELLOW_ON_TIME)
        
    # *** Flash red lights
    # *** 
    def red_lights(self):
        # Start flashing on left
        self._now_left = True        
        self.logger.log('blink_red_warning start')
        
        # Brief phase of both red LEDS
        self._red_both()
        await asyncio.sleep_ms(_RED_ON_TIME)
        
        # For flashing lights we establish a callback
        self._flasher.init(period=_RED_ON_TIME, mode=Timer.PERIODIC, callback=swap_red_lights)
        
    def swap_red_lights(self):
        if (self._now_left == True):
            self._red_left()
            self._now_left = False
        else:
            self._red_right()
            self._now_left = True

    def stop_red_lights(self):
            self._lights_off()
            self._flasher.deint()
        
    def start_crossing_lights(self):
        self._lights_start.set()
    
    def stop_crossing_lights(self):
        self._lights_stop.set()    
        
    async def crossing_light_coro(self) -> None:
        while True:
            self._lights_start.wait()
            self._yellow_lights()
            self._red_lights()
            self._lights_stop.wait()
            self._red_lights()
            
    # *** task to blink the onboard LED
    async def blink_test_led(self) -> None:
        self.logger.log('blink_red_warning start')
        try:
            led = Pin('LED', Pin.OUT)
        except TypeError:
            led = Pin(25, Pin.OUT)
        while True:
            led.value(1)
            await asyncio.sleep_ms(20)
            led.value(0)
            await asyncio.sleep_ms(980)

# the asyncio scheduler is now in control
# no code after this line is executed

print('*** to be completed ***')
