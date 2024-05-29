import logging
import sys
from datetime import datetime, timezone
from logging.handlers import TimedRotatingFileHandler

from tg_logger.logger.logger_warner import ClientLogger
from tg_logger.settings import TgLoggerSettings
from tg_logger.utils import model_dict_or_none


class BaseLogger:
    """
    A base logger class that integrates with Telegram for error logging.
    And supports both console and file logging.

    Attributes:
    - shrug (str): A shrug emoji represented in characters.
    - FORMATTER (logging.Formatter): Default logging formatter.
    - logger (logging.Logger): The logger instance.
    - start_time (datetime): The time the logger was initialized.
    - tg_logger (ClientLogger): The Telegram logger instance.
    """
    shrug: str = ''.join(map(chr, (175, 92, 95, 40, 12484, 41, 95, 47, 175)))
    FORMATTER: logging.Formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s'
    )

    def __init__(
            self,
            name: str = 'app',
            bot_token: str = None,
            recipient_id: str | int = None,
            logger: logging.Logger = None
    ) -> None:
        """
        Initializes the BaseLogger with optional Telegram logging.

        Parameters:
        - name (str, optional): The name of the logger.
        - bot_token (str, optional): The Telegram bot token.
        - recipient_id (str, int, optional): The Telegram recipient ID.
        """
        if logger is None:
            self.logger = logging.getLogger(name)
        else:
            self.logger = logger
        self.start_time = datetime.now(timezone.utc)
        self.tg_logger = self.configure_tg_logger(bot_token, recipient_id)

    def __getattr__(self, name: str) -> callable:
        """
        Allows dynamic access to logging methods based on attribute name.

        Parameters:
        - name (str): The logging method name.

        Returns:
        - callable: A function that logs a message with the specified level.
        """
        if name.startswith('__') and name.endswith('__'):
            return super().__getattr__(name)
        return lambda *args, **kwargs: self.log_message(name, *args, **kwargs)

    @staticmethod
    def get_console_log_handler(
            formatter: logging.Formatter = FORMATTER,
            level: int = logging.DEBUG
    ) -> logging.StreamHandler:
        """
        Creates a console log handler.

        Parameters:
        - formatter (logging.Formatter, optional): The formatter for the log
            handler.
        - level (int, optional): The log level.

        Returns:
        - logging.StreamHandler: The configured console log handler.
        """
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
        """
        Creates a file log handler.

        Parameters:
        - path (str): The path to the log file.
        - formatter (logging.Formatter, optional): The formatter for
            the log handler.
        - level (int, optional): The log level.
        - **kwargs: Additional keyword arguments for TimedRotatingFileHandler.

        Returns:
        - TimedRotatingFileHandler: The configured file log handler.
        """
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
        """
        Configures a Telegram logger.

        Parameters:
        - bot_token (str): The Telegram bot token.
        - recipient_id (int): The Telegram recipient ID.

        Returns:
        - ClientLogger: The configured Telegram logger.

        Raises:
        - ValueError: If bot_token or recipient_id is not provided and cannot
            be found in settings.
        """
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
            settings = TgLoggerSettings(bot_token, recipient_id)
            return ClientLogger(settings, self.logger)

    def log(self, level: int, msg=shrug, *args, **kwargs):
        """
        Log 'msg % args' with the integer severity 'level'.

        To pass exception information, use the keyword argument exc_info with
        a true value, e.g.

        logger.log(level, "We have a %s", "mysterious problem", exc_info=1)
        """
        if not isinstance(level, int):
            raise TypeError("level must be an integer")

        if self.logger.isEnabledFor(level):
            level_name = logging.getLevelName(level).lower()
            getattr(self, level_name)(msg, *args, **kwargs)

    def critical(self, message: str) -> None:
        """
        Logs a critical message and sends it to the configured Telegram chat.

        Parameters:
        - message (str): The critical message.
        """
        self.tg_logger.send_error(message)
        self.logger.critical(message)

    def error(self, message: str) -> None:
        """
        Logs an error message and sends it to the configured Telegram chat.

        Parameters:
        - message (str): The error message.
        """
        self.tg_logger.send_error(message)
        self.logger.error(message)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def log_message(
            self,
            name: str,
            log_level: str,
            message: str = shrug,
            **kwargs
    ) -> None:
        """
        Logs a message with a specified log level.

        Parameters:
        - name (str): The name associated with the log message.
        - log_level (str): The log level ('error', 'info', 'debug', 'warning').
        - message (str, optional): The log message. Defaults to a shrug emoji.
        - **kwargs: Additional keyword arguments to include in the log message.
        """
        try:
            log_method = super().__getattribute__(log_level.lower())
        except AttributeError:
            self.error(f'{name}: Invalid {log_level=}.')
            log_method = self.error
        log_msg = f'{name}: {message}'
        kwargs_str = ' '.join(
            f'{k}={v}' for k, v in kwargs.items()
        ) if kwargs else ''
        log_msg += kwargs_str
        log_method(log_msg)

    def model_log(
            self,
            log_level: str,
            model: object,
            method: str,
            user: str = None,
            add_info: str = None
    ) -> None:
        """
        Logs a message related to a model operation.

        Parameters:
        - log_level (str): The log level as a string.
        - model (object): The model involved in the operation.
        - method (str): The method or operation performed on the model.
        - user (str, optional): The user performing the operation.
            Defaults to None.
        - add_info (str, optional): Additional information to include in
            the log message. Defaults to None.
        """
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
