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
    ("IntTime", "f"),
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
