import logging
from logging.handlers import RotatingFileHandler
from watcher import Watcher

root_logger = logging.getLogger()
formatter = logging.Formatter('%(asctime)s [%(levelname)-5.5s] [%(name)s]- %(message)s')
root_logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler('logging.log', maxBytes=1024*1024, backupCount=2)
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
root_logger.addHandler(stream_handler)


def main():
    watcher = Watcher('config.json')
    watcher.run()


if __name__ == "__main__":
    main()

