# Mark Stambaugh
# 2019/07/26
# Module for sensing the SDS011 PM2.5 PWM output

import pins
import gpio
from time import time


class PM:
    """PM class to read PWM outputs of SDS011 sensor"""

    def __init__(self, input_pin_2u5, input_pin_10u,):
        self.input_2u5 = gpio.Gpio(input_pin_2u5)
        self.input_2u5.set_direction(gpio.INPUT)
        self.concentration_2u5_ugpm3 = 0
        self.input_10u = gpio.Gpio(input_pin_10u)
        self.input_10u.set_direction(gpio.INPUT)
        self.concentration_10u_ugpm3 = 0

    def read_PM_2u5_ugpm3(self):
        start_time = time()  # start watchdog timer. Abort process after 2 seconds
        if self.input_2u5.read_value():
            # output is high. Wait for falling edge, then capture the time
            while self.input_2u5.read_value():
                if time() - start_time > 2:
		    self.concentration_2u5_ugpm3 = -1
                    return
            t_falling_edge_ms = 1000 * time()
            # wait for rising edge, then capture the time
            while not self.input_2u5.read_value():
                if time() - start_time > 2:
                    self.concentration_2u5_ugpm3 = -1
                    return
            t_rising_edge_ms = 1000*time()
            self.concentration_2u5_ugpm3 = 1000 - (t_rising_edge_ms - (t_falling_edge_ms + 2))
        else:
            # output is low. Wait for rising edge, then capture the time
            while not self.input_2u5.read_value():
                if time() - start_time > 2:
                    self.concentration_2u5_ugpm3 = -1
                    return
            t_rising_edge_ms = 1000*time()
            # output is high. Wait for falling edge, then capture the time
            while self.input_2u5.read_value():
                if time() - start_time > 2:
                    self.concentration_2u5_ugpm3 = -1
                    return
            t_falling_edge_ms = 1000 * time()
            self.concentration_2u5_ugpm3 = t_falling_edge_ms - t_rising_edge_ms - 2
        return self.concentration_2u5_ugpm3

    def read_PM_10u_ugpm3(self):
        start_time = time()  # start watchdog timer. Abort process after 2 seconds
        if self.input_10u.read_value():
            # output is high. Wait for falling edge, then capture the time
            while self.input_10u.read_value():
                if time() - start_time > 2:
                    self.concentration_10u_ugpm3 = -1
                    return
            t_falling_edge_ms = 1000 * time()
            # wait for rising edge, then capture the time
            while not self.input_10u.read_value():
                if time() - start_time > 2:
                    self.concentration_10u_ugpm3 = -1
                    return
            t_rising_edge_ms = 1000*time()
            self.concentration_10u_ugpm3 = 1000 - (t_rising_edge_ms - (t_falling_edge_ms + 2))
        else:
            # output is low. Wait for rising edge, then capture the time
            while not self.input_10u.read_value():
                if time() - start_time > 2:
                    self.concentration_10u_ugpm3 = -1
                    return
            t_rising_edge_ms = 1000*time()
            # output is high. Wait for falling edge, then capture the time
            while self.input_10u.read_value():
                if time() - start_time > 2:
                    self.concentration_10u_ugpm3 = -1
                    return
            t_falling_edge_ms = 1000 * time()
            self.concentration_10u_ugpm3 = t_falling_edge_ms - t_rising_edge_ms - 2
        return self.concentration_10u_ugpm3
