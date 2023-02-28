import logging

from lib.internal.model.trixie import TrixieConfig
from lib.internal.service import smu_ppk2_service as ppk
from lib.external.mCommon3.service import serialcomm_service as ser


def send(config: TrixieConfig, message):
    ser.send_message(config.InputComm, message.encode("utf-8"))


def set_voltage(config, line):
    try:
        elements = line.decode("utf-8").split("|")
        channel = int(elements[1])
        v = float(elements[2])
        unit = elements[3].strip().lower()
    except:
        send(config, f"Error. Invalid set command. Proper command use: \n"
                     f"\tset|<channel num>|<voltage num>|<unit>\nTry again.\n")
        return
    if unit not in ["mv", "v"]:
        send(config, f"Error. Invalid Unit. Use mv or v. Try again.\n")
        return
    if channel not in [1, 2]:
        send(config, f"Error. Invalid Channel. Choose 1 or 2. Try again.\n")
        return

    if unit == "v":
        v = v * 1000

    if channel == 1:
        try:
            ppk.set_voltage_mv(config.Channel1, v)
        except:
            send(config, f"Error. Invalid voltage value. Must be between 0 and 5V. Try again. \n")
            return
        else:
            config.Channel1.Voltage = v
            send(config, f"Success. Set Channel 1's voltage to: {v}mV.\n")
    if channel == 2:
        try:
            ppk.set_voltage_mv(config.Channel2, v)
        except:
            send(config, f"Error. Invalid voltage value. Must be between 0 and 5V. Try again. \n")
            return
        else:
            config.Channel2.Voltage = v
            send(config, f"Success. Set Channel 2's voltage to: {v}mV.\n")


def set_state(config, line):
    try:
        elements = line.decode("utf-8").split("|")
        channel = int(elements[1])
        state = elements[2].strip().lower()
    except:
        send(config, f"Error. Invalid set command. Proper command use: \n"
                     f"\tstate|<channel num>|<state>\nTry again.\n")
        return
    if state not in ["on", "off"]:
        send(config, f"Error. Invalid state. Use ON or OFF. Try again.\n")
        return
    if channel not in [1, 2]:
        send(config, f"Error. Invalid Channel. Choose 1 or 2. Try again.\n")
        return

    if channel == 1:
        if not config.Channel1.Voltage:
            send(config, f"Error. No voltage has been set for Channel 1. Use the set command to do this first.\n")
            return

        if state == "on":
            ppk.turn_on_voltage(config.Channel1)
        else:
            ppk.turn_off_voltage(config.Channel1)
        send(config, f"Success. Turned {state} Channel 1's voltage to: {config.Channel1.Voltage}mV.\n")
    if channel == 2:
        if not config.Channel2.Voltage:
            send(config, f"Error. No voltage has been set for Channel 2. Use the set command to do this first.\n")
            return

        if state == "on":
            ppk.turn_on_voltage(config.Channel2)
        else:
            ppk.turn_off_voltage(config.Channel2)
        send(config, f"Success. Turned {state} Channel 2's voltage to: {config.Channel2.Voltage}mV.\n")


def get_current(config, line):
    try:
        elements = line.decode("utf-8").split("|")
        channel = int(elements[1])
    except:
        send(config, f"Error. Invalid set command. Proper command use: \n"
                     f"\tget|<channel num>\nTry again.\n")
        return
    if channel not in [1, 2]:
        send(config, f"Error. Invalid Channel. Choose 1 or 2. Try again.\n")
        return

    if channel == 1:
        try:
            current_ua = ppk.get_current_reading(config.Channel1)
        except ZeroDivisionError:
            send(config, f"Error. Voltage not set on Channel 1.\n")
        else:
            send(config, f"current|1|{current_ua}|ua\n")
    if channel == 2:
        try:
            current_ua = ppk.get_current_reading(config.Channel2)
        except:
            send(config, f"Error. Voltage not set on Channel 2.\n")
        else:
            send(config, f"current|1|{current_ua}|ua\n")


def uart_listen(config: TrixieConfig):
    line = ser.read_message(config.InputComm)
    if line:
        if b'help' in line:
            send(config, "Command list:\n"
                         "\tSet Voltage: \tset|<channel num>|<voltage num>|<unit>\n"
                         "\tSet State: \tstate|<channel num>|<state>\n"
                         "\tGet Current: \tget|<channel num>\n")
        elif b'set' in line:
            set_voltage(config, line)
        elif b'state' in line:
            set_state(config, line)
        elif b'get' in line:
            get_current(config, line)
        else:
            send(config, f"Invalid command:\n\t{line}\nEnter help for list of valid commands.\n")


def run_application(config: TrixieConfig):
    print("Welcome to Trixie.")
    ppk.connect(config.Channel1)
    ppk.connect(config.Channel2)

    ser.open_serial(config.InputComm)
    send(config, "Welcome to Trixie.\nEnter a command to begin. Enter help for command list.\n")
    while 1:
        uart_listen(config)
