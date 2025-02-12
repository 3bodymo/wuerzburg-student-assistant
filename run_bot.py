import asyncio
from app.bot.telegram_bot import create_bot_application
import logging
from app.utils.logger import setup_loggers
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

conversation_logger = setup_loggers()

def main():
    application = None
    try:
        application = create_bot_application()
        print("Starting bot...")
        application.run_polling(poll_interval=3)
    except Exception as e:
        print(f"Error starting bot: {e}")
        if application:
            application.shutdown()
        raise e

if __name__ == '__main__':
    asyncio.run(main())
