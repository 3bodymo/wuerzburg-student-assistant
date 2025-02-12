import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.error import NetworkError, TimedOut, RetryAfter
from app.services.rag_service import RAGService
from app.core.config import get_settings
from app.utils.logger import setup_loggers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from app.bot.handlers.menus import MenuHandlers
from app.bot.handlers.lists import ListHandlers
from app.bot.handlers.info import GeneralInfoHandlers
from app.bot.handlers.case_specific import CaseSpecificHandlers
from app.bot.handlers.message import MessageHandlers
from app.bot.constants import *

# Enable logging
logger = logging.getLogger(__name__)
conversation_logger = setup_loggers()

# Initialize services
settings = get_settings()
rag_service = RAGService()
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
message_handlers = MessageHandlers()

@asynccontextmanager
async def get_db():
    """Creates a database session context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def check_access(update: Update) -> bool:
    """
    Checks if a user has access to the bot based on development mode settings.

    Args:
        update (Update): The Telegram update object containing user information.

    Returns:
        bool: True if user has access, False otherwise.
    """
    settings = get_settings()
    if settings.DEVELOPMENT_MODE:
        return update.message.from_user.id == settings.DEVELOPER_USER_ID
    return True

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

async def safe_send_message(update: Update, text: str, retries: int = MAX_RETRIES) -> None:
    """
    Safely sends a message with retry mechanism for handling network errors.

    Args:
        update (Update): The Telegram update object.
        text (str): The message text to send.
        retries (int, optional): Number of retry attempts. Defaults to MAX_RETRIES.

    Returns:
        None: This function doesn't return anything.
    """
    for attempt in range(retries):
        try:
            await update.message.reply_text(text)
            return
        except (NetworkError, TimedOut) as e:
            if attempt == retries - 1:  # Last attempt
                logger.error(f"Failed to send message after {retries} attempts: {e}")
                await update.message.reply_text(
                    "⚠️ Network issue detected. Please try again in a few moments."
                )
                return
            await asyncio.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
            continue
        except Exception as e:
            logger.error(f"Unexpected error while sending message: {e}")
            await update.message.reply_text(
                "⚠️ An unexpected error occurred. Please try again."
            )
            return

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles the /start command and sends a welcome message with available commands.

    Args:
        update (Update): The Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): The context object for the handler.

    Returns:
        None: This function doesn't return anything.
    """
    if not await check_access(update):
        await safe_send_message(update, "Sorry, this bot is currently in development mode.")
        return
    await safe_send_message(update, WELCOME_MESSAGE)

def create_bot_application() -> Application:
    """
    Creates and configures the Telegram bot application with all handlers.

    Returns:
        Application: Configured Telegram bot application instance.
            - Includes all command handlers
            - Includes error handler
            - Includes message handler for non-command messages
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in environment variables")

    # Create application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
    
    # Add error handler
    application.add_error_handler(message_handlers.error_handler)

    # Add handlers
    menu_handlers = MenuHandlers()
    list_handlers = ListHandlers()
    general_info_handlers = GeneralInfoHandlers()
    case_specific_handlers = CaseSpecificHandlers()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("apartment", menu_handlers.handle_apartment_menu))
    application.add_handler(CommandHandler("places", menu_handlers.handle_places_menu))
    application.add_handler(CommandHandler("insurance", menu_handlers.handle_insurance_menu))
    application.add_handler(CommandHandler("immigration", menu_handlers.handle_immigration_menu))
    application.add_handler(CommandHandler("healthcare", menu_handlers.handle_healthcare_menu))
    application.add_handler(CommandHandler("sports", menu_handlers.handle_sports_menu))
    application.add_handler(CommandHandler("education", menu_handlers.handle_education_menu))
    application.add_handler(CommandHandler("lifetips", menu_handlers.handle_lifetips_menu))
    application.add_handler(CommandHandler("apartment_private", list_handlers.list_apartments))
    application.add_handler(CommandHandler("groups", list_handlers.list_groups))
    application.add_handler(CommandHandler("places_restaurants", list_handlers.list_restaurants))
    application.add_handler(CommandHandler("places_cafe", list_handlers.list_cafes))
    application.add_handler(CommandHandler("places_attractions", list_handlers.list_attractions))
    application.add_handler(CommandHandler("places_libraries", list_handlers.list_libraries))
    application.add_handler(CommandHandler("places_supermarkets", list_handlers.list_supermarkets))
    application.add_handler(CommandHandler("places_drugstores", list_handlers.list_drugs))
    application.add_handler(CommandHandler("newarrival", general_info_handlers.handle_newarrival))
    application.add_handler(CommandHandler("immigration_registration", general_info_handlers.handle_immigration_registration))
    application.add_handler(CommandHandler("immigration_permit", general_info_handlers.handle_immigration_permit))
    application.add_handler(CommandHandler("healthcare_doctor", general_info_handlers.handle_healthcare_doctor))
    application.add_handler(CommandHandler("healthcare_emergency", general_info_handlers.handle_healthcare_emergency))
    application.add_handler(CommandHandler("apartment_studentwerk", general_info_handlers.handle_apartment_studentwerk))
    application.add_handler(CommandHandler("apartment_company", general_info_handlers.handle_apartment_company))
    application.add_handler(CommandHandler("education_german", general_info_handlers.handle_education_german))
    application.add_handler(CommandHandler("education_scholarships", general_info_handlers.handle_education_scholarships))
    application.add_handler(CommandHandler("education_erasmus", general_info_handlers.handle_education_erasmus))
    application.add_handler(CommandHandler("sports_university", general_info_handlers.handle_sports_university))
    application.add_handler(CommandHandler("lifetips_transport", general_info_handlers.handle_lifetips_transport))
    application.add_handler(CommandHandler("lifetips_deutschlandticket", general_info_handlers.handle_lifetips_deutschlandticket))
    application.add_handler(CommandHandler("lifetips_waste", general_info_handlers.handle_lifetips_waste))
    application.add_handler(CommandHandler("lifetips_legal", general_info_handlers.handle_lifetips_legal))
    application.add_handler(CommandHandler("lifetips_rundfunk", general_info_handlers.handle_lifetips_rundfunk))
    application.add_handler(CommandHandler("lifetips_daily", general_info_handlers.handle_lifetips_daily))
    application.add_handler(CommandHandler("insurance_health", case_specific_handlers.handle_insurance_health))
    application.add_handler(CommandHandler("insurance_private", case_specific_handlers.handle_insurance_private))
    application.add_handler(CommandHandler("lifetips_apps", case_specific_handlers.handle_lifetips_apps))
    application.add_handler(CommandHandler("lifetips_telecom", case_specific_handlers.handle_lifetips_telecom))
    application.add_handler(CommandHandler("lifetips_bank", case_specific_handlers.handle_lifetips_bank))
    application.add_handler(CommandHandler("sports_skating", case_specific_handlers.handle_sports_skating))
    application.add_handler(CommandHandler("sports_hiking", case_specific_handlers.handle_sports_hiking))
    application.add_handler(CommandHandler("sports_clubs", case_specific_handlers.handle_sports_clubs))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handlers.handle_message))

    logger.info("Bot application created and configured")
    return application
