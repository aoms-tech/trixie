import logging
import time
from serial.tools import list_ports

from lib.internal.model.smu_ppk2 import SMUPPK2Config
from lib.external.pythontools.ppk2_api_modified import PPK2_API


def find_port(config: SMUPPK2Config):
    ports = list_ports.comports()
    for port, desc, hwid in sorted(ports):
        if config.ID in hwid:
            config.Port = port


def connect(config: SMUPPK2Config):
    config.Device = PPK2_API(config.Port)
    config.Device.get_modifiers()
    config.Device.use_source_meter()


def set_voltage_mv(config: SMUPPK2Config, voltage):
    if voltage > 5000 or voltage < 0:
        raise ValueError
    voltage = int(voltage)
    try:
        config.Device.set_source_voltage(voltage)
    except:
        config.Device.disconnect_device()
        find_port(config)
        connect(config)
        config.Device.set_source_voltage(voltage)


def turn_on_voltage(config: SMUPPK2Config):
    try:
        config.Device.toggle_DUT_power("ON")
    except:
        config.Device.disconnect_device()
        find_port(config)
        connect(config)
        set_voltage_mv(config, config.Voltage)
        config.Device.toggle_DUT_power("ON")


def turn_off_voltage(config: SMUPPK2Config):
    try:
        config.Device.toggle_DUT_power("OFF")
    except:
        config.Device.disconnect_device()
        find_port(config)
        connect(config)
        set_voltage_mv(config, config.Voltage)
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
