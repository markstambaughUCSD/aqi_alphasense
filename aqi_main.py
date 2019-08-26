# Mark Stambaugh
# 2019/07/26
# main module for the UDOO air quality sensor board

import pins
import mux
import adc
import cal
import gas_sensor
import PM
import TMP36
from time import time
import sqlite3

sample_period_s = 3
report_period_s = 10
run_time_s = 30

print "begin Air Quality Sensor"

# set up the analog mux
analog_mux = mux.Mux(16, pins.MUX_EN, pins.MUX_SEL, active_low=True)
analog_mux.select_channel(pins.CH_EMPTY)
analog_mux.enable()
print "mux initialized"

# set up the ADC reading the MUX output
mux_ADC = adc.ADC(pins.ADC_MUX)
mux_ADC.oversample = 16
LUT_bits = []
for i in pins.CH_REF:
    analog_mux.select_channel(i)
    LUT_bits.append(mux_ADC.read("bits"))
mux_ADC.LUT_bits = LUT_bits
mux_ADC.LUT_mV = pins.REF_mV
print "ADC initialized"

print mux_ADC.LUT_bits
print mux_ADC.LUT_mV
#mux_ADC.LUT_bits = [0, 4095] # TEST
#mux_ADC.LUT_mV = [0, 3300] # TEST

# set up the PM2.5, PM10 sensor
sensor_PM = PM.PM(pins.PM_2U5_PWM, pins.PM_10U_PWM)
#print sensor_PM.concentration_2u5_ugpm3
#print sensor_PM.concentration_10u_ugpm3
if sensor_PM.concentration_2u5_ugpm3 != -1 and sensor_PM.concentration_10u_ugpm3 != -1:
    print "PM 2u5, 10u sensor initialized"
else:
    print "PM 2u5, 10u sensor failure"

# load calibration data for each gas sensor
sensor_NO2 = gas_sensor.GasSensor("NO2", cal.NO2)
sensor_SO2 = gas_sensor.GasSensor("SO2", cal.SO2)
sensor_CO = gas_sensor.GasSensor("CO", cal.CO)
sensor_O3 = gas_sensor.GasSensor("O3", cal.O3)
print "gas sensors calibration loaded"

# initialize data frame
aqi_frame = {"time_s": 0, "temp_C": 25, "NO2_ppb": 0, "SO2_ppb": 0, "CO_ppb": 0, "O3_ppb": 0, "PM_2u5_ugpm3": 0, "PM_10u_ugpm3": 0, "aqi": 0, "critical pollutant": "none"}

# setup database
conn = sqlite3.connect("aqi.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS history (time INT PRIMARY KEY NOT NULL, temp INT, NO2_ppb INT, SO2_ppb INT, CO_ppb INT, O3_ppb INT, PM_2u5_ugpm3 INT, PM_10_ugpm3 INT, aqi INT, crit_pol STRING)")
conn.close()


def save_frame_to_db(f):
    frame = (f["time_s"], f["temp_C"], f["NO2_ppb"], f["SO2_ppb"], f["CO_ppb"], f["O3_ppb"], f["PM_2u5_ugpm3"], f["PM_10u_ugpm3"], f["aqi"], f["critical pollutant"])
    conn = sqlite3.connect("aqi.db")
    c = conn.cursor()
    c.execute("INSERT INTO history VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", frame)
    conn.commit()
    conn.close()


# gather full set of data
def read_all_sensors():
    aqi_frame["time_s"] = int(time())

    # read temperature, C
    analog_mux.select_channel(pins.CH_TMP36)
    aqi_frame["temp_C"] = int(TMP36.mV_to_C(mux_ADC.read("mV")))

    # read NO2, ppb
    analog_mux.select_channel(pins.CH_NO2_WE)
    sensor_NO2.WE_mV = mux_ADC.read("mV")
    analog_mux.select_channel(pins.CH_NO2_AE)
    sensor_NO2.AE_mV = mux_ADC.read("mV")
    aqi_frame["NO2_ppb"] = int(sensor_NO2.calc_ppb(aqi_frame["temp_C"]))

    # read SO2, ppb
    analog_mux.select_channel(pins.CH_SO2_WE)
    sensor_SO2.WE_mV= mux_ADC.read("mV")
    analog_mux.select_channel(pins.CH_SO2_AE)
    sensor_SO2.AE_mV = mux_ADC.read("mV")
    aqi_frame["SO2_ppb"] = int(sensor_SO2.calc_ppb(aqi_frame["temp_C"]))

    # read CO, ppb
    analog_mux.select_channel(pins.CH_CO_WE)
    sensor_CO.WE_mV = mux_ADC.read("mV")
    analog_mux.select_channel(pins.CH_CO_AE)
    sensor_CO.AE_mV = mux_ADC.read("mV")
    aqi_frame["CO_ppb"] = int(sensor_CO.calc_ppb(aqi_frame["temp_C"]))

    # read O3, ppb
    analog_mux.select_channel(pins.CH_O3_WE)
    sensor_O3.WE_mV = mux_ADC.read("mV")
    analog_mux.select_channel(pins.CH_O3_AE)
    sensor_O3.AE_mV = mux_ADC.read("mV")
    aqi_frame["O3_ppb"] = int(sensor_O3.calc_ppb(aqi_frame["temp_C"]))

    # read PM 2u5 and 10u, ug per m^3
    aqi_frame["PM_2u5_ugpm3"] = int(round(sensor_PM.read_PM_2u5_ugpm3()))
    aqi_frame["PM_10u_ugpm3"] = int(round(sensor_PM.read_PM_10u_ugpm3()))


start_time_s = time()
last_sample_time_s = start_time_s
last_report_time_s = start_time_s
print "begin reading. {0}s sample period, {1}s report period, {2}s run time".format(sample_period_s, report_period_s, run_time_s)

while time() < start_time_s + run_time_s:

    if time() - last_sample_time_s > sample_period_s:
	last_sample_time_s = time()
	print "{0} reading sensors".format(time()-start_time_s)
        read_all_sensors()
	print """TIME: {0}
TEMP: {1} C
NO2: {2} ppb
SO2: {3} ppb
CO: {4} ppb
O3: {5} ppb
PM2.5: {6} ugpm3
PM10: {7} ugpm3
""".format(aqi_frame["time_s"], \
aqi_frame["temp_C"], \
aqi_frame["NO2_ppb"], \
aqi_frame["SO2_ppb"], \
aqi_frame["O3_ppb"], \
aqi_frame["CO_ppb"], \
aqi_frame["PM_2u5_ugpm3"], \
aqi_frame["PM_10u_ugpm3"])
        save_frame_to_db(aqi_frame)
	print sensor_NO2.WE_mV
	print sensor_NO2.AE_mV
        print sensor_SO2.WE_mV
        print sensor_SO2.AE_mV
        print sensor_O3.WE_mV
        print sensor_O3.AE_mV
        print sensor_CO.WE_mV
        print sensor_CO.AE_mV


    if time() - last_report_time_s > report_period_s:
	print "{0} writing to web server\n".format(time()-start_time_s)
        # report all data to web server since last report. Use HTTP
        last_report_time_s = time()

