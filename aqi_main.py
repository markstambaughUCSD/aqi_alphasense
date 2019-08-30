# Mark Stambaugh
# 2019/08/29
# main module for the UDOO air quality sensor board

import config
import pins
import mux
import adc
import cal
import gas_sensor
import PM
import TMP36
from time import time
import sqlite3
import requests

print "begin Air Quality Sensor"

# set up the analog mux
analog_mux = mux.Mux(16, pins.MUX_EN, pins.MUX_SEL, active_low=True)
analog_mux.select_channel(pins.CH_TMP36)
analog_mux.enable()
print "mux initialized"

# set up the ADC reading the MUX output
mux_ADC = adc.ADC(pins.ADC_MUX)
mux_ADC.oversample = 256
# Calibrate the ADC by reading the reference inputs
LUT_bits = []
for i in pins.CH_REF:
    analog_mux.select_channel(i)
    LUT_bits.append(mux_ADC.read("bits"))
# Check for valid (monotonic increasing) references. If invalid, abort startup. 
for i in range(1, len(LUT_bits)):
    if LUT_bits[i] <= LUT_bits[i-1]:
	print "ADC calibration error. Exiting program"
	exit()
mux_ADC.LUT_bits = LUT_bits
mux_ADC.LUT_mV = pins.REF_mV
print "ADC initialized"



# set up the PM2.5, PM10 sensor
sensor_PM = PM.PM(pins.PM_2U5_PWM, pins.PM_10U_PWM)
sensor_PM.read_PM_2u5_ugpm3()
sensor_PM.read_PM_10u_ugpm3()
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
aqi_frame = {"time_s": 0, "temp_C": 25, "NO2_ppb": 0, "SO2_ppb": 0, "CO_ppb": 0, "O3_ppb": 0, "PM_2u5_ugpm3": 0, "PM_10u_ugpm3": 0}

# set up database
conn = sqlite3.connect("aqi.db")
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS history (time_s INT PRIMARY KEY NOT NULL, temp INT, NO2_ppb INT, SO2_ppb INT, CO_ppb INT, O3_ppb INT, PM_2u5_ugpm3 INT, PM_10_ugpm3 INT)")
conn.close()

# save one set of data to the local database
def save_frame_to_db(f):
	frame = (f["time_s"], f["temp_C"], f["NO2_ppb"], f["SO2_ppb"], f["CO_ppb"], f["O3_ppb"], f["PM_2u5_ugpm3"], f["PM_10u_ugpm3"])
	conn = sqlite3.connect("aqi.db")
	c = conn.cursor()
	c.execute("INSERT INTO history VALUES(?, ?, ?, ?, ?, ?, ?, ?)", frame)
	conn.commit()
	conn.close()


# retrieve data from specified time period and send to the web server over http
def upload_to_server(start_time, stop_time):
	conn = sqlite3.connect("aqi.db")
	c = conn.cursor()
	c.execute("SELECT * FROM history WHERE time_s BETWEEN ? AND ?", (start_time, stop_time))
	rows = c.fetchall()
	for row in rows:
		frame = {"time_s": row[0], "temp_C": row[1], "NO2_ppb": row[2], "SO2_ppb": row[3], "CO_ppb": row[4], "O3_ppb": row[5], "PM_2u5_ugpm3": row[6], "PM_10u_ugpm3": row[7]}
		r = requests.post(url = config.ENDPOINT, data = frame)
		if r.status_code != 200:
			print "HTTP post failed. Frame time: %d" %frame("time_s")


# gather full set of data
def read_all_sensors():
	aqi_frame["time_s"] = int(time())
	
	# read temperature, C
	analog_mux.select_channel(pins.CH_TMP36)
	aqi_frame["temp_C"] = int(TMP36.mV_to_C(mux_ADC.read("mV")))
	
	# read NO2, ppb
	analog_mux.select_channel(pins.CH_GAS["NO2_WE"])
	sensor_NO2.WE_mV = mux_ADC.read("mV")
	analog_mux.select_channel(pins.CH_GAS["NO2_AE"])
	sensor_NO2.AE_mV = mux_ADC.read("mV")
	aqi_frame["NO2_ppb"] = int(sensor_NO2.calc_ppb(aqi_frame["temp_C"]))
	
	# read SO2, ppb
	analog_mux.select_channel(pins.CH_GAS["SO2_WE"])
	sensor_SO2.WE_mV= mux_ADC.read("mV")
	analog_mux.select_channel(pins.CH_GAS["SO2_AE"])
	sensor_SO2.AE_mV = mux_ADC.read("mV")
	aqi_frame["SO2_ppb"] = int(sensor_SO2.calc_ppb(aqi_frame["temp_C"]))
	
	# read CO, ppb
	analog_mux.select_channel(pins.CH_GAS["CO_WE"])
	sensor_CO.WE_mV = mux_ADC.read("mV")
	analog_mux.select_channel(pins.CH_GAS["CO_AE"])
	sensor_CO.AE_mV = mux_ADC.read("mV")
	aqi_frame["CO_ppb"] = int(sensor_CO.calc_ppb(aqi_frame["temp_C"]))
	
	# read O3, ppb
	analog_mux.select_channel(pins.CH_GAS["O3_WE"])
	sensor_O3.WE_mV = mux_ADC.read("mV")
	analog_mux.select_channel(pins.CH_GAS["O3_AE"])
	sensor_O3.AE_mV = mux_ADC.read("mV")
	aqi_frame["O3_ppb"] = int(sensor_O3.calc_ppb(aqi_frame["temp_C"]))
	
	# read PM 2u5 and 10u, ug per m^3
	aqi_frame["PM_2u5_ugpm3"] = int(round(sensor_PM.read_PM_2u5_ugpm3()))
	aqi_frame["PM_10u_ugpm3"] = int(round(sensor_PM.read_PM_10u_ugpm3()))


def gather_data_and_save(sample_period_s, report_period_s, run_time_s):
	start_time_s = time()
	last_sample_time_s = start_time_s
	last_report_time_s = start_time_s
	print "begin reading. {0}s sample period, {1}s report period, {2}s run time".format(sample_period_s, report_period_s, run_time_s)
	print "TIME(s)    TEMP(C) NO2(ppb) SO2(ppb) CO(ppb) O3(ppb) PM2u5(ugpm3) PM10u(ugpm3)"
	
	while time() < start_time_s + config.run_time_s:
		if time() - last_sample_time_s > config.sample_period_s:
			last_sample_time_s = time()
			#print "{0} reading sensors".format(time()-start_time_s)
			read_all_sensors()
			save_frame_to_db(aqi_frame)
			print "%10d %+03d     %04d     %04d     %04d    %04d    %03d          %03d" %( \
			aqi_frame["time_s"], aqi_frame["temp_C"], aqi_frame["NO2_ppb"], aqi_frame["SO2_ppb"], \
			aqi_frame["CO_ppb"], aqi_frame["O3_ppb"], aqi_frame["PM_2u5_ugpm3"], aqi_frame["PM_10u_ugpm3"])
		
		if time() - last_report_time_s > config.report_period_s:
			print "%d writing to web server" %(time() - start_time_s)
			# report all data to web server since last report. Use HTTP.
			upload_to_server(last_report_time_s, time())
			last_report_time_s = time()
		
		# one last upload for any remaining data
		upload_to_server(last_report_time_s, time())


def test_mux_and_ADC():
	print "begin mux/ADC test mode"
	print "ADC calibration LUT:"
	print "mV: ", mux_ADC.LUT_mV
	print "bits: ", mux_ADC.LUT_bits
	print "select negative channel value to exit"
	
	while True:
		channel = int(raw_input("channel?: "))
		if channel < 0:
			print "exiting mux/ADC test mode"
			break
		analog_mux.select_channel(channel)
		print mux_ADC.read("bits")
		print mux_ADC.value_mV


def calibrate_alphasense():
	print "begin Alphasense calibration(mV)"
	for key in pins.CH_GAS:
		analog_mux.select_channel(pins.CH_GAS[key])
		mV = int(round(mux_ADC.read("mV")))
		print key, pins.CH_GAS[key], mV


while True:
	print """\navailable  commands:
	g: gather data and save to web server
	t: test mux/ADC
	c: calibrate Alphasense array
	e: exit program
"""

	command = raw_input("command?:")
	if command == 'g':
		gather_data_and_save(config.sample_period_s, config.report_period_s, config.run_time_s)
	if command == 't':
		test_mux_and_ADC()
	if command == 'c':
		calibrate_alphasense()
	if command == 'e':
		print "exiting program"
		exit()
