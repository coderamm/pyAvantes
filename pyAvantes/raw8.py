# NOTICE: This is a modified version from scholi/pyAvantes/pyAvantes/raw8.py
# See the NOTICE at the repository top level for a description of changes.

import datetime as datetime
import struct

from dataclasses import dataclass
import numpy as np

_Raw8_Fields = [
    ("version", "5s"),
    ("numSpectra", "B"),
    ("length", "I"),
    ("seqNum", "B"),
    (
        "measMode",
        "B",
        {
            0: "scope",
            1: "absorbance",
            2: "scope corrected for dark",
            3: "transmission",
            4: "reflectance",
            5: "irradiance",
            6: "relative irradiance",
            7: "temperature",
        },
    ),
    ("bitness", "B"),
    ("SDmarker", "B"),
    ("specID", "10s"),
    ("userfriendlyname", "64s"),
    ("status", "B"),
    ("startPixel", "H"),
    ("stopPixel", "H"),
    ("integrationTime", "f"),
    ("integrationdelay", "I"),
    ("Avg", "I"),
    ("enable", "B"),
    ("forgetPercentage", "B"),
    ("Boxcar", "H"),
    ("smoothmodel", "B"),
    ("saturationdetection", "B"),
    ("TrigMode", "B"),
    ("TrigSource", "B"),
    ("TrigSourceType", "B"),
    ("strobeCtrl", "H"),
    ("laserDelay", "I"),
    ("laserWidth", "I"),
    ("laserWavelength", "f"),
    ("store2ram", "H"),
    ("timestamp", "I"),
    ("SPCfiledate", "I"),
    ("detectorTemp", "f"),
    ("boardTemp", "f"),
    ("NTC2volt", "f"),
    ("ColorTemp", "f"),
    ("CalIntTime", "f"),
    ("fitdata", "5d"),
    ("comment", "130s"),
]


def plank_function(temp: float, wl: np.array):
    c = 3e8  # speed of light [m s**−1]
    h = 6.625e-34  # Planck constant [J s]
    kb = 1.38e-23  # Boltzmann constant [J K**−1]
    return ((2 * h * c**2) / (wl**5)) * 1.0 / (np.exp((h * c) / (wl * kb * temp)) - 1)


@dataclass
class Raw8:
    def __init__(self, filename: str):
        self.header = {}
        with open(filename, "rb") as f:
            for k in _Raw8_Fields:
                s = struct.Struct(k[1])
                dat = s.unpack(f.read(s.size))
                if len(dat) == 1:
                    dat = dat[0]
                if "s" in k[1]:
                    dat = dat.decode("latin1").split("\x00")[0]
                self.header[k[0]] = dat
            data_length = self.header["stopPixel"] - self.header["startPixel"] + 1
            self.data_length = data_length
            self.data = {
                "wl": struct.unpack(f"<{data_length}f", f.read(4 * data_length)),
                "scope": struct.unpack(f"<{data_length}f", f.read(4 * data_length)),
                "dark": struct.unpack(f"<{data_length}f", f.read(4 * data_length)),
                "ref": struct.unpack(f"<{data_length}f", f.read(4 * data_length)),
            }

    def get_data(self, name: str):
        return np.array(self.data[name])

    @property
    def scope(self):
        return self.get_data("scope")

    @property
    def wavelength(self):
        return self.get_data("wl")

    @property
    def dark(self):
        return self.get_data("dark")

    @property
    def ref(self):
        return self.get_data("ref")

    @property
    def black_body(self):
        return plank_function(self.header["ColorTemp"], self.wavelength * 1e-9)

    @property
    def relative_irradiance(self):
        return self.black_body * (self.scope - self.dark)

    # This is from the manual: http://www.content.mphotonics.de/AVA/AVASOFT_Manual_8.4.pdf
    # Page 35. But I'm not conviced that this is correct

    def get_header(self, name: str):
        return self.header[name]

    @property
    def version(self):
        return self.get_header("version")

    @property
    def num_spectra(self):
        return self.get_header("numSpectra")

    @property
    def length(self):
        return self.get_header("length")

    @property
    def sequence_number(self):
        return self.get_header("seqNum")

    @property
    def measurement_mode(self):
        return self.get_header("measMode")

    @property
    def bitness(self):
        return self.get_header("bitness")

    @property
    def SD_marker(self):
        return self.get_header("SDmarker")

    @property
    def specID(self):
        return self.get_header("specID")

    @property
    def user_friendly_name(self):
        return self.get_header("userfriendlyname")

    @property
    def status(self):
        return self.get_header("status")

    @property
    def start_pixel(self):
        return self.get_header("startPixel")

    @property
    def stop_pixel(self):
        return self.get_header("stopPixel")

    @property
    def integration_time(self):
        return self.get_header("integrationTime")

    @property
    def integration_delay(self):
        return self.get_header("integrationdelay")

    @property
    def average(self):
        return self.get_header("Avg")

    @property
    def enable(self):
        return self.get_header("enable")

    @property
    def forget_percentage(self):
        return self.get_header("forgetPercentage")

    @property
    def boxcar(self):
        return self.get_header("Boxcar")

    @property
    def smooth_model(self):
        return self.get_header("smoothmodel")

    @property
    def saturation_detection(self):
        return self.get_header("saturationdetection")

    @property
    def timestamp(self):
        return self.get_header("timestamp")

    @property
    def trigger_mode(self):
        return self.get_header("TrigMode")

    @property
    def trigger_source(self):
        return self.get_header("TrigSource")

    @property
    def trigger_type(self):
        return self.get_header("TrigSourceType")

    @property
    def strobe_control(self):
        return self.get_header("strobeCtrl")

    @property
    def laser_delay(self):
        return self.get_header("laserDelay")

    @property
    def laser_width(self):
        return self.get_header("laserWidth")

    @property
    def laser_wavelength(self):
        return self.get_header("laserWavelength")

    @property
    def store2ram(self):
        return self.get_header("store2ram")

    @property
    def SPCfiledate(self):
        return self.get_header("SPCfiledate")

    @property
    def detector_temp(self):
        return self.get_header("detectorTemp")

    @property
    def board_temp(self):
        return self.get_header("boardTemp")

    @property
    def NTC2volt(self):
        return self.get_header("NTC2volt")

    @property
    def color_temp(self):
        return self.get_header("ColorTemp")

    @property
    def calibration_integration_time(self):
        return self.get_header("CalIntTime")

    @property
    def calibration_constants(self):
        return self.get_header("fitdata")

    @property
    def comment(self):
        return self.get_header("comment")

    @property
    def date(self):
        d = self.header["SPCfiledate"]
        return {
            "year": d >> 20,
            "month": (d >> 16) % (2**4),
            "day": (d >> 11) % (2**5),
            "hour": (d >> 6) % (2**5),
            "minute": d % (2**6),
        }

    @property
    def datetime(self):
        d = self.date
        return datetime.datetime(
            d["year"], d["month"], d["day"], d["hour"], d["minute"]
        )
