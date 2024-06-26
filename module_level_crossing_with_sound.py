#
# module_level_crossing.py
#
# simplest example CBUS module main class using asyncio library
#
# (c) Ian Blair 3rd. April 2024
#

import uasyncio as asyncio
from machine import Pin,SPI
import time
import pindefs_Pico02 as pindefs
from picodfplayer import DFPlayer

import aiorepl
import cbus
import cbusconfig
import cbusdefs
import cbusmodule
import logger
import mcp2515
import crossing_barriers
import crossing_lights

_YELLOW_ON_TIME = const(4000)
_RED_ON_TIME = const(333)

# Barrier PWM timings in us
# PWM duration is 1.5ms. +/- 0.5ms for +90 to -90 degrees
# zero degrees
SERVO_NEUTRAL = const(1500)
# =45 degrees (i.e. down)
BARRIER_DOWN = const(1250)
# +45 degrees (i.e. up)
BARRIER_UP = const(1750)
# These transition durations in ms ...
TRANSITION_DOWN = const(2000)
TRANSITION_UP = const(1500)
BARRIER_DELAY = const(6000)
INTER_BARRIER_PAUSE = const(1500)
# PWM frequency is in Hz
SERVO_FRAME_RATE = const(50)
#Update period in ms
UPDATE_PERIOD = const(20)
PULSE_MIN = 1000*BARRIER_DOWN
PULSE_INIT = 1000*BARRIER_UP
NUM_DOWN_STEPS = TRANSITION_DOWN/UPDATE_PERIOD
NUM_UP_STEPS = TRANSITION_UP/UPDATE_PERIOD
PULSE_DOWN_STEP = int(1000*(BARRIER_UP-BARRIER_DOWN)/NUM_DOWN_STEPS)
PULSE_UP_STEP = int(1000*(BARRIER_UP-BARRIER_DOWN)/NUM_UP_STEPS)

SOUND_VOLUME =  int(20)
SOUND_BAR_DOWN_TRK = const(6)
SOUND_BAR_UP_TRK = const(3)

class mymodule(cbusmodule.cbusmodule):
    def __init__(self):
        super().__init__()
        self.logger = logger.logger()
        self._lights_start = asyncio.ThreadSafeFlag()
        self._lights_stop = asyncio.ThreadSafeFlag()
        self._lights_stop_event = asyncio.Event()
        self._barriers_start = asyncio.ThreadSafeFlag()
        self._barriers_stop = asyncio.ThreadSafeFlag()
        self._event_led = Pin(pindefs.PIN_LED_RED, Pin.OUT)
        self._sound_available = True
 
    def initialise(self):
        # ***
        # *** Module init
        # ***
        # SPI pin configuration from pindefs
        bus = SPI(
            1,
            baudrate=10_000_000,
            polarity=0,
            phase=0,
            bits=8,
            firstbit=SPI.MSB,
            sck=Pin(pindefs.PIN_CAN_CLK),
            mosi=Pin(pindefs.PIN_CAN_MOSI),
            miso=Pin(pindefs.PIN_CAN_MISO),)
        self.cbus = cbus.cbus(
            mcp2515.mcp2515(osc=16_000_000, cs_pin=pindefs.PIN_CAN_CS0, interrupt_pin=pindefs.PIN_CAN_INT1, bus=bus),
            cbusconfig.cbusconfig(storage_type=cbusconfig.CONFIG_TYPE_FILES),
        )

        # ** change the module name and ID if desired

        self.module_id = 107
        self.module_name = bytes('LEVCR  ', 'ascii')
        self.module_params = [
            20,
            cbusdefs.MANU_MERG,
            0,
            self.module_id,
            self.cbus.config.num_events,
            self.cbus.config.num_evs,
            self.cbus.config.num_nvs,
            1,
            # Parameter below sets PF flags. 6 sets Consumer and Producer node, 
            # but only Consumer node functionality is implemented so far.
            6,
            0,
            cbusdefs.PB_CAN,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]

        # change the CBUS switch and LED pin numbers if desired

        self.cbus.set_leds(pindefs.PIN_LED_GRN,pindefs.PIN_LED_YEL)
        self.cbus.set_switch(pindefs.PIN_SW1)
        self.cbus.set_name(self.module_name)
        self.cbus.set_params(self.module_params)
        self.cbus.set_event_handler(self.event_handler)
        self.cbus.set_received_message_handler(self.received_message_handler)
        self.cbus.set_sent_message_handler(self.sent_message_handler)

        self.cbus.begin()

        # ***
        # *** Instantiate barrier and light clusses
        self.cl = crossing_lights.crossing_lights()
        self.cb = crossing_barriers.crossing_barriers()

        self.cb.initialise_barriers(PULSE_INIT)

        self._event_led.value(0)
        self._sound_player=DFPlayer(uartInstance=0, txPin=pindefs.PIN_SND_TXD, rxPin=pindefs.PIN_SND_RXD, busyPin=pindefs.PIN_SND_BSY, myLog=self.logger)

#        try:
#            self._sound_player.begin(isAck=True, doReset=True, useAsyncio=True)
#            self.logger.log('Sound available')
#        except:
#            self._sound_available = False
#            self.logger.log('Sound not available')
#            
#        if (self._sound_available):
#            self._sound_player.setVolume(SOUND_VOLUME)
        self.logger.log('Sound init start')
        self._sound_player.begin(isAck=False, doReset=True, useAsyncio=True)
        # Allow reset to happen
        time.sleep_ms(2000)
        self.logger.log('Sound player begun')
        
        self._sound_player.setVolume(SOUND_VOLUME)
        time.sleep_ms(500)
        
        # *** module initialisation complete
        self.logger.log(f'module: name = <{self.cbus.name.decode()}>, mode = {self.cbus.config.mode}, can id = {self.cbus.config.canid}, node number = {self.cbus.config.node_number}')
        self.logger.log(f'free memory = {self.cbus.config.free_memory()} bytes')

        
        # *** end of initialise method
        
          # ***
    # *** CBUS event handler -- called whenever a previously taught event is received
    # *** when teaching, set the value of EV1 to select the LED to control (0-7)
    # ***

    def event_handler(self, msg: canmessage.canmessage, idx: int) -> None:
        self.logger.log(f'-- event handler: idx = {idx}: {msg}')

        # lookup the value of the 1st EV
        ev1 = self.cbus.config.read_event_ev(idx, 1)
        self.logger.log(f'** idx = {idx}, opcode = {msg.data[0]}, polarity = {"OFF" if msg.data[0] & 1 else "ON"}, ev1 = {ev1}')

        # switch the crossing on or off according to the event opcode
        # On in this context means gates down and lights on
        if ev1 < 8:
            if not (msg.data[0] & 1):        # on events are even numbers
                self.logger.log(f'** Crossing {ev1} on')
                self._barriers_start.set()
                self._lights_start.set()
                self._event_led.value(1) 
            else:                      # off events are pdd numbers
                self.logger.log(f'** Crossing {ev1} off') 
                self._barriers_stop.set()
                # An event is used here because the flag needs to be polled
                # If this doesn't work from a task is needed to convert
                # the ThreadSafeFlag to an asyncio Event
                #self._lights_stop.set()
                self._lights_stop_event.set()
                self._event_led.value(0) 
    # ***
    # *** coroutines that run in parallel
    # ***

    # *** task to blink the onboard LED
    # to show that program is running
    async def blink_led_coro(self) -> None:
        self.logger.log('blink_led_coro start')
        try:
            led = Pin('LED', Pin.OUT)
        except TypeError:
            led = Pin(25, Pin.OUT)
        while True:
            led.value(1)
            await asyncio.sleep_ms(20)
            led.value(0)
            await asyncio.sleep_ms(980)
            
# This asynchronous task for lights
    async def crossing_lights_coro(self) -> None:
        self.logger.log('crossing_lights_coro start')
        while True:
            await self._lights_start.wait()
            self.logger.log('yellow on')
            self.cl.yellow_lights()
            await asyncio.sleep_ms(_YELLOW_ON_TIME)
            self.logger.log('yellow done')
            self.cl.red_lights()
            self.logger.log('red done')
            await asyncio.sleep_ms(_RED_ON_TIME)
            while (self._lights_stop_event.is_set() == False):
                self.cl.swap_red_lights()
                self.logger.log('flashing red swap')
                await asyncio.sleep_ms(_RED_ON_TIME)
            self._lights_stop_event.clear()
            self.logger.log('flashing red done')
            self._lights_stop.wait()
            self.cl.stop_red_lights()
            self.logger.log('crossing_lights_coro end of loop')
                   
# *** user module application task - like Arduino loop()
# used for barriers
    async def module_main_loop_coro(self) -> None:
        self.logger.log('main loop coroutine start')
        while True:
            await self._barriers_start.wait()
            if (self._sound_available):
                self.logger.log('Playing barrier down')
                self._sound_player.play(SOUND_BAR_DOWN_TRK)
            await asyncio.sleep_ms(BARRIER_DELAY)

            for i in range(0,NUM_DOWN_STEPS+1):
                pulse_width = int(PULSE_MIN + (NUM_DOWN_STEPS-i)*PULSE_DOWN_STEP)
                self.cb.nearside_barriers(pulse_width)
                await asyncio.sleep_ms(UPDATE_PERIOD)
            await asyncio.sleep_ms(INTER_BARRIER_PAUSE)
            for i in range(0,NUM_DOWN_STEPS+1):
                pulse_width = int(PULSE_MIN + (NUM_DOWN_STEPS-i)*PULSE_DOWN_STEP)
                self.cb.offside_barriers(pulse_width)
                await asyncio.sleep_ms(UPDATE_PERIOD)
            self._sound_player.pause()
            
            await self._barriers_stop.wait()
            if (self._sound_available):
                self._sound_player.play(SOUND_BAR_UP_TRK)
            
            for i in range(0,NUM_UP_STEPS+1):
                pulse_width = int(PULSE_MIN + i*PULSE_UP_STEP)
                self.cb.bothside_barriers(pulse_width)
                await asyncio.sleep_ms(UPDATE_PERIOD)
            self._sound_player.pause()
            self.logger.log('barrier loop end')                
    # ***
    # *** module main entry point - like Arduino setup()
    # ***

    async def run(self) -> None:
        # self.logger.log('run start')

        # start coroutines
        self.tb = asyncio.create_task(self.blink_led_coro())
        self.tl = asyncio.create_task(self.crossing_lights_coro())
#        self.tg = asyncio.create_task(self.crossing_barriers_coro(())
        self.tm = asyncio.create_task(self.module_main_loop_coro())

        repl = asyncio.create_task(aiorepl.task(globals()))

        self.logger.log('module startup complete')
        await asyncio.gather(repl)


# create the module object and run it
mod = mymodule()
mod.initialise()
asyncio.run(mod.run())

# the asyncio scheduler is now in control
# no code after this line is executed

print('*** application has ended ***')
