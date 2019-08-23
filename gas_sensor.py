# Mark Stambaugh
# 2019/07/25
# gas_sensor class for dealing with Alphasense array of gas sensors


class GasSensor:

    def __init__(self, name, cal_data={}):
        self.name = name
        self.we0 = cal_data["WE0"]
        self.ae0 = cal_data["AE0"]
        self.temp_coefficients = cal_data["TEMP"]
        self.sens_mV_per_ppb = cal_data["SENS"]
        self.ppb = 0
        self.AE_mV = 0
        self.WE_mV = 0
        self.temp_C = 20

    def calc_ppb(self, temp):
        self.temp = temp
        n = self.temp_coefficients[10*round(self.temp/10)]
        self.ppb = ((self.we-self.we0) - n*(self.ae - self.ae0))/self.sens_mV_per_ppb
        return self.ppb



