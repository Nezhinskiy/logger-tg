import asyncio

import aiohttp

from tg_logger.settings import TgLoggerSettings


class ClientLogger:
    """
    A client logger for sending error messages to a specified Telegram chat.

    Attributes:
    - MAX_MSG_LENGTH (int): Maximum length of a message that can be sent in a
        single Telegram message.
    - bot_token (str): Telegram bot token used for authentication.
    - recipient_id (int, int): Telegram chat ID to which messages will be sent.
    - logger (BaseLogger): Python logger for logging errors.
    - api_url (str): URL for the Telegram sendMessage API endpoint.
    """
    MAX_MSG_LENGTH: int = 4096

    def __init__(self, settings: TgLoggerSettings, logger: 'BaseLogger'):
        """
        Initializes the ClientLogger with settings and a logger.

        Parameters:
        - settings (SyncTgLoggerSettings): Configuration settings containing
            the bot token and recipient ID.
        - logger (logging.Logger): Logger for logging errors.
        """
        self.bot_token = settings.bot_token
        self.recipient_id = settings.recipient_id
        self.logger = logger
        self.api_url = (
            f'https://api.telegram.org/bot{self.bot_token}/sendMessage')

    def _format_message(self, message: str) -> list[str]:
        """
        Splits a message into parts if it exceeds the maximum message length.

        Parameters:
        - message (str): The message to be split.

        Returns:
        - list[str]: A list of message parts.
        """
        return [
            message[i:i + self.MAX_MSG_LENGTH] for i in range(
                0, len(message), self.MAX_MSG_LENGTH
            )
        ]

    async def _send_error_async(self, message: str) -> None:
        """
        Asynchronously sends an error message to the specified Telegram chat.

        Parameters:
        - message (str): The error message to be sent.
        """
        data = {'chat_id': self.recipient_id}
        for part in self._format_message(message):
            data['text'] = part
            print(data)
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(self.api_url,
                                            data=data) as response:
                        response.raise_for_status()
                except aiohttp.ClientError as e:
                    self.logger.error(f'Client error sending message: {e}')
                except aiohttp.HttpProcessingError as e:
                    self.logger.error(f'HTTP error sending message: {e}')
                except Exception as e:
                    self.logger.error(f'Unexpected error sending message: {e}')

    def send_error(self, message: str) -> None:
        """
        Sends an error message to the specified Telegram chat.
        It uses an asynchronous task if the event loop is already running,
        otherwise it runs a new event loop.

        Parameters:
        - message (str): The error message to be sent.
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._send_error_async(message))
            loop.close()
        else:
            if loop.is_running():
                loop.create_task(self._send_error_async(message))
            else:
                asyncio.run(self._send_error_async(message))
