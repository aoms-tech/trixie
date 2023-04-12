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
        set_voltage_mv(config, config.OutputVoltage)
        config.Device.toggle_DUT_power("ON")


def turn_off_voltage(config: SMUPPK2Config):
    try:
        config.Device.toggle_DUT_power("OFF")
    except:
        config.Device.disconnect_device()
        find_port(config)
        connect(config)
        set_voltage_mv(config, config.OutputVoltage)
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


def update_output_from_fb(config: SMUPPK2Config, fb_voltage):
    fb_voltage = fb_voltage * 1000
    if (fb_voltage < (config.IntendedVoltage - 50)) or (fb_voltage > (config.IntendedVoltage + 50)):
        if fb_voltage:
            print(f"Updating output voltage to better match intended voltage ...")
            print(f"ORG Output Voltage: {config.OutputVoltage}")
            new_voltage = (config.OutputVoltage * config.IntendedVoltage) / fb_voltage
            print(f"NEW Output Voltage: {new_voltage}")
            try:
                set_voltage_mv(config, new_voltage)
            except:
                print("New voltage failed to set.")
            else:
                config.OutputVoltage = new_voltage


def apply_current_fb_offset(config: SMUPPK2Config, uamps):
    print(f"ORG Current: {uamps}")
    new_uamps = ((440*uamps) - (config.IntendedVoltage*1000)) / 440
    print(f"NEW Current: {new_uamps}")
    return new_uamps
