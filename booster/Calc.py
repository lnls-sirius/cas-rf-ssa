#!/usr/bin/python3
# -*- coding: utf-8 -*-
import math

def calc_I(voltage):
    """
    To real world current readings
    :param voltage:
    :return:
    """
    return (4.8321*voltage - 2.4292)

def convert_adc_to_voltage(adc_code):
    """
    Convert from adc values (4095) to voltage readings
    :param adc_code: 
    :return:
    """
    return (adc_code / 4095.0) * 5.0

def calc_Pdbm(voltage):
    """
    To real world Pdbm readings
    :param voltage:
    :return:
    """
    return (10 * math.log10((11.4*(voltage*voltage) + 1.7*voltage + 0.01)))

def flip_low_high(low,high):
    """
    Flip if needed
    return low, high
    """
    if low > high:
        aux = low
        low = high
        high = aux
    
    return low, high