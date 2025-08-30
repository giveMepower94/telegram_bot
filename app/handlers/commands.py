from telegram import Update
from telegram.ext import ContextTypes


# Создаем обработчик команды start с помощью асинронной функции
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Добро пожаловать"
        )
