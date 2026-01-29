from app.core.orders.constants import OrderStatusEnum
from app.core.orders.models import Product, Order
from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def build_order_buttons(order_id: int, items: list[Product]) -> InlineKeyboardMarkup:
    keyboard = []
    for item in items:
        keyboard.append([InlineKeyboardButton(text=f"{item.name}",
                                              callback_data=("add_item", order_id, item.id))])
    keyboard.append([InlineKeyboardButton(text="Завершить заказ",
                                          callback_data=("finish_order", order_id))])
    return InlineKeyboardMarkup(keyboard)


def format_order_contents(order: Order) -> str:
    if order.products:
        msg_text = "<b>В вашей корзине:</b>\n"
        for ordered_products in order.products:
            msg_text += f"<b>{ordered_products.product.name}:</b> {ordered_products.amount}\n"
        if order.status == OrderStatusEnum.unlisted:
            msg_text += "Выберите что-то еще или оформите новый заказ"
    else:
        msg_text += "<b>В вашей корзине пока пусто</b>\nВыберите, что хотите заказать"
    return msg_text


def format_order_contents_for_waiters(order: Order) -> str:
    msg_text = ""
    for ordered_products in order.products:
        msg_text += f"- <b>{ordered_products.product.name}:</b> {ordered_products.amount}\n"
    return msg_text
