import logging
from datetime import datetime, timezone

from tg_logger.logger.logger_warner import ClientLogger
from tg_logger.settings import SyncTgLoggerSettings
from tg_logger.utils import model_dict_or_none


class BaseLogger:
    shrug: str = ''.join(map(chr, (175, 92, 95, 40, 12484, 41, 95, 47, 175)))

    def __init__(
            self,
            bot_token: str = None,
            recipient_id: int = None,
    ) -> None:
        from tg_logger.settings import logger_settings
        self.logger = logging.getLogger('app')
        self.start_time = datetime.now(timezone.utc)
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
            self.tg_logger = ClientLogger(settings, self.logger)

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            return super().__getattr__(name)
        return lambda *args, **kwargs: self.log_message(name, *args, **kwargs)

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
