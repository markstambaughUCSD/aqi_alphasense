# Mark Stambaugh
# 2019/07/25
# mux class for dealing with a 16-to-1 or or more multiplexer

import gpio


class Mux:
    """Mux class to set number of channels, enable pin, active high or low """

    def __init__(self, number_of_channels, enable_pin, select_pins=[], active_low=True):
        if number_of_channels > 1:
            self.number_of_channels = number_of_channels
        else:
            print "invalid number of channels: {0}".format(number_of_channels)
            return

        if 2**len(select_pins) >= number_of_channels:
            self.select_pins = []
            for i in range(0,len(select_pins)):
                self.select_pins.append(gpio.Gpio(select_pins[i]))
                self.select_pins[i].set_direction(gpio.OUTPUT)
                self.select_pins[i].set_value(gpio.LOW)
                self.current_channel = 0
        else:
            print "insufficient select pins"
            return

        self.active_low = active_low
        self.enable_pin = gpio.Gpio(enable_pin)
        self.enable_pin.set_direction(gpio.OUTPUT)
        if self.active_low:
            self.enable_pin.set_value(gpio.HIGH)
        else:
            self.enable_pin.set_value(gpio.LOW)

    def enable(self):
        if self.active_low:
            self.enable_pin.set_value(gpio.LOW)
        else:
            self.enable_pin.set_value(gpio.HIGH)

    def disable(self):
        if self.active_low:
            self.enable_pin.set_value(gpio.HIGH)
        else:
            self.enable_pin.set_value(gpio.LOW)

    def select_channel(self, channel):
        if channel in range(0, self.number_of_channels):
            for i in range(0, len(self.select_pins)):
                self.select_pins[i].set_value((channel & 2**i) >> i)
            self.current_channel = channel
        else:
            print "invalid channel: {0}".format(channel)

