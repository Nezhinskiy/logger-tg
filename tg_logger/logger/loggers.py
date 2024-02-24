import logging
import sys
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler

from tg_logger.logger.logger_warner import ClientLogger
from tg_logger.settings import SyncTgLoggerSettings
from tg_logger.utils import model_dict_or_none


class BaseLogger:
    shrug: str = ''.join(map(chr, (175, 92, 95, 40, 12484, 41, 95, 47, 175)))
    FORMATTER: logging.Formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s'
    )

    def __init__(
            self,
            bot_token: str = None,
            recipient_id: int = None,
            name: str = 'app',
    ) -> None:
        self.logger = logging.getLogger(name)
        self.start_time = datetime.now(timezone.utc)
        self.tg_logger = self.configure_tg_logger(bot_token, recipient_id)

    def __getattr__(self, name: str) -> callable:
        if name.startswith('__') and name.endswith('__'):
            return super().__getattr__(name)
        return lambda *args, **kwargs: self.log_message(name, *args, **kwargs)

    @staticmethod
    def get_console_log_handler(
            formatter: logging.Formatter = FORMATTER,
            level: int = logging.DEBUG
    ) -> logging.StreamHandler:
        console_log_handler = logging.StreamHandler(sys.stderr)
        console_log_handler.setFormatter(formatter)
        console_log_handler.setLevel(level)
        return console_log_handler

    @staticmethod
    def get_file_log_handler(
            path: str,
            formatter: logging.Formatter = FORMATTER,
            level: int = logging.INFO,
            **kwargs
    ) -> TimedRotatingFileHandler:
        file_log_handler = TimedRotatingFileHandler(
            filename=kwargs.pop('filename', path), **kwargs
        )
        file_log_handler.setFormatter(formatter)
        file_log_handler.setLevel(level)
        return file_log_handler

    def configure_tg_logger(
            self,
            bot_token: str,
            recipient_id: int
    ) -> ClientLogger:
        from tg_logger.settings import logger_settings
        try:
            if bot_token is None:
                bot_token = logger_settings.bot_token
            if recipient_id is None:
                recipient_id = logger_settings.recipient_id
        except AttributeError:
            raise ValueError(
                'You must configure the logger using "configure_logger" or '
                'provide "bot_token" and "recipient_id" during initialization.'
            ) from AttributeError
        else:
            settings = SyncTgLoggerSettings(bot_token, recipient_id)
            return ClientLogger(settings, self.logger)

    def get_logger(
            self,
            name: str = None,
            level: int = None,
            console_log_handler: logging.StreamHandler = None,
            file_log_handler: TimedRotatingFileHandler = None
    ) -> 'BaseLogger':
        logger = logging.getLogger(name)
        if console_log_handler is not None:
            logger.addHandler(console_log_handler)
        if file_log_handler is not None:
            logger.addHandler(file_log_handler)
        if level is not None:
            logger.setLevel(level)
        self.logger = logger
        return self

    def error(self, message) -> None:
        self.tg_logger.send_error(message)
        self.logger.error(message)

    def info(self, message) -> None:
        self.logger.info(message)

    def debug(self, message) -> None:
        self.logger.debug(message)

    def warning(self, message) -> None:
        self.logger.warning(message)

    def log_message(
            self,
            name: str,
            log_level: str,
            message: str = shrug,
    ) -> None:
        try:
            log_method = super().__getattribute__(log_level.lower())
        except AttributeError:
            self.error(f'{name}: Invalid {log_level=}.')
            log_method = self.error
        log_method(f'{name}: {message}')

    def model_log(self, log_level, model, method, user=None, add_info=None):
        msg = (f'{model.__class__.__name__} with {model_dict_or_none(model)} '
               f'was {method=}.')
        if user:
            msg = (
                f'{user} {method} {model.__class__.__name__}'
                f' with {model_dict_or_none(model)}.'
            )
        if add_info:
            msg += add_info
        self.log_message('model_log', log_level, msg)
