from pkg_resources import resource_filename
import datetime as dt
from dateutil.parser import parse
import subprocess
import pywapi
import json
import argparse
import time
import os

try:
    import ConfigParser as cp
except ImportError:
    import configparser as cp


CONFIG = "/home/kotfic/.config/nitrogen/bg-saved.cfg"

FILES = ["01-Early-Morning.jpg",
         "02-Morning.jpg",
         "03-Late-Morning.jpg",
         "04-Afternoon.jpg",
         "05-Late-Afternoon.jpg",
         "06-Evening.jpg",
         "07-Late-Evening.jpg",
         "08-Night.jpg",
         "09-Late-Night.jpg"]


class Weather(object):

    def __init__(self, location):
        try:
            self.weather = pywapi.get_weather_from_yahoo(location)
            self._cache_weather(self.weather)
        except:
            self.weather = self._cache_weather()

    def _cache_weather(self, weather_json=None):
        cache = resource_filename(__name__, '.last_weather.json')

        if weather_json is None:
            with open(cache, "r") as fh:
                return json.loads(fh.read())
        else:
            with open(cache, "w") as fh:
                fh.write(json.dumps(weather_json))
            return None

    @property
    def sunrise(self):
        return parse(self.weather['astronomy']['sunrise'])

    @property
    def sunset(self):
        return parse(self.weather['astronomy']['sunset'])

    def get_weather(self):
        # For now we only have sunny
        return "sunny_no_sun"


def set_wallpaper(filename):
    write = False

    cfg = cp.ConfigParser()
    cfg.read(CONFIG)

    for section in cfg.sections():
        if cfg.get(section, "file") != filename:
            cfg.set(section, "file", filename)
            write = True

    if write:
        with open(CONFIG, 'wb') as fh:
            cfg.write(fh)
        subprocess.call(["/usr/bin/nitrogen", "--restore"])


def base_dir():
    return resource_filename(__name__, 'img/')


def get_file_name(now, w):
    
    # Well before sunrise
    if now < (w.sunrise - dt.timedelta(hours=2)):
        return "08-Late-Night.png"

    #Sunrise
    elif now < w.sunrise:
        return "07-Night.png"

    # Early Morning
    elif now < (w.sunrise + dt.timedelta(hours=1)):
        return "01-Morning.png"

    # Until Midday
    elif now < (w.sunrise +  ((w.sunset - w.sunrise) / 2)):
        return "02-Late-Morning.png"

    elif now < (w.sunset - dt.timedelta(hours=1)):
        return "03-Afternoon.png"

    # Late Afternoon
    elif now < (w.sunset - dt.timedelta(minutes=30)):
        return "04-Late-Afternoon.png"

    # Sun setting
    elif now < (w.sunset - dt.timedelta(minutes=15)):
        return "05-Evening.png"

    # Through Sunset
    elif now < (w.sunset + dt.timedelta(minutes=5)):
        return "06-Late-Evening.png"

    # Early Night
    elif now < (w.sunset + dt.timedelta(hours=3)):
        return "07-Night.png"

    else:
        return "08-Late-Night.png"


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle", "-c", type=float)
    parser.add_argument("--debug", "-d", type=str)

    args = parser.parse_args()

    w = Weather("12180")
    now = dt.datetime.now()

    if args.cycle:
        for f in sorted(os.listdir(os.path.join(base_dir(),
                                                w.get_weather()))):
            set_wallpaper(os.path.join(base_dir(), w.get_weather(), f))
            time.sleep(args.cycle)

    if args.debug:
        print(w.sunrise)
        print(w.sunset)
        now = parse(args.debug)

    set_wallpaper(os.path.join(base_dir(),
                               w.get_weather(),
                               get_file_name(now, w)))


if __name__ == "__main__":
    main()
