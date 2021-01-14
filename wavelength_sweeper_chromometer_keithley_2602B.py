import pyvisa
import argparse
import time
import pandas as pd
import matplotlib.pyplot as plt

from sp_2150i_chromometer_driver import Chromometer
from keithley_2602B_driver import Keithley2602B
from thorlabs_pm100_driver import ThorlabsPM100

"""
For Keithley 2602B (40V limit)
"""

class Debug:
    def print_resource_ids(self):
        print("Resource List: ", rm.list_resources(), "\n")
        print("TL ID: ", thorlabs_pm100_handle.query("*IDN?"))
        print("Keithley ID: ", keithley_handle.query("*IDN?"))

    def print_pm100_commands(self):
        print(pm100.take_power_measurement())

    def print_chromometer_commands(self):
        print(chromometer.get_wavelength_nm_raw_ouput())
        print(chromometer.get_scan_speed_nm_p_min())
        print(chromometer.get_grating_position())
        print(chromometer.get_grating_spacing_and_blaze_wavelength())
        #print(chrom.get_turrent_number())
        #print(chrom.get_turrent_spacing())


class Plotter:
    def line_dot_plot(self, data):
        plot_kwargs = {"grid": True}
        data.plot(kind="line", x="wl_chromometer_list", y="rev_bias_list", **plot_kwargs)
        #plt.plot(data["rev_bias_list"], "ro-")
        plt.title("Rev Bias Current [mA?] vs. Wavelength [nm]")
        plt.xlabel("Wavelength [nm]")
        plt.ylabel("Rev Bias Current [mA?]")
        #plt.xticks(range(len(data["wl_chromometer_list"])), data["wl_chromometer_list"])
        #plt.grid()
        plt.savefig(filename + string_time)
        plt.show()


def wavelength_list_generator(start, stop, step):
        my_list = []
        while start < stop:
            my_list.append(start)
            start += step
        return my_list


def arg_handler(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("wavelength_start_coarse", type=int, help="The sweep start wavelength as integer.")
    parser.add_argument("wavelength_stop_coarse", type=int, help="The sweep end wavelength as integer.")
    parser.add_argument("wavelength_step_coarse", type=int, help="The sweep step in nanometers [nm].")

    parser.add_argument("wavelength_start_fine", type=int, nargs='?', help="The sweep start wavelength as integer.")
    parser.add_argument("wavelength_stop_fine", type=int, nargs='?', help="The sweep stop wavelength as integer.")
    parser.add_argument("wavelength_step_fine", type=int, nargs='?', help="The sweep step in nanometers [nm].")

    args = parser.parse_args(argv)

    global wl_start_coarse
    global wl_stop_coarse
    global wl_step_coarse

    global wl_start_fine
    global wl_stop_fine
    global wl_step_fine

    wl_start_coarse = args.wavelength_start_coarse
    wl_stop_coarse = args.wavelength_stop_coarse
    wl_step_coarse = args.wavelength_step_coarse

    wl_start_fine = args.wavelength_start_fine
    wl_stop_fine = args.wavelength_stop_fine
    wl_step_fine = args.wavelength_step_fine


if __name__ == '__main__':
    chromometer = Chromometer()
    pm100 = ThorlabsPM100()
    keithley = Keithley2602B()
    debug = Debug()
    wl_chromometer_list = []
    rev_bias_list = []

    print(keithley.get_id())
    #print(pm100.measure_current())
    keithley.keithley_initialize_2410()

    arg_handler()  # creates wavelength variables

    wl_list_coarse = [*range(wl_start_coarse, wl_stop_coarse + wl_step_coarse, wl_step_coarse)]

    if wl_start_fine is not None:
        wl_list_fine = [*range(wl_start_fine, wl_stop_fine + wl_step_fine, wl_step_fine)]
        wl_list = [wl for wl in wl_list_coarse if wl < wl_start_fine] + \
                   wl_list_fine + \
                  [wl for wl in wl_list_coarse if wl > wl_stop_fine]
    else:
        wl_list = wl_list_coarse

    print(wl_list)

    keithley.smua_output_on()
    chrom_scan_speed = 300
    chromometer.set_scan_speed_nm_p_min(chrom_scan_speed)

    for wavelength in wl_list:
        print("chrom speed: ", chromometer.get_scan_speed_nm_p_min_clean_output())
        print("current chrom wl: ", chromometer.get_wavelength_nm_clean_output())
        print("set wl: ", wavelength)

        # find wavelength difference btwn current and target value
        delta_wavelength_nm = abs(round(chromometer.get_wavelength_nm_clean_output() - wavelength))
        chromometer.set_wavelength_nm(wavelength)

        # must wait until chromometer reaches target wavelength, with safety factor at end
        time.sleep((60 * delta_wavelength_nm) / chrom_scan_speed * 1.2)
        print("current chrom wl: ", chromometer.get_wavelength_nm_clean_output())

        avg_list = [keithley.SCPI_measure_i_clean() for i in range(0, 9)]
        #print(avg_list)
        avg = sum(avg_list)/len(avg_list)
        #print(avg)

        wl_chromometer_list.append(chromometer.get_wavelength_nm_clean_output())
        #rev_bias_list.append(keithley.SCPI_measure_i_clean())
        rev_bias_list.append(avg)

    keithley.smua_output_off()

    combined_list = list(zip(wl_chromometer_list, rev_bias_list))
    string_time = time.strftime("%Y-%m-%d_%H-%M-%S")

    df = pd.DataFrame(combined_list, columns=["wl_chromometer_list", "rev_bias_list"])
    df = df.assign(Voltage=keithley.SCPI_get_source_voltage())
    filename = "main_v4_red_0V_"
    df.to_csv(filename + string_time + ".csv", index=None)
    print(df)

    Plotter().line_dot_plot(df)

