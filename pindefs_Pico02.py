# Definitions for IB Pico projects

# GPIOs

# Thes for Waveshare (B) MCP interface
PIN_CAN_MISO = const(12)
PIN_CAN_CS0 =  const(13)
PIN_CAN_CLK =  const(10)
PIN_CAN_MOSI = const(11)
PIN_CAN_INT1 = const(14)

# These for CBUS configuration
PIN_LED_YEL =  const(15)
PIN_LED_GRN =  const(9)
PIN_LED_RED =  const(8)
PIN_SW1 =      const(22)

# Level crossing warning lights
PIN_WRN_GRN =  const(0)
PIN_WRN_BLU =  const(1)
PIN_WRN_RED =  const(2)
PIN_WRN_YEL =  const(3)

# Level crossing barrier servos
# Note that adjacent pairs of pins must share PWM frequency
# Probably not an issue, but nearside and offside barriers grouped sparately
PIN_BAR_NRS0 =  const(4)
PIN_BAR_NRS1 =  const(5)
PIN_BAR_OFS0 =  const(6)
PIN_BAR_OFS1 =  const(7)

