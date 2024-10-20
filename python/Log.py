import logging

logging.basicConfig(level=logging.INFO)

class Log:
    def __init__(self, log_able=False):
        self._log_able = log_able

    @property
    def log_able(self):
        return self._log_able

    @log_able.setter
    def log_able(self, able):
        if not isinstance(able, bool):
            raise ValueError("log_able must be a boolean value")
        self._log_able = able

    def message(self, text, level='INFO'):
        if self.log_able:
            if level == 'INFO':
                logging.info(text)
            elif level == 'WARNONG':
                logging.warning(text)
            elif level == 'ERROR':
                logging.error(text)

log = Log()