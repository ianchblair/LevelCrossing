#
# module_level_crossing.py
#
# simplest example CBUS module main class using asyncio library
#

import uasyncio as asyncio
from machine import Pin

import aiorepl
import cbus
import cbusconfig
import cbusdefs
import cbusmodule
import logger
import mcp2515

import crossing_barriers
import crossing_lights


class mymodule(cbusmodule.cbusmodule):
    def __init__(self):
        super().__init__()
        self.logger = logger.logger()

    def initialise(self):

        # ***
        # *** bare minimum module init
        # ***

        self.cbus = cbus.cbus(
            mcp2515.mcp2515(),
            cbusconfig.cbusconfig(storage_type=cbusconfig.CONFIG_TYPE_FILES),
        )

        # ** change the module name and ID if desired

        self.module_id = 103
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
            7,
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

        self.cbus.set_leds(21, 20)
        self.cbus.set_switch(22)
        self.cbus.set_name(self.module_name)
        self.cbus.set_params(self.module_params)
        self.cbus.set_event_handler(self.event_handler)
        self.cbus.set_received_message_handler(self.received_message_handler)
        self.cbus.set_sent_message_handler(self.sent_message_handler)

        self.cbus.begin()

        # ***
        # *** end of bare minimum init

        # ***
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

        # switch the LED on or off according to the event opcode
        if ev1 < 8:
            if msg.data[0] & 1:        # off events are odd numbers
                self.logger.log(f'** Crossing {ev1} off')
                #self.pins[ev1].off()
                self.tg.crossing_gates(up)
                self.tl.crossing_lights(off)
            else:                      # on events are even numbers
                self.logger.log(f'** Crossing {ev1} on')
                self.pins[ev1].on()
                self.tg.crossing_gates(down)
                self.tl.crossing_lights(on)  

    # ***
    # *** coroutines that run in parallel
    # ***

    # *** task to blink the onboard LED
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

    # *** user module application task - like Arduino loop()
    async def module_main_loop_coro(self) -> None:
        self.logger.log('main loop coroutine start')
        while True:
            await asyncio.sleep_ms(25)

    # ***
    # *** module main entry point - like Arduino setup()
    # ***

    async def run(self) -> None:
        # self.logger.log('run start')

        # start coroutines
        self.tb = asyncio.create_task(self.blink_led_coro())
        self.tg = asyncio.create_task(self.crossing_gates_coro())
        self.tl = asyncio.create_task(self.crossing_lights_coro())
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
