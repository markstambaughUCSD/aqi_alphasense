# Mark Stambaugh
# 2019/08/21
# lookup tables of Air Quality Index (AQI) values for different pollutants

LUT_AQI = [0, 50, 51, 100, 101, 150, 151, 200, 201, 300, 301, 400, 401, 500]

LUT_concentrations = {"O3_8hr_ppb" : [0, 54, 55, 70, 71, 85, 86, 105, 106, 200, -1, -1],
                      "O3_1hr_ppb" : [-1, -1, -1, -1, 125, 164, 165, 204, 205, 404, 405, 504, 505, 604],
                      "PM_2u5_24hr_ugpm3" : [0.0, 12.0, 12.1, 35.4, 35.5, 55.4, 55.5, 150.4, 150.5, 250.4, 250.5, 350.4, 350.5, 500.4],
                      "PM_10u_24hr_ugpm3" : [0, 54, 55, 154, 155, 254, 255, 354, 355, 424, 425, 504, 505, 604],
                      "CO_8hr_ppm" : [0.0, 4.4, 4.5, 9.4, 9.5, 12.4, 12.5, 15.4, 15.5, 30.4, 30.5, 40.4, 40.5, 50.4],
                      "SO2_1hr_ppb" : [0, 35, 36, 75, 76, 185, 186, 304, 305, 604, 605, 804, 805, 1004],
                      "NO2_1hr_ppb" : [0, 53, 54, 100, 101, 360, 361, 649, 650, 1249, 1250, 1649, 1650, 2049]
                      }

def calculate_aqi(pollutant, concentration_in):
    if pollutant in LUT_concentrations:
        LUT_con = LUT_concentrations[pollutant]
        aqi_out = 0
        if concentration_in < 0:
            print "invalid concentration"
            aqi_out = -1
        elif concentration_in < LUT_con[-1]:
            for k in range(0, len(LUT_con) - 1):
                if concentration_in < LUT_con[k+1]:
                    aqi_out = LUT_AQI[k] + (concentration_in - LUT_con[k]) * (LUT_AQI[k+1] - LUT_AQI[k]) / (LUT_con[k+1] - LUT_con[k])
                    break
        else:
            aqi_out = LUT_AQI[-1] + (concentration_in - LUT_con[-1]) * (LUT_AQI[-1] - LUT_AQI[-2]) / (LUT_con[-1] - LUT_con[-2])

        return aqi_out
    else:
        print "Invalid pollutant called to aqi calculation"
        return -1
