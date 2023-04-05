from lib.external.pythontools.ppk2_api_modified import PPK2_API
import time

sm1 = PPK2_API("/dev/ttyACM1")  # serial port will be different for you
sm1.get_modifiers()
sm1.use_source_meter()  # set source meter mode
sm1.set_source_voltage(4200)  # set source voltage in mV
sm1.toggle_DUT_power("ON")
# sm1.start_measuring()  # start measuring

# sm2 = PPK2_API("/dev/ttyACM1")  # serial port will be different for you
# sm2.get_modifiers()
# sm2.use_source_meter()  # set source meter mode
# sm2.set_source_voltage(3600)  # set source voltage in mV
# sm2.toggle_DUT_power("ON")
# sm2.start_measuring()  # start measuring

print("You have 10 seconds to check voltage")
for i in range(1, 11):
    print(f"{i} second")
    time.sleep(1)

# read measured values in a for loop like this:
# for i in range(0, 100):
#     read_data = sm1.get_data()
#     if read_data != b'':
#         samples = sm1.get_samples(read_data)
#         print(f"SM111111111111111: {sum(samples) / len(samples)}uA")

    # read_data = sm2.get_data()
    # if read_data != b'':
    #     samples = sm2.get_samples(read_data)
    #     print(f"SM222222222222222: {sum(samples) / len(samples)}uA")

#     time.sleep(0.001)  # lower time between sampling -> less samples read in one sampling period
#
# sm1.stop_measuring()
# sm2.stop_measuring()
