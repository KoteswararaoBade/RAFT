import logging


def get_log_level(level):
    level = level.upper()
    if level == "DEBUG":
        return logging.DEBUG
    elif level == "INFO":
        return logging.INFO
    elif level == "WARNING":
        return logging.WARNING
    elif level == "ERROR":
        return logging.ERROR
    elif level == "CRITICAL":
        return logging.CRITICAL
    else:
        return logging.DEBUG


class LoggingUtil:
    def __init__(self, name, log_file_name=None, log_level="DEBUG"):
        """
        Create a logger with a file handler and a stream handler
        :param name: logger name
        :param log_file_name: log file name
        :param log_level: log level
        """
        self.logger = logging.getLogger(name=name)
        self.logger.setLevel(get_log_level(log_level))
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.stream_handler = logging.StreamHandler()
        self.stream_handler.setLevel(get_log_level(log_level))
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)
        if log_file_name is not None:
            self.file_handler = logging.FileHandler(log_file_name)
            self.file_handler.setLevel(get_log_level(log_level))
            self.file_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.file_handler)

    def get_logger(self):
        """
        Get the logger
        :return: logger
        """
        return self.logger
