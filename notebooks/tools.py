# Copyright 2022 Cognite AS
from math import log


def thermal_resistance(x):
    """Function to calculate Thermal Resistance"""
    # Some constants like Correction factor, Area and Cp values
    F = 0.8
    A = 1.0
    Cp_hot = 2.4
    # Calculate the cross temperature differences
    x["dT1"] = abs(x["T_hot_IN"] - x["T_cold_OUT"])
    x["dT2"] = abs(x["T_hot_OUT"] - x["T_cold_IN"])
    # Calculate the numerator and denominator for the thermal resistance calculation
    temp1 = A * F * (x["dT1"] - x["dT2"]) / log(x["dT1"] / x["dT2"])
    temp2 = x["Flow_hot"] * Cp_hot * (x["T_hot_IN"] - x["T_hot_OUT"])
    TR = temp1 / temp2
    return TR
