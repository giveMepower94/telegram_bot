from telegram.ext import ContextTypes


async def sync_roles(context: ContextTypes.DEFAULT_TYPE) -> None:
    app = context.application  # type: ignore[attr-defined]
    await app.setup_roles()
