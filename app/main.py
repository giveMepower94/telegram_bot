from telegram.ext import Application as PTBApplication, ApplicationBuilder
from settings.config import AppSettings
import logging


class Application(PTBApplication):
    def __init__(self, app_settings: AppSettings, **kwargs):
        super().__init__(**kwargs)
        self._settings = app_settings

    def run(self) -> None:
        self.run_polling()


def configure_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)


def create_app(app_settings: AppSettings) -> Application:
    application = ApplicationBuilder().application_class(
        Application,
        kwargs={"app_settings": app_settings}
    ).token(
        app_settings.TELEGRAM_API_KEY.get_secret_value()
    ).build()

    return application  # type: ignore[return-value]


if __name__ == '__main__':
    configure_logging()
    settings = AppSettings()
    app = create_app(settings)
    app.run()
