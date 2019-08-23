# Mark Stambaugh
# 2019/07/25
# adc class for dealing with UDOO's on-board ADC

PINS = {"A0": 0, "A1": 1, "A2": 2, "A3": 3, "A4": 4, "A5": 5}

MODES = ["bits", "mV", "V"]


class ADC:
    """ADC class to handle conversion and arithmetic"""
    def __init__(self, pin="A0"):
        if pin in PINS:
            self.pin = PINS[pin]
            self.val_str = "/sys/bus/iio/devices/iio:device" + str(self.pin/4) + "/in_voltage" + str(self.pin % 4) + "_raw"
            self.LUT_bits = [0, 4095]
            self.LUT_mV = [0, 3300]
            self.oversample = 1
            self.value_mV = 0
            self.value_bits = 0
        else:
            print "invalid ADC pin assignment"
            return

    # simple linear interpolation. LUT_bits must ascend
    def bits_to_mV(self, bits_in):
        if len(self.LUT_bits) != len(self.LUT_mV):
            print "ADC interpolation LUT size mismatch"
            return -1
        mV_out = 0
        bits_in = float(bits_in)
        if bits_in < self.LUT_bits[0]:  # input is below cal range. Extrapolate.
            mV_out = self.LUT_mV[0] - (self.LUT_bits[0] - bits_in) * (self.LUT_mV[1] - self.LUT_mV[0]) / (self.LUT_bits[1] - self.LUT_bits[0])
        elif bits_in < self.LUT_bits[-1]: # input is in cal range. Interpolate.
            for k in range(0, len(self.LUT_bits)-1):
                if bits_in < self.LUT_bits[k+1]:
                    mV_out = self.LUT_mV[k] + (bits_in - self.LUT_bits[k]) * (self.LUT_mV[k+1] - self.LUT_mV[k]) / (self.LUT_bits[k+1] - self.LUT_bits[k])
                    break
        else:  # input is above cal range. Extrapolate.
            mV_out = self.LUT_mV[-1] + (bits_in - self.LUT_bits[-1]) * (self.LUT_mV[-1] - self.LUT_mV[-2]) / (self.LUT_bits[-1] - self.LUT_bits[-2])
        return mV_out

    # oversamples the ADC reading and converts to straight bits, milliVolt, Volt outputs
    def read(self, mode="mV"):
        if mode in MODES:
            raw = 0
            for i in range(0, self.oversample):
                raw += int(open(self.val_str, 'r').read())
            self.value_bits = int(raw/self.oversample)
            self.value_mV = self.bits_to_mV(self.value_bits)
            if mode == "bits":
                return self.value_bits
            elif mode == "mV":
                return self.value_mV
            elif mode == "V":
                return self.value_mV/1000
        else:
            print "invalid mode: {0}".format(mode)
            return 0

