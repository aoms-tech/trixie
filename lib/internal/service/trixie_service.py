import logging
import RPi.GPIO as GPIO
import time

import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

from lib.internal.model.trixie import TrixieConfig
from lib.internal.service import smu_ppk2_service as ppk
from lib.external.mCommon3.service import serialcomm_service as ser


def init_fb(config: TrixieConfig):
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    cs = digitalio.DigitalInOut(board.D22)
    config.Feedback = MCP.MCP3008(spi, cs)


def update_outputs(config: TrixieConfig):
    if config.Channel1.State:
        ch1_fb_input = AnalogIn(config.Feedback, MCP.P0)
        ch1_fb = round(ch1_fb_input.voltage*2, 2)
        print(f"Channel 1 FB Voltage: {ch1_fb}V")
        ppk.update_output_from_fb(config.Channel1, ch1_fb)

    if config.Channel2.State:
        ch2_fb_input = AnalogIn(config.Feedback, MCP.P1)
        ch2_fb = round(ch2_fb_input.voltage*2, 2)
        print(f"Channel 2 FB Voltage: {ch2_fb}V")
        ppk.update_output_from_fb(config.Channel2, ch2_fb)


def send(config: TrixieConfig, message):
    print(message)
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
            config.Channel1.IntendedVoltage = v
            config.Channel1.OutputVoltage = v
            send(config, f"Success. Set Channel 1's voltage to: {v}mV.\n")
    if channel == 2:
        try:
            ppk.set_voltage_mv(config.Channel2, v)
        except:
            send(config, f"Error. Invalid voltage value. Must be between 0 and 5V. Try again. \n")
            return
        else:
            config.Channel2.IntendedVoltage = v
            config.Channel2.OutputVoltage = v
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
        if state == "on":
            if config.Channel1.IntendedVoltage is None:
                send(config, f"Error. No voltage has been set for Channel 1. Use the set command to do this first.\n")
                return
            ppk.turn_on_voltage(config.Channel1)
            config.Channel1.State = 1
        else:
            ppk.turn_off_voltage(config.Channel1)
            config.Channel1.State = 0
        send(config, f"Success. Turned {state} Channel 1's voltage to: {config.Channel1.IntendedVoltage}mV.\n")
    if channel == 2:
        if state == "on":
            if config.Channel2.IntendedVoltage is None:
                send(config, f"Error. No voltage has been set for Channel 2. Use the set command to do this first.\n")
                return
            ppk.turn_on_voltage(config.Channel2)
            config.Channel2.State = 1
        else:
            ppk.turn_off_voltage(config.Channel2)
            config.Channel2.State = 0
        send(config, f"Success. Turned {state} Channel 2's voltage to: {config.Channel2.IntendedVoltage}mV.\n")


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
            current_ua = ppk.apply_current_fb_offset(config.Channel1, current_ua)
            send(config, f"current|1|{current_ua}|ua\n")
    if channel == 2:
        try:
            current_ua = ppk.get_current_reading(config.Channel2)
        except:
            send(config, f"Error. Voltage not set on Channel 2.\n")
        else:
            current_ua = ppk.apply_current_fb_offset(config.Channel2, current_ua)
            send(config, f"current|2|{current_ua}|ua\n")


def power_channel1():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.OUT)
    GPIO.output(23, GPIO.HIGH)


def power_channel2():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(24, GPIO.OUT)
    GPIO.output(24, GPIO.HIGH)


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
        elif b'exit' in line:
            exit(0)
        elif b'hello' in line:
            send(config, f"Hello!\n")
        else:
            send(config, f"Invalid command:\n\t{line}\nEnter help for list of valid commands.\n")


def run_application(config: TrixieConfig):
    print("Welcome to Trixie.")
    power_channel1()
    power_channel2()

    time.sleep(4)

    ppk.find_port(config.Channel1)
    ppk.find_port(config.Channel2)

    ppk.connect(config.Channel1)
    ppk.connect(config.Channel2)

    ser.open_serial(config.InputComm)

    init_fb(config)

    config.Channel1.State = 0
    config.Channel2.State = 0

    send(config, "Welcome to Trixie.\nEnter a command to begin. Enter help for command list.\n")
    while 1:
        update_outputs(config)
        uart_listen(config)
