from telegram.ext import BaseHandler, CommandHandler


from .commands import start


HANDLERS: tuple[BaseHandler] = (CommandHandler("start", start),)
