# Mark Stambaugh
# 2019/08/21
# mux class for storing / calculating the temperature using TMP36

REF_C = 25
REF_mV = 750
SCALE_mV_PER_C = 10


def mV_to_C(mV_in):
    C_out = REF_C + (mV_in - REF_mV) / SCALE_mV_PER_C
    return C_out


# class TMP36:
#     """TMP36 class to calculate the temperature"""
#
#     def __init__(self):
#         self.mV = 750
#         self.C = 25
#