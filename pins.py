# Mark Stambaugh
# 2019/07/26
# defines pins and connections from UDOO board to other sensors

# PM2.5 PWM output
PM_2U5_PWM = 29
PM_10U_PWM = 30

# mux control pins
MUX_EN = 24
MUX_SEL = (25, 26, 27, 28)

# ADC channel used at the output of the mux
ADC_MUX = "A0"

# mux channel definitions
CH_NO2_WE = 0
CH_NO2_AE = 1
CH_O3_WE = 2
CH_O3_AE = 3
CH_CO_WE = 4
CH_CO_AE = 5
CH_SO2_WE = 6
CH_SO2_AE = 7
CH_TMP36 = 8

CH_EMPTY = 9

# reference voltage definitions for ADC calibration
REF_mV = [0, 500, 1000, 1500, 2000, 2500]
CH_REF = [10, 11, 12, 13, 14, 15]
