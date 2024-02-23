import asyncio

import aiohttp

ADMIN_SENDER_ID=333371434
ADMIN_BOT_TOKEN='6471265983:AAG5omqLltOaznQPaHVee-Imsm2HQg0zP5Q'


class ClientLogger:
    MAX_MSG_LENGTH: int = 1

    def __init__(self):
        self.bot_token = ADMIN_BOT_TOKEN
        self.recipient_id = ADMIN_SENDER_ID
        self.api_url = (
            f'https://api.telegram.org/bot{self.bot_token}/sendMessage')

    def _format_message(self, message: str) -> list[str]:
        return [message[i:i + self.MAX_MSG_LENGTH] for i in range(0, len(message), self.MAX_MSG_LENGTH)]

    async def _send_error_async(self, message):
        data = {'chat_id': self.recipient_id}
        for part in self._format_message(message):
            data['text'] = part
            print(data)
            async with aiohttp.ClientSession() as session:
                try:
                    print('try send message')
                    async with session.post(self.api_url,
                                            data=data) as response:
                        response.raise_for_status()
                        print('send message')
                except Exception as e:
                    print(f'Error sending message: {e}')

    def send_error(self, message):
        if asyncio.get_event_loop().is_running():
            loop = asyncio.get_event_loop()
            loop.create_task(self._send_error_async(message))
        else:
            asyncio.run(self._send_error_async(message))




if __name__ == '__main__':
    logger = ClientLogger()
    async def main():
        await asyncio.sleep(1)
        logger.send_error('123456789')
        logger.send_error('абвгдежз')
        await asyncio.sleep(100)

    asyncio.run(main())

    # logger.send_error('123456789')
