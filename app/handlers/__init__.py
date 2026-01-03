from dataclasses import dataclass

from telegram.ext import BaseHandler, CommandHandler
from app.core.users.constants import RolesEnum
from app.handlers.commands import start, waiter_start


@dataclass
class Handler:
    handler: BaseHandler
    role: RolesEnum | None = None


HANDLERS: tuple[Handler, ...] = (Handler(CommandHandler("start", waiter_start),
                                         role=RolesEnum.waiter),
                                 Handler(CommandHandler("start", start)))
