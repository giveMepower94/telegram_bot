from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.main import Application
from app.core.orders.constants import OrderStatusEnum
from app.core.orders.exceptions import ActiveOrderExists
from app.core.orders.servises import ProductService, OrderService
from app.core.users.services import UserService


# Создаем обработчик команды start с помощью асинронной функции
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if update.effective_chat and update.effective_user:
        app: Application = context.application

        await app.user_service.register_visitor(update.effective_user.id)
        keyboard = [
            [InlineKeyboardButton("Сделать заказ", callback_data="order_create")],
        ]
        markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Добро пожаловать",
            reply_markup=markup
        )


async def waiter_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat and update.effective_user:
        app: Application = context.application

        await app.user_service.register_visitor(update.effective_user.id)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Добро пожаловать на работу")
