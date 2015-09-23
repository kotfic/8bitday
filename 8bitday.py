from pkg_resources import resource_filename
from datetime import datetime as dt
from datetime import timedelta
import subprocess
import json
import requests
import argparse
import time
import os
import sys

try:
    from io import StringIO
except ImportError:
    from cStringIO import StringIO

try:
    import ConfigParser as cp
except ImportError:
    import configparser as cp


CONFIG = os.path.expanduser("~/.config/nitrogen/bg-saved.cfg")

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

    def __init__(self, cached=False):
        self.config = cp.ConfigParser()
        self.config.readfp(open(resource_filename(__name__, 'config')))

        self._api_key = self.config.get("default", "api_key")
        self._lat = self.config.get("default", "latitude")
        self._lon = self.config.get("default", "longitude")

        if cached == True:
            self.weather = self._cache_weather()
        else:
            try:
                self.weather = self.fetch_weather()
                self._cache_weather(self.weather)
            except:
                self.weather = self._cache_weather()

    def fetch_weather(self):
        r = requests.get("https://api.forecast.io/forecast/{}/{},{}".format(
            self._api_key, self._lat, self._lon))
        return r.json()


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
        return dt.fromtimestamp(
            self.weather['daily']['data'][0]['sunriseTime'])

    @property
    def sunset(self):
        return dt.fromtimestamp(
            self.weather['daily']['data'][0]['sunsetTime'])

    @property
    def timezone(self):
        return self.weather['timezone']

    def get_weather(self):
        # For now we only have sunny
        return "sunny_no_sun"


def set_wallpaper(filename):
    nitrogen_config = """
[xin_0]
file={0}
mode=0
bgcolor=#000000

[xin_1]
file={0}
mode=0
bgcolor=#000000
""".format(filename)

    cfg = cp.ConfigParser()
    cfg.readfp(StringIO(nitrogen_config.decode('utf-8')))

    with open(CONFIG, 'wb') as fh:
        cfg.write(fh)

    os.environ['DISPLAY'] = ":0.0"
    subprocess.call(["/usr/bin/nitrogen", "--restore"])


def base_dir():
    return resource_filename(__name__, 'img/')


cutoffs = [
    ("08-Late-Night.png", lambda w: w.sunrise - timedelta(hours=2)),
    ("07-Night.png", lambda w: w.sunrise),
    ("01-Morning.png", lambda w: w.sunrise + timedelta(hours=1)),
    ("02-Late-Morning.png", lambda w: w.sunrise + ((w.sunset - w.sunrise) / 2)),
    ("03-Afternoon.png", lambda w: w.sunset - timedelta(hours=1)),
    ("04-Late-Afternoon.png", lambda w: w.sunset - timedelta(minutes=30)),
    ("05-Evening.png", lambda w: w.sunset - timedelta(minutes=15)),
    ("06-Late-Evening.png", lambda w: w.sunset + timedelta(minutes=5)),
    ("07-Night.png", lambda w: w.sunset + timedelta(hours=3))]


def get_file_name(now, w):
    for filename, func in cutoffs:
        if now < func(w):
            return filename

    return "08-Late-Night.png"


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle", "-c", type=float)
    parser.add_argument("--debug", "-d", action="store_true")

    args = parser.parse_args()

    if args.debug:
        try:
            import pudb; pu.db
        except ImportError:
            import pdb; pdb.set_trace()


    w = Weather()
    now = dt.now()

    if args.cycle:
        print("NOW: {}".format(now.isoformat()))

        for f, func in cutoffs:
            print("{}: {}".format(f, func(w).isoformat()))

            set_wallpaper(os.path.join(base_dir(), w.get_weather(), f))
            time.sleep(args.cycle)


    set_wallpaper(os.path.join(base_dir(),
                               w.get_weather(),
                               get_file_name(now, w)))


if __name__ == "__main__":
    main()
