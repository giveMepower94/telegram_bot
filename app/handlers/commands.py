from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.main import Application
from telegram.constants import ParseMode
from app.infra.postgres
from app.core.orders.servises import OrderService
from app.core.orders.constants import OrderStatusEnum
from app.core.users.constants import RolesEnum
from app.core.orders.exceptions import ActiveOrderExists
from app.core.orders.servises import ProductService, OrderService
from app.core.users.services import UserService
from app.handlers.helpers import build_order_buttons, format_order_contents, format_order_contents_for_waiters


# Создаем обработчик команды start с помощью асинронной функции
async def create_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    try:
        # Пытаемся создать новый заказ
        order_id = await OrderService.create_order(user_id)
        # Если создалось — подгружаем заказ с продуктами сразу через сессию
        async with async_session() as session:
            from app.core.orders.models import Order
            new_order = await session.get(Order, order_id)
            text = f"✅ Ваш заказ создан!\n\n{format_order_contents(new_order)}"

    except ActiveOrderExists:
        # Если заказ уже есть — подгружаем активный заказ через сессию
        async with async_session() as session:
            from app.core.orders.models import Order
            active_order = await session.execute(
                Order.__table__.select().where(Order.user_id == user_id, Order.status == "active")
            )
            active_order = active_order.scalars().first()
            text = f"⚠ У вас уже есть активный заказ:\n\n{format_order_contents(active_order)}"

    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🍦 Сделать заказ", callback_data="order_create")]
        ]
    )

    await update.effective_chat.send_message(
        text=text,
        reply_markup=keyboard
    )


# Создаем обработтчик кнопки сделать заказ
async def create_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not update.effective_user:
        return

    await query.answer()

    app: "Application" = context.application  # type: ignore[assignment]
    order_service: OrderService = app.order_service
    product_service: ProductService = app.product_service

    user_id = update.effective_user.id

    # Получаем список товаров
    items = await product_service.list_products()
    if not items:
        await context.bot.send_message(chat_id=user_id, text="❌ Сейчас нет доступных товаров")
        return

    try:
        # Создаём новый заказ
        order_id = await order_service.create_order(user_id)
        await context.bot.send_message(
            chat_id=user_id,
            text="🍽 Добавьте блюдо или напиток в заказ",
            reply_markup=build_order_buttons(order_id, items)
        )
    except ActiveOrderExists:
        # Если уже есть активный заказ — продолжаем его
        active_order = await order_service.get_active_order_for_user(user_id)
        await context.bot.send_message(
            chat_id=user_id,
            text=format_order_contents(active_order),
            reply_markup=build_order_buttons(active_order.id, items),
            parse_mode=ParseMode.HTML
        )


async def add_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    callback_data = query.data

    app: "Application" = context.application  # type: ignore[assignment]
    order_service: OrderService = app.order_service
    product_service: ProductService = app.product_service

    order_id, item_id = int(callback_data[1]), int(callback_data[2])
    products = await product_service.list_products()

    await order_service.add_product_to_order(order_id, item_id)
    order = await order_service.get_order_by_id(order_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=format_order_contents(order),
        reply_markup=build_order_buttons(order_id, products),
        parse_mode=ParseMode.HTML
    )


async def finish_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    callback_data = query.data

    app: "Application" = context.application  # type: ignore[assignment]
    order_service: OrderService = app.order_service
    user_service: UserService = app.user_service

    order_id = int(callback_data[1])
    await order_service.send_order_to_waiters(order_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Заказ был передан нашим оффициантам, пожалуйста, ожидайте!"
    )

    waiter_users_ids = await user_service.get_waiter_user_ids()
    order = await order_service.get_order_by_id(order_id)

    for waiter_user_id in waiter_users_ids:
        await context.bot.send_message(
            chat_id=waiter_user_id,
            text=f"Создан новый заказ: {order_id}\n\n"
                 f"{format_order_contents_for_waiters(order)}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text="Заказ доставлен", callback_data=("waiters finish order", order_id))]])
        )


async def waiter_finish_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    app: "Application" = context.application  # type: ignore[assignment]
    order_service: OrderService = app.order_service

    query = update.callback_query
    if not query or not update.effective_user:
        return

    # 🔐 ПРОВЕРКА РОЛИ
    user_id = update.effective_user.id
    if not app._roles.has_member(RolesEnum.waiter, user_id):
        await query.answer("⛔ У вас нет прав официанта", show_alert=True)
        return

    await query.answer()

    callback_data = query.data.split("_")
    order_id = int(callback_data[-1])

    await order_service.mark_order_done(order_id)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Заказ успешно завершен!"
    )