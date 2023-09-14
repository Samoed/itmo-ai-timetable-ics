import logging


class Logger(logging.Formatter):
    """
    Add colors and formatter for logger
    """

    yellow = "\x1b[33m"
    red = "\x1b[31m"
    white = "\x1b[37m"
    blue = "\x1b[34m"
    reset = "\x1b[0m"
    _format = "%(asctime)s - %(levelname)s - (%(filename)s:%(lineno)d) %(message)s"
    formats = {
        logging.DEBUG: white + _format + reset,
        logging.WARNING: yellow + _format + reset,
        logging.INFO: blue + _format + reset,
        logging.ERROR: red + _format + reset,
        logging.CRITICAL: red + _format + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(Logger())
    logger.addHandler(console_handler)
    return logger
