import logging
import time
from ppk2_api.ppk2_api import PPK2_API

from lib.internal.model.smu_ppk2 import SMUPPK2Config


def connect(config: SMUPPK2Config):
    config.Device = PPK2_API(config.Port)
    config.Device.get_modifiers()
    config.Device.use_source_meter()


def set_voltage_mv(config: SMUPPK2Config, voltage):
    if voltage > 5000 or voltage < 0:
        raise ValueError
    config.Device.set_source_voltage(voltage)


def turn_on_voltage(config: SMUPPK2Config):
    config.Device.toggle_DUT_power("ON")


def turn_off_voltage(config: SMUPPK2Config):
    config.Device.toggle_DUT_power("OFF")


def get_current_reading(config: SMUPPK2Config):
    current_ua = 0
    config.Device.start_measuring()
    time.sleep(0.5)
    for i in range(0, 5):
        read_data = config.Device.get_data()
        if read_data != b'':
            samples = config.Device.get_samples(read_data)
            current_ua = sum(samples) / len(samples)
    config.Device.stop_measuring()
    return current_ua
