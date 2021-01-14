import pyvisa
import time
import re


class Chromometer:
    """
    See document "acton_2150i_operating_instructions.pdf" page 9 for commands.
    Alternative instrument control via MonoControl (by Princeton Instruments) for download at:
    ftp://ftp.princetoninstruments.com/Public/Software/Official/Acton/Mono-Control%205.2.4.zip
    Run app as administrator.
    """
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.device_handle = self.rm.open_resource("COM4")

    def __del__(self):
        self.rm.close()

    def initialize_defaults(self):
        self.set_wavelength_nm("200.0 NM")
        self.set_scan_speed_nm_p_min("120 NM/MIN")

    def print_resource_ids(self):
        return print("Resource List: ", self.rm.list_resources(), "\n")

    def read(self):
        return self.device_handle.read()

    def set_scan_speed_nm_p_min(self, rate):
        """
        Sets scan speed.
        Ex. 100.0 NM/MIN (this sets the scan rate to 100 nm per/min).

        :param rate:
        :return: str "[rate] NM/MIN ok"
        """
        return self.device_handle.query(str(rate) + " NM/MIN")

    def scan_to(self, wavelength):
        """
        Goes to destination wavelength to nearest 0.1 nm at selected scan rate.
        Ex. 250.0NM (causes the SP-2150i to go to 250 nm).

        I did not verify if this method works.
        Need to check of return strings means anything.

        :param wavelength:
        :return: str "[scan_to_wavelength]NM [scan_to_wavelength]NM ?"
        """
        return self.device_handle.query(str(wavelength) + "NM")

    def set_wavelength_nm(self, wavelength):
        """
        Goes to destination wavelength to nearest 0.1 nm at selected scan rate.
        Ex. 250.0 NM (causes the SP-2150i to go to 250 nm).

        Must wait until target wavelength reached.  Safety factor of 1.1 used.
        Pinging chromometer while adjusting throws pyVISA IOError.


        :param wavelength:
        :return:
        """
        delta_wavelength_nm = abs(round(self.get_wavelength_nm_clean_output() - wavelength))
        time_to_sleep = round((60 * delta_wavelength_nm) / self.get_scan_speed_nm_p_min_clean_output() * 1.1, 2)
        try:
            self.device_handle.query(str(wavelength) + " NM")

        except Exception:
            print("Adjustment Time:", time_to_sleep, "seconds")
            time.sleep(time_to_sleep)
            self.read()

        return self.get_wavelength_nm_clean_output()

    def set_grating(self, grating):
        """
        Selects either the first or second grating on the selected turret. Requires approximately 20 seconds.
        Ex. 2 GRATING (indexes grating number 2 into position.  Moves to the same wavelength as the previous grating
        or 200 nm default if wavelength is not accessible by the selected grating).

        Input "1" or "2".
        Ex. Chromometer().set_grating(2))

        :return:
        """
        try:
            return self.device_handle.query(str(grating) + " GRATING")

        except Exception:
            print("Please Wait...")
            time.sleep(1)
            self.set_grating(grating)

    def set_turret(self, turret):
        """
        Selects parameters for the gratings on turret 1, 2, or 3.
        Ex. 2 TURRET (selects parameters for turret number 2).

        :param turret:
        :return:
        """
        return self.device_handle.query(str(turret) + " TURRET")

    def get_wavelength_nm_raw_output(self):
        """
        Sends the current wavelength to the computer or terminal with the format 250.0.
        Returns nasty format: ?NM 300.000 nm ok

        :return:
        """
        return self.device_handle.query("?NM")

    def get_wavelength_nm_clean_output(self):
        """
        Sends the current wavelength to the computer or terminal with the format 250.0.
        Returns clean format: 300.000

        :return: float
        """
        return float(re.sub(r"[^0123456789.]", "", self.get_wavelength_nm_raw_output()))

    def get_scan_speed_nm_p_min_raw_output(self):
        """
        Sends the present scan speed to computer or terminal with the format 100.0.
        Returns raw format: [rate] NM/MIN ok

        :return: str "[rate] NM/MIN ok"
        """
        return self.device_handle.query("?NM/MIN")

    def get_scan_speed_nm_p_min_clean_output(self):
        """
        Sends the present scan speed to computer or terminal with the format 100.0.
        Returns clean format: [rate]

        :return: float "[rate]"
        """
        return float(re.sub(r"[^0123456789.]", "", self.get_scan_speed_nm_p_min_raw_output()))

    def get_grating(self):
        """
        Sends the present grating position (1 or 2) on the selected turret to the computer or terminal.

        :return:
        """
        return self.device_handle.query("?GRATING")

    def get_grating_spacing_and_blaze_wavelength(self):
        """
        Sends the groove spacing and blaze wavelength of each grating position 1 through 6 (2 grating positions for each
        of the 3 turrets) to the computer or terminal.

        :return:
        """
        self.device_handle.write("?GRATINGS")
        for i in range(5):
            print(self.read())
        return self.read()

    def get_turret_number(self):
        """
        Sends the selected turret number (1,2,3, or 4) to the computer terminal.

        :return:
        """
        return self.device_handle.query("?TURRET")

    def get_groove_spacing(self):
        """
        Sends the groove spacing of each grating for each turret to the computer or terminal.

        :return:
        """
        return self.device_handle.query("?TURRETS")


if __name__ == "__main__":
    c = Chromometer()
    c.print_resource_ids()
    c.set_scan_speed_nm_p_min(300)
    print("Current wavelength: ", c.get_wavelength_nm_clean_output())
    print(c.set_wavelength_nm(300))
