import logging

class CustomFormatter(logging.Formatter):

    GREY = "\x1b[1;38"
    GREEN = "\x1b[1;32m"
    YELLOW = "\x1b[1;33m"
    RED = "\x1b[1;31m"
    MAGENTA = "\x1b[1;35m"
    RESET = "\x1b[0m"

    # Base format (without coloring)
    DETAILED_LOGS = """{level_color}%(levelname)s{reset} - %(name)s - %(asctime)s
    ---> {level_color}%(filename)s:%(lineno)d{reset}
-- DETAILS --
%(message)s
-------------"""

    RAW_LOGS = """{level_color}%(levelname)s{reset} - %(filename)s - %(asctime)s
    ---> %(message)s"""

    LEVEL_FORMATS = {
        logging.DEBUG: DETAILED_LOGS,
        logging.INFO: RAW_LOGS,
        logging.WARNING: RAW_LOGS,
        logging.ERROR: DETAILED_LOGS,
        logging.CRITICAL: DETAILED_LOGS,
    }

    LEVEL_COLORS = {
        logging.DEBUG: YELLOW,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: MAGENTA,
    }

    def format(self, record):
        color = self.LEVEL_COLORS.get(record.levelno, self.GREY)
        template = self.LEVEL_FORMATS.get(record.levelno, self.RAW_LOGS)
        format_string = template.format(level_color=color, reset=self.RESET)
        formatter = logging.Formatter(format_string, datefmt="%H:%M:%S")
        return formatter.format(record)
