import astral
import datetime as dt
from astral.sun import sun, golden_hour, blue_hour, SunDirection, midnight, sunrise, sunset
import json
import pprint
from typing import Dict, Union
import pytz
import logging


class Sun(object):
    def __init__(self) -> None:
        self._logger = logging.getLogger(__name__)
        self._timezone_name = 'Europe/Bucharest'
        self._city = astral.LocationInfo(name='Targu Mures', region='Romania', latitude=46.539749, longitude=24.558581, timezone=self._timezone_name)
        self._moments = None
        self._last_update = dt.datetime.now() - dt.timedelta(days=1, minutes=1)
        self._update_moments()
    
    def _print_moments(self) -> None:
        self._logger.info('Moments:')
        for moment, time in self._moments.items():
            self._logger.info(f'{moment:>20}: {time.strftime("%H:%M")}')

    def _update_moments(self) -> None:
        now = dt.datetime.now()
        if self._last_update and now - self._last_update <= dt.timedelta(days=1):
            return
        
        s = sun(self._city.observer, date=dt.datetime.now(), tzinfo=self._city.timezone)
        self._moments = {
            'midnight': midnight(observer=self._city.observer, date=dt.datetime.now(), tzinfo=self._city.timezone),
            'morning blue hour': blue_hour(observer=self._city.observer, date=dt.datetime.now(), direction=SunDirection.RISING, tzinfo=self._city.timezone)[0],
            'morning golden hour': golden_hour(observer=self._city.observer, date=dt.datetime.now(), direction=SunDirection.RISING, tzinfo=self._city.timezone)[0],
            'sunrise': s["sunrise"],
            'noon':    s["noon"],
            'evening golden hour': golden_hour(observer=self._city.observer, date=dt.datetime.now(), direction=SunDirection.SETTING, tzinfo=self._city.timezone)[0],
            'evening blue hour': blue_hour(observer=self._city.observer, date=dt.datetime.now(), direction=SunDirection.SETTING, tzinfo=self._city.timezone)[0],
            'dusk':    s["dusk"],
        }
        self._moments = dict(sorted(self._moments.items(), key=lambda x: x[1]))
        self._last_update = dt.datetime.now()

        self._print_moments()

    def get(self, moment: Union[str, dt.datetime]) -> dt.datetime:
        self._update_moments()
        
        if isinstance(moment, str):
            return self._moments[moment.lower()]
        if isinstance(moment, dt.datetime):
            for i in range(len(self._moments)-1):
                if self._moments[i][1] <= moment and moment <= self._moments[i+1][1]:
                    return self._moments[i][1]
            return self._moments[-1][1]
    
    def get_current_moment(self) -> str:
        self._update_moments()
        
        tz = pytz.timezone(self._timezone_name)
        now = dt.datetime.now(tz=tz)
        for i in range(len(self._moments)-1):
            i_next = list(self._moments.keys())[i+1]
            i = list(self._moments.keys())[i]

            if self._moments[i] <= now and now <= self._moments[i_next]:
                return i
        return self._moments.keys()[-1]

    def get_moments(self) -> Dict[str, dt.datetime]:
        self._update_moments()

        return self._moments
        

def main():
    sun = Sun()
    sun.get('midnight')


if __name__ == "__main__":
    main()