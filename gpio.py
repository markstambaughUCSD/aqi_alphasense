# Mark Stambaugh
# 2019/07/25
# gpio class for dealing with digital GPIO pins on the UDOO board

INPUT = "in"
OUTPUT = "out"
HIGH = 1
LOW = 0


class Gpio:
    """ GPIO class to set direction, set value, read value"""


    def __init__(self, pin_number):
        self.pin = pin_number
        self.dir_str = "/gpio/pin" + str(self.pin) + "/direction"
        self.val_str = "/gpio/pin" + str(self.pin) + "/value"
        self.direction = open(self.dir_str, 'r').read()
        self.value = int(open(self.val_str, 'r').read())

    def set_direction(self, direction):
        if direction == INPUT or direction == OUTPUT:
            open(self.dir_str, 'w').write(direction)
            self.direction = direction
        else:
            print "pin {0} invalid direction: {1}".format(self.pin, direction)

    def set_value(self, value):
        if self.direction == OUTPUT:
            if value == HIGH or value == LOW:
                open(self.val_str, 'w').write(str(value))
                self.value = value
            else:
                print "pin {0} invalid value: {1}".format(self.pin, value)
        else:
            print "cannot set pin {0} (input)".format(self.pin)

    def read_value(self):
        self.value = int(open(self.val_str, 'r').read())
        return self.value


