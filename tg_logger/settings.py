from dataclasses import dataclass

# Global variable to hold logger settings. Initially set to None.
logger_settings = None


@dataclass
class TgLoggerSettings:
    """
    Data class for storing Telegram logger settings.

    Attributes:
    - bot_token (str): The Telegram bot token used for authentication.
    - recipient_id (int): The Telegram recipient ID where messages will be
        sent.
    """
    bot_token: str
    recipient_id: int


def configure_logger(bot_token: str, recipient_id: int) -> None:
    """
    Configures global logger settings with the provided Telegram bot token and
        recipient ID.
    This function initializes the global `logger_settings` variable with
        an instance of `TgLoggerSettings`.

    Parameters:
    - bot_token (str): The Telegram bot token.
    - recipient_id (int): The Telegram recipient ID.

    This configuration allows the `BaseLogger` to use these settings by default, eliminating the need to
    pass them explicitly during its initialization if they are already configured here.
    """
    global logger_settings
    logger_settings = TgLoggerSettings(bot_token, recipient_id)
