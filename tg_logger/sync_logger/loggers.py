import logging
from datetime import datetime, timezone

from tg_logger.settings import SyncTgLoggerSettings
from tg_logger.sync_logger.logger_warner import ClientLogger


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
            self.tg_logger = ClientLogger(settings)

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
            error: str = None,
            *args,
            **kwargs
    ) -> None:
        if error is not None:
            message += f'\n{error} {args} {kwargs}'
        try:
            log_method = super().__getattribute__(log_level.lower())
        except AttributeError:
            self.error(f'{name}: Invalid {log_level=}.')
            log_method = self.error
        log_method(f'{name}: {message}')

    def model_log(self, log_level, model, method, user=None, add_info=None):
        msg = f'{model.__class__.__name__} with id {model.pk} was {method}d.'
        if user:
            msg = (
                f'{user} {method} {model.__class__.__name__}'
                f' with id {model.pk}.'
            )
        if add_info:
            msg += add_info
        self.log_message('model_log', log_level, msg)

    def multiple_entities_log(self, log_level, model, method, add_info=None):
        msg = f'{model.__class__.__name__} was {method}d.'
        if add_info:
            msg += add_info
        self.log_message('multiple_entities_log', log_level, msg)

    def get_or_create_bot_log(self, log_level, bot, create):
        if create:
            msg = f'TelegramClient with tg_id={bot.tgbot_id} created.'
        else:
            msg = (
                f'Data of bot with tg_id={bot.tgbot_id} '
                'was retrieved and saved.'
            )
        self.log_message('get_or_create_bot_log', log_level, msg)


class ManagerLogger(BaseLogger):
    def __init__(self, tgbot_model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tgbot_model = tgbot_model

    def get_update_tgbot(self, log_level, tgbot):
        if isinstance(tgbot, self.tgbot_model):
            if tgbot.is_activated:
                msg = f'Updated bot tg_id={tgbot.tgbot_id}.'
            else:
                msg = f'Deactivated bot tg_id={tgbot.tgbot_id}.'
            self.log_message('get_update_tgbot', log_level, msg)

    def send_bot_msg(self, log_level, bot_id, user_id):
        msg = f'Bot tg_id={bot_id} sent payment message to user {user_id}.'
        self.log_message('send_bot_msg', log_level, msg)

    def key_duplicate_error(self, log_level, msg_err):
        msg = (
            f'{msg_err}: the session was used under two different IP '
            f'addresses at the same time.'
        )
        self.log_message('key_duplicate_error', log_level, msg)

    def key_unregistered_error(self, log_level, msg_err):
        msg = f'{msg_err}: authorization key not registered.'
        self.log_message('key_unregistered_error', log_level, msg)

    def log_run_client(self, log_level):
        msg = 'Connected client to proxy.'
        self.log_message('log_run_client', log_level, msg)

    def change_proxy(self, log_level):
        msg = 'Changed proxy for client.'
        self.log_message('change_proxy', log_level, msg)

    def send_payment_message(self, log_level, bot_id):
        msg = f'Set to cache for payment message bot id={bot_id}.'
        self.log_message('send_payment_message', log_level, msg)

    def start_chatting(self, log_level):
        msg = 'Started new event loop.'
        self.log_message('start_chatting', log_level, msg)

    def create_telegram_client(self, log_level, tgbot):
        msg = f'Started listener for tg_bot id={tgbot.tgbot_id}.'
        self.log_message('create_telegram_client', log_level, msg)

    def wait_messages(self, log_level, tgbot_id):
        msg = f'Listener wait commands for bot id={tgbot_id}.'
        self.log_message('wait_messages', log_level, msg)

    def start_tasks_listener(self, log_level):
        msg = 'Started asyncio tasks for Listener.'
        self.log_message('start_tasks_listener', log_level, msg)


class ResponsibleLogger(BaseLogger):
    def __init__(self, number, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.number = number
        self.thread_str = f'. Thread={self.number}'

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            return super().__getattr__(name)
        return lambda *args, **kwargs: self.log_message(
            name, *args, **kwargs, thread_str=self.thread_str
        )

    def create_telegram_client(self, log_level, tgbot):
        msg = f'Started client for bot id={tgbot.tgbot_id}' + self.thread_str
        self.log_message('get_or_create_bot_log', log_level, msg)

    def answer_chats(self, log_level, tgbot, chat_id):
        msg = (
            f'Bot id={tgbot.tgbot_id} started answering for chat={chat_id}'
            + self.thread_str
        )
        self.log_message('answer_chats', log_level, msg)

    def get_input_message_data(self, log_level):
        msg = 'Got the data for input message' + self.thread_str
        self.log_message('get_input_message_data', log_level, msg)

    def end_user_balance(self, log_level, user):
        msg = f'User id={user.tg_id} has zero balance' + self.thread_str
        self.log_message('get_or_create_bot_log', log_level, msg)

    def cancel_chat_task(self, log_level, tgbot_id, chat_id):
        msg = f'Cancel task: chatting_{tgbot_id}_{chat_id}' + self.thread_str
        self.log_message('cancel_chat_task', log_level, msg)

    def start_tasks(self, log_level):
        msg = 'Started asyncio tasks' + self.thread_str
        self.log_message('start_tasks', log_level, msg)
