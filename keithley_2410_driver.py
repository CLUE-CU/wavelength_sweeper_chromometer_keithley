import pyvisa
import time

#TODO:
# Finish/test voltage_sweep

class Keithley2410:
    '''
    Keithley 2602B uses TSP (Test Script Processor) commands and a limited number of SCPI commands.
    Keithley 2410 uses SCPI only.
    SCPI is common among various testing equipment.
    TSP is Tektronix's IP so limited to their newer equipment.  TSP allows local processing on unit w/o accessing bus to
        an external PC.  It is Lua-based so it's compatible w/ related programs.
    In manual ("2400S-900-01_K-Sept2011_User.pdf") pg. 307 has commands.

    2410 — With the 1kV source range selected, the highest current measurement
    range is 20mA. With the 1A or 100mA source range selected, the highest voltage measurement range is 20V.

    See basic source-measure commands pg. 73
    '''

    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.device_handle = self.rm.open_resource('GPIB0::24::INSTR')  # for keithely 2410

    def __del__(self):
        self.rm.close()

    # def keithley_initialize_2602B(self):
    #     # safety limits
    #     self.device_handle.write("smua.source.limitv = 10")
    #     self.device_handle.write("smub.source.limitv = 10")
    #
    #     self.device_handle.write("smua.source.limiti = 1")
    #     self.device_handle.write("smub.source.limiti = 1")
    #
    #     # test settings
    #     self.device_handle.write("smua.source.levelv = -3")
    #     self.device_handle.write("smub.source.levelv = 0")
    #
    #     self.device_handle.write("smua.source.leveli = 0")
    #     self.device_handle.write("smub.source.leveli = 0")
    #
    #     # front display
    #     self.device_handle.write("display.smua.measure.func = display.MEASURE_DCAMPS")
    #     self.device_handle.write("display.smub.measure.func = display.MEASURE_DCAMPS")


    # def voltage_sweep(self, start, stop, step):
    #     '''
    #     Two methods: use the :STARt and :STOP commands or :CENTer and :SPAN commands.
    #     To run a sweep, selected source must be in the sweep sourcing mode and trigger count should match the number of
    #     measurment points in sweep (pg. 388).
    #     To avoid a setting conflicts error, make sure the step size is greater than the start value and less than the
    #     stop value.
    #
    #     This function takes care of all requirements for you.
    #
    #     Full SCPI commands:
    #     :SOURce:FUNCtion:MODE VOLTage
    #
    #     :return:
    #     '''
    #     self.device_handle.write(':SOUR:FUNC VOLT')
    #     self.device_handle.write(':SOUR:CURR:MODE SWE')
    #
    #     self.device_handle.write(f'SOUR:VOLT:STAR {start}')
    #     self.device_handle.write(f'SOUR:VOLT:STOP {stop}')
    #     self.device_handle.write(f'SOUR:VOLT:STEP {step}')
    #     #self.device_handle.write(f':TRIG:SEQ:COUN {value}')
    #
    #     self.device_handle.write('SOUR:SWE:RANG: FIX') # options: BEST or FIXed
    #     self.device_handle.write('SOUR:SWE:DIR UP')

    def get_voltage_sweep_start(self, option=None):
        '''

        :param option: <n>, def, default, max, maximum, min, minimum
        :return:
        '''
        cmd = ':SOUR:VOLT:STAR?'
        return self.processor_query_def_min_max(cmd, option)

    def get_voltage_sweep_stop(self, option=None):
        '''

        :param option: <n>, def, default, max, maximum, min, minimum
        :return:
        '''
        cmd = ':SOUR:VOLT:STOP?'
        return self.processor_query_def_min_max(cmd, option)

    def get_voltage_sweep_step(self, option=None):
        '''

        :param option: <n>, def, default, max, maximum, min, minimum
        :return:
        '''
        cmd = 'SOUR:VOLT:STEP?'
        return self.processor_query_def_min_max(cmd, option)


    def set_current_sense(self):
        '''


        :return:
        '''
        self.device_handle.write(':SENS:FUNC CURR')

    def set_voltage_sense(self):
        '''


        :return:
        '''
        self.device_handle.write(':SENS:FUNC VOLT')


    def get_id(self):
        return self.device_handle.query('*IDN?')

    def list_resources(self):
        return self.rm.list_resources()

    def keithley_initialize_2410(self):
        # safety limits
        self.set_voltage_compliance(25)
        self.set_current_compliance(2)
        # self.device_handle.write(":CURRent:PROTection 500e-6")

        # test settings
        # self.device_handle.write(":SOUR:VOLT -2")

    def get_display_state(self):
        '''
        0 for OFF.
        1 for ON.

        Full SCPI command:
        :DISPlay:ENABle?

        :return:
        '''
        return self.device_handle.query(':DISP:ENAB?')

    def set_display_state(self, cmd):
        '''
        0 for OFF.  1 for ON.
        This command is used to enable and disable the front panel display circuitry. When disabled, the instrument
        operates at a higher speed.  While disabled, the display is frozen with the following message:

        FRONT PANEL DISABLED
        Press LOCAL to resume.

        As reported by the message, all front panel controls (except LOCAL and OUTPUT OFF) are disabled. Normal display
        operation can be resumed by using the :ENABle command to enable the display or by putting the SourceMeter into
        local.

        Full SCPI command:
        :DISPlay:ENABle?

        :return:
        '''
        return self.device_handle.write(f':DISP:ENAB {cmd}')

    def get_source_mode(self):
        '''
        This command is used to select the source mode. With VOLTage selected, the V-Source will be used, and with
        CURRent selected, the I-Source will be used (pg. 378).

        Full SCPI command:
        :SOURce:FUNCtion:MODE?
        '''
        return self.device_handle.query(':SOUR:FUNC?')

    def set_as_current_source(self):
        '''
        This command is used to select the source mode. With VOLTage selected, the V-Source will be used, and with
        CURRent selected, the I-Source will be used (pg. 378).

        Full SCPI command:
        :SOURce:FUNCtion:MODE?

        :return:
        '''
        self.device_handle.write(':SOUR:FUNC CURR')

    def set_as_voltage_source(self):
        '''
        This command is used to select the source mode. With VOLTage selected, the V-Source will be used, and with
        CURRent selected, the I-Source will be used (pg. 378).

        Full SCPI command:
        :SOURce:FUNCtion:MODE?

        :return:
        '''
        self.device_handle.write(':SOUR:FUNC VOLT')

    def get_current_source_mode(self):
        '''
        This command is used to select the DC sourcing mode for the specified source.

        FIXed — In this DC sourcing mode, the specified source will output a fixed level. Use the :RANGe and :AMPLitude
        commands to specify the fixed source level. (See “Select range,” page 18-74, and “Set amplitude for fixed source
        ,” page 18-77.)

        LIST — In this mode, the source will output levels that are specified in a list. See “Configure list” for
        commands to define and control the execution of the list.

        SWEep — In this mode, the source will perform a voltage, current or memory sweep. See “Configure voltage and
        current sweeps,”page 18-83, and “Configure memory sweep,” page 18-93, for commands to define the sweep.

        The sourcing mode will default to FIXed whenever the SourceMeter goes to the local state  (pg. 378).

        Full SCPI command:
        :SOURce:CURRent:MODE?

        :param value:
        :return:
        '''
        return self.device_handle.query(':SOUR:CURR:MODE?')

    def get_voltage_source_mode(self):
        '''
        This command is used to select the DC sourcing mode for the specified source.

        FIXed — In this DC sourcing mode, the specified source will output a fixed level. Use the :RANGe and :AMPLitude
        commands to specify the fixed source level. (See “Select range,” page 18-74, and “Set amplitude for fixed source
        ,” page 18-77.)

        LIST — In this mode, the source will output levels that are specified in a list. See “Configure list” for
        commands to define and control the execution of the list.

        SWEep — In this mode, the source will perform a voltage, current or memory sweep. See “Configure voltage and
        current sweeps,”page 18-83, and “Configure memory sweep,” page 18-93, for commands to define the sweep.

        The sourcing mode will default to FIXed whenever the SourceMeter goes to the local state  (pg. 378).

        Full SCPI command:
        :SOURce:CURRent:MODE?

        :param value:
        :return:
        '''
        return self.device_handle.query(':SOUR:VOLT:MODE?')

    def get_trigger_count(self, option=None):
        '''
        This command is used to specify how many times an operation is performed in the specified layer of the trigger
        model.  For example, assume the arm count is set to 2 and the trigger counter is set to 10, the SourceMeter is
        configured to perform 10 source-measure operations twice for a total of 20 source-measure operations.  The
        product of the arm count and trigger count cannot exceed 2500.  If, for example, the arm count is 2, then the
        maximum trigger count is 1250.

        Full SCPI command:
        :TRIGger:SEQuence:COUNt <n>

        :param option:
        :return:
        '''
        cmd = ':TRIG:SEQ:COUN?'
        return self.processor_query_def_min_max(cmd, option)

    def set_trigger_count(self, value):
        '''
        This command is used to specify how many times an operation is performed in the specified layer of the trigger
        model.  For example, assume the arm count is set to 2 and the trigger counter is set to 10, the SourceMeter is
        configured to perform 10 source-measure operations twice for a total of 20 source-measure operations.  The
        product of the arm count and trigger count cannot exceed 2500.  If, for example, the arm count is 2, then the
        maximum trigger count is 1250.

        Full SCPI command:
        :SOURce:VOLTage:PROTection:LEVel <n>

        :param value:
        :return:
        '''
        self.device_handle.write(f':TRIG:SEQ:COUN {value}')

    def get_voltage_limit(self, option=None):
        '''
        This command is used to set the Over Voltage Protection (OVP) limit for the V-Source. The V-Source output will
        not exceed the selected limit.  If you specify a value that is less than the lowest limit, the lowest limit will
        be selected. If you specify a value that is between limits, the lower limit will be selected. For example, if
        you specify a value of 110 for the Model 2400, the 100V limit will be selected.

        To set/get voltage compliance, use the get/set_current_compliance function.
        SMU limit intervals of +- 20, 40, 100, 200, 300, 400, 500, 501-1100 (pg. 385).

        Full SCPI command:
        :SOURce:VOLTage:PROTection:LEVel?

        :param option:
        :return:
        '''
        cmd = ':SOUR:VOLT:PROT?'
        return self.processor_query_def_min_max(cmd, option)

    def set_voltage_limit(self, value):
        '''
        This command is used to set the Over Voltage Protection (OVP) limit for the V-Source. The V-Source output will
        not exceed the selected limit.  If you specify a value that is less than the lowest limit, the lowest limit will
        be selected. If you specify a value that is between limits, the lower limit will be selected. For example, if
        you specify a value of 110 for the Model 2400, the 100V limit will be selected.

        To set/get voltage compliance, use the get/set_current_compliance function.
        SMU limit intervals of +- 20, 40, 100, 200, 300, 400, 500, 501-1100 (pg. 385).

        Full SCPI command:
        :SOURce:VOLTage:PROTection:LEVel <n>

        :param value:
        :return:
        '''
        self.device_handle.write(f':SOUR:VOLT:PROT {value}')

    def get_voltage_source(self, option=None):
        '''
        Full SCPI command:
        :SOURce:VOLTage:AMPLitude?

        :return:
        '''
        cmd = ':SOUR:VOLT?'
        return self.processor_query_def_min_max(cmd, option).rstrip()

    def set_voltage_source(self, value):
        self.device_handle.write(f':SOUR:VOLT {value}')

    def get_current_source(self, option=None):
        '''
        Full SCPI command:
        :SOURce:CURRent:AMPLitude?

        :return:
        '''
        cmd = ':SOUR:CURR?'
        return self.processor_query_def_min_max(cmd, option).rstrip()

    def set_current_source(self, value):
        self.device_handle.write(f':SOUR:CURR {value}')

    def get_voltage_compliance(self, option=None):
        '''
        Full SCPI Command:
        :SENSe:VOLTage:PROTection:LEVel?

        :param option: <n>, def, default, max, maximum, min, minimum
        :return:
        '''
        cmd = ':VOLT:PROT?'
        return self.processor_query_def_min_max(cmd, option)

    def set_voltage_compliance(self, value):
        '''
        Full SCPI Command:
        :SENSe:VOLTage:PROTection:LEVel <n>

        :param value:
        :return:
        '''
        self.device_handle.write(f':VOLT:PROT {value}')

    def get_current_compliance(self, option=None):
        '''
        Full SCPI command:
        :SENSe:CURRent:PROTection:LEVel?

        :param option: <n>, def, default, max, maximum, min, minimum
        :return:
        '''
        cmd = ':CURR:PROT?'
        return self.processor_query_def_min_max(cmd, option)

    def set_current_compliance(self, value):
        '''
        Full SCPI Command:
        :SENse:CURRent:PROTection:LEVel <n>

        :param value:
        :return:
        '''
        self.device_handle.write(f':CURR:PROT {value}')

    def get_measurement_count(self, option=None):
        '''
        These commands are used to specify the filter count. In general, the filter count is the number of readings that
        are acquired and stored in the filter buffer for the averaging calculation. The larger the filtercount, the
        more filtering that is performed.

        Full SCPI command:
        :SENSe:AVERage:COUNt? [DEFault, MINimum, MAXimum]

        :param option: <n>, def, default, max, maximum, min, minimum
        :return:
        '''
        cmd = ':AVER:COUN?'
        return self.processor_query_def_min_max(cmd, option)

    def set_measurement_count(self, value):
        '''
        These commands are used to specify the filter count. In general, the filter count is the number of readings that
        are acquired and stored in the filter buffer for the averaging calculation. The larger the filtercount, the
        more filtering that is performed.

        ':SENSe:' phrase optional

        Full SCPI command:
        :SENSe:AVERage:COUNt [value, MAXimum, MINimum]


        :param value: 1 to 100, def, default, max, maximum, min, minimum
        :return: None
        '''
        try:
            value = value.lower()
        except:
            pass

        if isinstance(value, (int, float)):
            if value > 100:
                print('Set at max value of 100.')
                self.device_handle.write(':AVER:COUN MAX')
            elif value < 1:
                print('Set at min value of 1.')
                self.device_handle.write(':AVER:COUN MIN')
            else:
                self.device_handle.write(f':AVER:COUN {value}')
        elif value in ['def', 'default']:
            self.device_handle.write(':AVER:COUN DEF')
        elif value in ['max', 'maximum']:
            self.device_handle.write(':AVER:COUN MAX')
        elif value in ['min', 'minimum']:
            self.device_handle.write(':AVER:COUN MIN')
        else:
            print('Invalid string input.')

    def get_current_integration_time(self, option=None):
        '''
        This command is used to set the integration period (speed) for measurements. NPLC (Number of Power Line Cycles) expresses the
        integration period by basing it on the power line frequency. For
        example, for a PLC of 1, the integration period would be 1/60 (for
        60Hz line power) which is 16.67 msec.
        Note that this is a global command. Thus, if you set the speed for
        voltage measurements to 10 PLC, then current and resistance will
        also set to 10 PLC.

        '''
        cmd = ':CURR:NPLC?'
        return self.processor_query_def_min_max(cmd, option)

    def set_current_integration_time(self, value):
        self.device_handle.write(f':CURR:NPLC {value}')

    def get_voltage_integration_time(self, option=None):
        '''
        This command is used to set the integration period (speed) for measurements. NPLC (Number of Power Line Cycles) expresses the
        integration period by basing it on the power line frequency. For
        example, for a PLC of 1, the integration period would be 1/60 (for
        60Hz line power) which is 16.67 msec.
        Note that this is a global command. Thus, if you set the speed for
        voltage measurements to 10 PLC, then current and resistance will
        also set to 10 PLC.

        '''
        cmd = ':VOLT:NPLC?'
        return self.processor_query_def_min_max(cmd, option)

    def set_voltage_integration_time(self, value):
        return self.device_handle.write(f':VOLT:NPLC {value}')

    def get_resistance_integration_time(self, option=None):
        '''
        This command is used to set the integration period (speed) for measurements. NPLC (Number of Power Line Cycles) expresses the
        integration period by basing it on the power line frequency. For
        example, for a PLC of 1, the integration period would be 1/60 (for
        60Hz line power) which is 16.67 msec.
        Note that this is a global command. Thus, if you set the speed for
        voltage measurements to 10 PLC, then current and resistance will
        also set to 10 PLC.

        '''
        cmd = ':RES:NPLC?'
        return self.processor_query_def_min_max(cmd, option)

    def set_resistance_integration_time(self, value):
        self.device_handle.write(f':RES:NPLC {value}')

    def get_measure_voltage_current_and_other(self):
        return self.device_handle.query(':MEAS:CURR:DC?')

    def get_measure_current(self):
        return self.get_measure_voltage_current_other().split(',')[1:2][0]

    def get_measure_voltage(self):
        return self.get_measure_voltage_current_other().split(',')[0:1][0]

    def output_on(self):
        """

        :return: None
        """
        self.device_handle.write(':OUTP:STAT ON')

    def output_off(self):
        return self.device_handle.write(':OUTP:STAT OFF')

    def output_state(self):
        '''
        0 for OFF.
        1 for ON.

        :return:
        '''
        return self.device_handle.query(':OUTP:STAT?')

    def reset(self):
        '''
        Reset to default values.

        :return:
        '''
        self.device_handle.write('*RST')

    def self_test(self):
        '''
        Use this query command to perform a checksum test on ROM. The command places the coded result (0 or 1) in the
        Output Queue. When the SourceMeter is addressed to talk, the coded result is sent from the Output Queue to the
        computer.  A returned value of zero (0) indicates that the test passed, and a value of one (1) indicates that
        the test failed.

        :return:
        '''
        self.device_handle.query('**TST?')

    def read(self):
        return self.device_handle.read()

    def operation_complete(self):
        '''
        When *OPC is sent, the OPC bit in the Standard Event Register will set after all pending command operations are
        complete. When *OPC? is sent, an ASCII “1” is placed in the Output Queue after all pending command operations
        are complete. Typically, either one of these commands is sent after the INITiate command. The INITiate command
        is used to take the instrument out of idle in order to perform measurements. While operating within the trigger
        model layers, all sent commands (except DCL, SDC, IFC, SYSTem:PRESet, *RST, *RCL, *TRG, GET, and ABORt) will not
        execute.  After all programmed operations are completed, the instrument returns to the idle state at which time
        all pending commands (including *OPC and/or *OPC?) are executed. After the last pending command is executed, the
        OPC bit and/or an ASCII “1” is placed in the Output Queue.

        :return:
        '''
        return self.device_handle.query('*OPC?')

    def processor_query_def_min_max(self, cmd, option):
        '''

        :param cmd (str): SCPI command
        :param option: <n>, def, default, max, maximum, min, minimum
        :return:
        '''
        if option is None:
            return self.device_handle.query(cmd)

        try:
            option = option.lower()
        except Exception:
            print('Entry does not do anything.  Set value is::')
            return self.device_handle.query(cmd)

        if option in ['def', 'default']:
            return self.device_handle.query(f'{cmd} DEF')
        elif option in ['max', 'maximum']:
            return self.device_handle.query(f'{cmd} MAX')
        elif option in ['min', 'maximum']:
            return self.device_handle.query(f'{cmd} MIN')
        else:
            print('Entered string does not do anything.  Set value is:')
            return self.device_handle.query(cmd)


if __name__ == '__main__':
    k = Keithley2410()
    print(k.list_resources())
    print(k.get_id())
    k.output_off()

    k.reset()
    k.set_as_current_source()
    print(k.get_source_mode())
    print(k.get_current_source_mode())
    print(k.get_voltage_source_mode())
    # k.voltage_sweep(0,10,1)
    # print(k.get_voltage_sweep_start(0))
    # print(k.set_voltage_sweep_stop(10))
    # print(k.set_voltage_sweep_step(1))
    # print(k.get_voltage_compliance())
    # print(k.get_current_compliance())
    # print(k.get_trigger_count())
    # print(k.get_sourcing_mode())
    # print(k.get_measurement_count())
    # print(k.get_current_integration_time())
    # k.set_measurement_count(100)
    # k.set_current_integration_time(10)
    # while True:
    #     print(k.get_measure_current())
    #     print(k.get_measure_voltage())
    #     time.sleep(1)


    #print(k.get_voltage_sweep_step())
    #print(k.get_function_mode())
    #print(k.get_sourcing_mode())

    # print(k.measure_voltage())
    # print(k.measure_current())

    # print(k.get_voltage_limit())
    # print(k.set_voltage_limit(40))
    # print(k.get_voltage_limit())

    # print(k.get_voltage_compliance())
    # k.set_voltage_compliance(5)
    # print(k.get_voltage_compliance())
    # print(k.get_voltage())
    # k.set_voltage(5)
    # print(k.get_voltage())

    #print(k.output_on())
    # print(k.measure_current())
    # k.set_measurement_count(21)
    # print(k.get_measurement_count())
