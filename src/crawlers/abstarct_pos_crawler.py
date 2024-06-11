from abc import ABC
import logging


class BasePosCrawler(ABC):
    def __init__(self, logging_prefix=""):
        self.logger = logging.getLogger(logging_prefix)
    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)
