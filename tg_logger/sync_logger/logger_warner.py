import telebot

from tg_logger.settings import SyncTgLoggerSettings


class ClientLogger:
    def __init__(self, settings: SyncTgLoggerSettings):
        self.bot = telebot.TeleBot(settings.bot_token)
        self.recipient_id = settings.recipient_id

    def send_error(self, message):
        try:
            self.bot.send_message(self.recipient_id, message)
        except Exception:
            return
