from telegram import Update
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db.models import GeneralInfo
from app.bot.constants import DEVELOPMENT_MODE_MESSAGE, INFO_NOT_AVAILABLE

class BaseHandler:
    """Base class for all command handlers."""
    def __init__(self):
        """Initialize the handler."""
        self.settings = get_settings()

    async def check_access(self, update: Update) -> bool:
        """Check if user has access in development mode."""
        if self.settings.DEVELOPMENT_MODE:
            has_access = update.message.from_user.id == self.settings.DEVELOPER_USER_ID
            if not has_access:
                await update.message.reply_text(DEVELOPMENT_MODE_MESSAGE)
            return has_access
        return True

    async def get_general_info_from_db(self, db: Session, title: str) -> str:
        """Get information from database by title."""
        info = db.query(GeneralInfo).filter(GeneralInfo.title == title).first()
        return info.description if info else INFO_NOT_AVAILABLE

    async def send_menu_message(self, update: Update, message: str) -> None:
        """Send a menu message to the user."""
        if not await self.check_access(update):
            return
        await update.message.reply_text(message)

    async def send_info_message(self, update: Update, db: Session, title: str) -> None:
        """Send an info message to the user."""
        if not await self.check_access(update):
            return
        response = await self.get_general_info_from_db(db, title)
        await update.message.reply_text(response)
