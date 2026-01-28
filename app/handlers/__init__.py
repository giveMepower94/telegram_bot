from dataclasses import dataclass

from telegram.ext import BaseHandler, CommandHandler, CallbackQueryHandler
from app.core.users.constants import RolesEnum
from app.handlers.commands import (start,
                                   create_order, add_item,
                                   finish_order,
                                   waiter_finish_order)


@dataclass
class Handler:
    handler: BaseHandler
    role: RolesEnum | None = None


HANDLERS: tuple[Handler, ...] = (
    # /start — для всех
    Handler(
        handler=CommandHandler("start", start),
    ),

    # Создание заказа
    Handler(
        handler=CallbackQueryHandler(create_order, pattern=r"^order_create$"),
    ),

    # Добавление продукта
    Handler(
        handler=CallbackQueryHandler(add_item, pattern=r"^add_item_\d+_\d+$"),
    ),

    # Завершение заказа пользователем
    Handler(
        handler=CallbackQueryHandler(finish_order, pattern=r"^finish_order_\d+$"),
    ),

    # Завершение заказа официантом
    Handler(
        handler=CallbackQueryHandler(
            waiter_finish_order,
            pattern=r"^waiter_finish_order_\d+$",
        ),
        role=RolesEnum.waiter,
    ),
)