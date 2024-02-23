import asyncio

import aiohttp

from tg_logger.settings import SyncTgLoggerSettings


class ClientLogger:
    MAX_MSG_LENGTH: int = 4096

    def __init__(self, settings: SyncTgLoggerSettings, logger):
        self.bot_token = settings.bot_token
        self.recipient_id = settings.recipient_id
        self.logger = logger
        self.api_url = (
            f'https://api.telegram.org/bot{self.bot_token}/sendMessage')

    def _format_message(self, message: str) -> list[str]:
        return [message[i:i + self.MAX_MSG_LENGTH] for i in
                range(0, len(message), self.MAX_MSG_LENGTH)]

    async def _send_error_async(self, message):
        data = {'chat_id': self.recipient_id}
        for part in self._format_message(message):
            data['text'] = part
            print(data)
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(self.api_url,
                                            data=data) as response:
                        response.raise_for_status()
                except Exception as e:
                    self.logger.error(f'Error sending message: {e}')

    def send_error(self, message):
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
