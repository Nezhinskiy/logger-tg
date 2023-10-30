from dataclasses import dataclass

logger_settings = None


@dataclass
class SyncTgLoggerSettings:
    bot_token: str
    recipient_id: int


def configure_logger(bot_token: str, recipient_id: int):
    global logger_settings
    logger_settings = SyncTgLoggerSettings(bot_token, recipient_id)
