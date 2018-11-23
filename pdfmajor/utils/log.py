import logging

logging.basicConfig(
    level=logging.WARNING
)

LOGGERS = {}

def set_log_level(debug_level: int):
    logging.basicConfig(level=debug_level)
    for _, logger in LOGGERS.items():
        logger.setLevel(debug_level)

def get_logger(logger_name: str) -> logging.Logger:
    if logger_name not in LOGGERS.keys():
        LOGGERS[logger_name] = logging.getLogger(logger_name)
    return LOGGERS[logger_name]