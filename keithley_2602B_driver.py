import pyvisa
import time
import re


class Keithley2602B():
    """
    Keithley 2602B uses TSP (Test Script Processor) commands and a limited number of SCPI commands.
    Keithley 2410 uses SCPI only.
    SCPI is common among various testing equipment.
    TSP is Tektronix's IP so limited to their newer equipment.  TSP allows local processing on unit w/o accessing bus to
        an external PC.  It is Lua-based so it's compatible w/ related programs.
    In manual ("2600BS-901-01E_Jan2019_Ref.pdf") Pg. 11 has compact list of command names and pg. 375 details commands.
    """
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        print(self.rm.list_resources())
        self.device_handle = self.rm.open_resource("GPIB0::30::INSTR") # for keithely 2602B

    def __del__(self):
        self.rm.close()

    def get_id(self):
        return self.device_handle.query("*IDN?")

    def keithley_initialize_2602B(self):
        self.device_handle.write('errorqueue.clear()')

        # safety limits
        self.device_handle.write("smua.source.limitv = 10")
        self.device_handle.write("smub.source.limitv = 10")

        self.device_handle.write("smua.source.limiti = 1")
        self.device_handle.write("smub.source.limiti = 1")

        # test settings
        self.device_handle.write("smua.source.levelv = -3")
        self.device_handle.write("smub.source.levelv = 0")

        self.device_handle.write("smua.source.leveli = 0")
        self.device_handle.write("smub.source.leveli = 0")

        # front display
        self.device_handle.write("display.smua.measure.func = display.MEASURE_DCAMPS")
        self.device_handle.write("display.smub.measure.func = display.MEASURE_DCAMPS")


    def keithley_initialize_2410(self):
        # safety limits
        self.device_handle.write(":CURRent:PROTection 500e-6")

        # test settings
        self.device_handle.write(":SOUR:VOLT -2")

        # front display
        #self.device_handle.write(":DISP:CNDisplay")





    def set_smua_current_limit(self, current):
        return self.device_handle.write("smua.source.limiti = ", current)

    def set_smub_current_limit(self, current):
        return self.device_handle.write("smub.source.limitv = ", current)

    def set_smua_voltage_limit(self, voltage):
        return self.device_handle.write("smua.source.limitv = ", voltage)

    def set_smub_voltage_limit(self, voltage):
        return self.device_handle.write("smub.source.limiti = ", voltage)

    def set_smua_power_limit(self, power):
        return self.device_handle.write("smua.source.limitp = ", power)

    def set_smub_power_limit(self, power):
        return self.device_handle.write("smub.source.limitp = ", power)


    def set_smu_limit(self, ab, vip, value):
        # replace string with the faster & shorter f'smu{ab}.measure.{vip}() = {value}'
        return self.device_handle.write("smu" + str(ab) + ".measure." + str(vip) + "() = " + str(value))



    def SCPI_ouput_off(self):
        return self.device_handle.write(":OUTP:STAT OFF")

    def SCPI_ouput_on(self):
        return self.device_handle.write(":OUTP:STAT ON")

    def SCPI_measure_i(self):
        return self.device_handle.query(":MEAS:CURR:DC?")

    def SCPI_measure_i_clean(self):
        '''
        pg. 304 Performs 'one-shot' measurement by executing CONFigure <function> and READ?

        '''
        return float(self.device_handle.query(":MEAS:CURR:DC?").split(",")[1:2][0])

    def SCPI_get_source_voltage(self):
        return self.device_handle.query(":SOURce:VOLTage:AMPLitude?").rstrip()

    def SCPI_configure(self):
        return self.device_handle.query(":CONF?")

    def smua_measure_i(self):
        return self.device_handle.write("smua.measure.i() = ")

    def smub_measure_i(self):
        return self.device_handle.write("smub.measure.i()")

    def smua_measure_v(self):
        return self.device_handle.write("smua.measure.v()")

    def smub_measure_v(self):
        return self.device_handle.write("smub.measure.v()")

    def smua_measure_r(self):
        return self.device_handle.write("smua.measure.r()")

    def smub_measure_r(self):
        return self.device_handle.write("smub.measure.r()")

    def smua_measure_p(self):
        return self.device_handle.write("smua.measure.p()")

    def smub_measure_p(self):
        return self.device_handle.write("smub.measure.p()")

    def smu_measure(self, ab, virp):
        # replace string with the faster & shorter f'smu{ab}.measure.{vip}()'
        return self.device_handle.write("smu" + str(ab) + ".measure." + str(virp) + "()")




    def reset(self):
        return self.device_handle.write("reset()")

    def smua_output_on(self):
        return self.device_handle.write("smua.source.output = smua.OUTPUT_ON")

    def smub_output_on(self):
        return self.device_handle.write("smub.source.output = smub.OUTPUT_ON")

    def smua_output_off(self):
        return self.device_handle.write("smua.source.output = smua.OUTPUT_OFF")

    def smub_output_off(self):
        return self.device_handle.write("smub.source.output = smub.OUTPUT_OFF")

    def smua_display_source_measure_compliance(self):
        return self.device_handle.write('display.screen = display.SMUA')

    def smub_display_source_measure_compliance(self):
        return self.device_handle.write('display.screen = display.SMUB')

    def smuab_display_source_measure(self):
        return self.device_handle.write('display.screen = display.SMUA_SMUB')

    def smua_display_current(self):
        return self.device_handle.write("display.smua.measure.func = display.MEASURE_DCAMPS")

    def smub_display_current(self):
        return self.device_handle.write("display.smub.measure.func = display.MEASURE_DCAMPS")

    def smua_display_voltage(self):
        return self.device_handle.write("display.smua.measure.func = display.MEASURE_DCVOLTS")

    def smub_display_voltage(self):
        return self.device_handle.write("display.smub.measure.func = display.MEASURE_DCVOLTS")

    def smua_display_ohms(self):
        return self.device_handle.write("display.smua.measure.func = display.MEASURE_OHMS")

    def smub_display_ohms(self):
        return self.device_handle.write("display.smub.measure.func = display.MEASURE_OHMS")

    def smua_display_watts(self):
        return self.device_handle.write("display.smua.measure.func = display.MEASURE_WATTS")

    def smub_display_watts(self):
        return self.device_handle.write("display.smub.measure.func = display.MEASURE_WATTS")

    def smua_set_measure_count(self, value):
        return self.device_handle.write(f'smua.measure.count = {value}')

    def smub_set_measure_count(self, value):
        return self.device_handle.write(f'smub.measure.count = {value}')

    def smua_set_to_measure_current(self):
        return self.device_handle.write('smua.measure.func = smua.FUNC_DC_CURRENT')


if __name__ == "__main__":
    k = Keithley2602B()
    print(k.get_id())
    k.smua_output_on()
    print(k.smua_display_current())




    # while True:
    #     avg_list = [k.SCPI_measure_i_clean() for i in range(0, 9)]
    #     avg = sum(avg_list) / len(avg_list)
    #     print(avg)
    #     time.sleep(0.1)

    #print(k.keithley_initialize_2410())
    #print(k.SCPI_measure_i_clean())
    #print(k.SCPI_get_source_voltage())
    #print(float(k.SCPI_measure_i().split(",")[1:2][0]))
    #print(k.SCPI_measure_i_clean())
    #print(k.smua_measure_v())
    #print(k.set_smu_limit("a", "v", 1))

