# logger-tg
[![PyPI version](https://badge.fury.io/py/logger-tg.svg)](https://badge.fury.io/py/logger-tg)
[![Downloads](https://pepy.tech/badge/logger-tg)](https://pepy.tech/project/logger-tg)
[![Downloads](https://pepy.tech/badge/logger-tg/month)](https://pepy.tech/project/logger-tg)
[![Downloads](https://pepy.tech/badge/logger-tg/week)](https://pepy.tech/project/logger-tg)

`logger-tg` is a Python package that seamlessly integrates logging with Telegram, allowing developers to receive log messages directly in a Telegram chat. This tool is especially useful for monitoring applications in real-time, receiving immediate error notifications, and keeping track of important information without the need to constantly check log files.

## Features
- **Easy Integration:** Set up with just a few lines of code.
- **Real-Time Notifications:** Receive log messages instantly on your Telegram.
- **Flexible Logging Levels:** Supports all standard logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- **Customizable:** Easily configure the logger to suit your needs, including custom message formatting.
- **Asynchronous Support:** Utilizes asynchronous communication with Telegram for efficient message delivery.

## Installation
`logger-tg` can be installed using pip. Ensure you have Python 3.6 or newer.

```bash
pip install logger-tg
```

## Quick Start
To get started with `logger-tg`, you need to configure it with your Telegram bot token and recipient chat ID. Here's a quick guide:

1. **Create a Telegram Bot:** If you haven't already, create a bot by chatting with [BotFather](https://t.me/botfather) on Telegram and save the bot token.
2. **Find Your Chat ID:** You can use the `@userinfobot` on Telegram to find your chat ID.

## Basic Setup
```python
from logger_tg import configure_logger, BaseLogger

# Configure global settings
configure_logger(bot_token='your_bot_token', recipient_id=your_chat_id)

# Initialize the logger
logger = BaseLogger(name='MyAppLogger')

# Start logging
logger.info("This is a test message!")
```

## Configuration
Custom Log Handlers
`logger-tg` allows for custom log handlers, enabling you to log to files, console, and Telegram simultaneously.

```python
from logging.handlers import TimedRotatingFileHandler
from logger_tg import BaseLogger, TgLoggerSettings

# File handler for logging to a file
file_handler = TimedRotatingFileHandler('app.log', when="midnight", interval=1)
file_handler.suffix = "%Y-%m-%d"

# Console handler for logging to stderr
console_handler = logging.StreamHandler()

# Initialize the logger with custom handlers
logger = BaseLogger().get_logger(
    name="MyAppLogger",
    console_log_handler=console_handler,
    file_log_handler=file_handler
)

logger.info("Logging to console and file.")
```

## Advanced Usage
`logger-tg` also supports asynchronous logging to Telegram, which can be particularly useful for applications with high logging throughput or when you wish to avoid blocking the main thread.

Asynchronous Error Logging
To log errors asynchronously to Telegram:

```python
import asyncio
from logger_tg import BaseLogger

logger = BaseLogger(name='AsyncAppLogger')

async def log_error():
    logger.error("Asynchronous error logging.")

# Running the asynchronous log function
asyncio.run(log_error())
```
This approach ensures that your application remains responsive, even when sending multiple log messages to Telegram.

## Contributing
Contributions are welcome! If you'd like to contribute, please fork the repository and use a main branch. Pull requests are warmly welcome.

## License
`logger-tg` is available under the MIT license. See the [LICENSE](LICENSE) file for more info.

## Acknowledgments
Thanks to the authors of `aiohttp`.
