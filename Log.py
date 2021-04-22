import logging


class Log:

    def log_info(self, message):
        return logging.info(f"---$---  {message}")

    def log_warning(self, message):
        return logging.warning(f"---$---  {message}")

    def log_error(self, message):
        return logging.error(f"---$---  {message}")
