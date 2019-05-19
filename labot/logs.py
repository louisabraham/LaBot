import logging
import time

import colorama
from colorama import Fore, Style

colorama.init()


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "WARNING": Fore.YELLOW,
        "INFO": Fore.WHITE,
        "DEBUG": Fore.BLUE,
        "CRITICAL": Fore.YELLOW,
        "ERROR": Fore.RED,
    }

    FORMAT = (
        f"{Fore.GREEN}%(asctime)s %(levelname)s: "
        f"{Fore.CYAN}%(threadName)s - [%(pathname)s:%(lineno)d] "
        f"in %(funcName)s():\n{Fore.WHITE}%(message)s\n"
        f"{Style.RESET_ALL}"
    )

    def __init__(self):
        logging.Formatter.__init__(self, self.FORMAT, "%H:%M:%S")

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = self.COLORS[levelname] + levelname + Style.RESET_ALL
        return logging.Formatter.format(self, record)

    def formatTime(self, record, datefmt):
        ct = self.converter(record.created)
        t = time.strftime(datefmt, ct)
        s = self.default_msec_format % (t, record.msecs)
        return s


color_formatter = ColoredFormatter()
logger = logging.getLogger("labot")
handler = logging.StreamHandler()
handler.setFormatter(color_formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
