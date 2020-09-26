import logging

from signal import SIGINT, SIGTERM, signal


class SignalHandler:
    def __init__(self, logger: logging.Logger):
        self.received_signal = False
        self.logger = logger
        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, signal, frame):
        self.logger.critical(f"received signal {signal} from host, exiting")
        self.received_signal = True
