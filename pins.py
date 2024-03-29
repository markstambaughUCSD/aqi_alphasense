# Mark Stambaugh
# 2019/07/26
# defines pins and connections from UDOO board to other sensors

# PM output
PM_2U5_PWM = 33
PM_10U_PWM = 32

# mux control pins
MUX_EN = 24
MUX_SEL = [25, 26, 27, 28]

# ADC channel used at the output of the mux
ADC_MUX = "A5"

# mux channel definitions
CH_GAS = {"NO2_WE": 11, 
		  "NO2_AE": 15, 
		  "O3_WE": 10, 
		  "O3_AE": 14, 
		  "CO_WE": 8, 
		  "CO_AE": 13, 
		  "SO2_WE": 9, 
		  "SO2_AE": 12
		  }

CH_TMP36 = 7

# reference voltage definitions for ADC calibration
REF_mV = [0, 169, 338, 506, 679, 846, 2503]
CH_REF = [6, 2, 1, 0, 3, 4, 5]
