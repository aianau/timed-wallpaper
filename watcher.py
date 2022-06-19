from dotenv import load_dotenv
import os
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler
import json
import time
import logging
from logging.handlers import RotatingFileHandler
import schedule
from sun import Sun
import datetime as dt
import random
import subprocess
import sys
import platform

class ReloadConfig(RegexMatchingEventHandler):
    def __init__(self, on_modified_func,  regexes=None, ignore_regexes=None,
                 ignore_directories=False, case_sensitive=False) -> None:
        super().__init__(regexes, ignore_regexes, ignore_directories, case_sensitive)
        self.on_modified = on_modified_func


class Watcher:
    def __init__(self, config_path):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)

        self._config_path = os.path.abspath(config_path)
        self._config = None

        self._read_config()

        read_config_func = lambda event: self._read_config()
        self._obsever = Observer()
        self._event_handler = ReloadConfig(read_config_func, regexes=[f'.*\\\\{os.path.basename(self._config_path)}'])
        self._obsever.schedule(self._event_handler, os.path.dirname(self._config_path), recursive=False)
        self._obsever.start()

        self._sun = Sun()
        self._update_details()

        self.update_wallpaper(self._sun.get_current_moment())

    def _update_details(self):
        schedule.clear()
        schedule.every().day.at('00:01').do(self._update_details)

        for moment, time in self._sun.get_moments().items():
            schedule.every().day.at(time.strftime('%H:%m')).do(self.update_wallpaper, moment)

    def _read_config(self):
        self._logger.info(f'Reading config file: {self._config_path}')
        load_dotenv('.env')
        with open(self._config_path) as f:
            self._config = json.load(f)
        self._logger.info(f'Config file readed: \n{json.dumps(self._config, indent=4)}')

    def run(self):
        self._logger.info('Starting watcher')

        while True:
            time.sleep(1)
            schedule.run_pending()
        

    def update_wallpaper(self, moment):
        images = self._config['times'][moment]['images']
        if len(images) == 0:
            self._logger.error(f'No images for moment: {moment}')
            return
        i = random.randint(0, len(images) - 1)
        current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        img_path = os.path.join(current_dir, 'images', images[i])
        if not os.path.exists(img_path):
            self._logger.error(f'Image not found: {img_path}')
            return
        if platform.platform().startswith('Windows'):
            cmd = ['reg', 'add', 'HKEY_CURRENT_USER\Control Panel\Desktop', '/v', 'Wallpaper', '/t', 'REG_SZ', '/d', img_path, '/f']
            subprocess.run(cmd)
            cmd = ['RUNDLL32.EXE', 'user32.dll', ',', 'UpdatePerUserSystemParameters']
            subprocess.run(cmd)
        else:
            self._logger.error(f'Not implemented update wallpaper for this platform: {platform.platform()}')
            return
        self._logger.info(f'Wallpaper updated: {img_path}')
        

def main():
    watcher = Watcher('config.json')
    watcher.run()


if __name__ == "__main__":
    main()



