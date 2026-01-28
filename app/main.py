from telegram.ext import Application as PTBApplication, ApplicationBuilder
from telegram.ext import CommandHandler, CallbackQueryHandler
from app.core.users.repositories import UserRepository
from app.core.users.services import UserService
from app.core.orders.repositories import ProductRepository, OrderRepository
from app.core.orders.servises import ProductService, OrderService
from settings.config import AppSettings
import logging
from app.handlers import HANDLERS
from app.infra.postgres.db import Database
from app.infra.base import Base
from app.core.users.constants import RolesEnum
from app.core.users.roles import RoleManager
from app.jobs.sync_roles import sync_roles


class Application(PTBApplication):
    def __init__(self, app_settings: AppSettings, **kwargs):
        super().__init__(**kwargs)
        self._settings = app_settings
        self._roles = RoleManager()
        self.database = Database(app_settings.POSTGRES_DSN, declarative_base=Base)

        user_repository = UserRepository(database=self.database)
        self.user_service = UserService(repository=user_repository)

        product_repository = ProductRepository(database=self.database)
        self.product_service = ProductService(repository=product_repository)

        order_repository = OrderRepository(database=self.database)
        self.order_service = OrderService(repository=order_repository)

    @staticmethod
    async def application_startup(application: "Application") -> None:
        await application.database.create_tables()
        await application.setup_roles()
        application.register_handlers()
        application.setup_jobs()

    @staticmethod
    async def application_shutdown(application: "Application") -> None:
        await application.database.shutdown()

    def run(self) -> None:
        self.run_polling()

    def register_handlers(self) -> None:
        for h in HANDLERS:
            self.add_handler(h.handler)

    async def setup_roles(self) -> None:
        for role in RolesEnum:
            user_ids = await self.user_service.get_user_ids_for_role(role)
            for user_id in user_ids:
                self._roles.add_member(role, user_id)

    def setup_jobs(self) -> None:
        if self.job_queue is None:
            raise Exception("job queue missing")
        roles_sync = self.job_queue.run_repeating(sync_roles, interval=60)


def configure_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.DEBUG
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)


def create_app(app_settings: AppSettings) -> Application:
    application = (
        ApplicationBuilder()
        .application_class(Application, kwargs={"app_settings": app_settings})
        .post_init(Application.application_startup)  # type: ignore[arg-type]
        .post_shutdown(Application.application_shutdown)  # type: ignore[arg-type]
        .token(app_settings.TELEGRAM_API_KEY.get_secret_value())
        .build()
    )
    return application  # type: ignore[return-value]


if __name__ == '__main__':
    configure_logging()
    settings = AppSettings()
    app = create_app(settings)
    app.run()
