from telegram import Update
from telegram.ext import ContextTypes
from app.bot.constants import (
    WELCOME_MESSAGE,
    APARTMENT_MENU,
    PLACES_MENU,
    INSURANCE_MENU,
    IMMIGRATION_MENU,
    HEALTHCARE_MENU,
    SPORTS_MENU,
    EDUCATION_MENU,
    LIFETIPS_MENU,
)
from .base import BaseHandler

class MenuHandlers(BaseHandler):
    """Handlers for main menu commands."""
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send welcome message when /start command is issued."""
        await self.send_menu_message(update, WELCOME_MESSAGE)

    async def handle_apartment_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show apartment options menu."""
        await self.send_menu_message(update, APARTMENT_MENU)

    async def handle_places_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show places categories menu."""
        await self.send_menu_message(update, PLACES_MENU)

    async def handle_insurance_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show insurance options menu."""
        await self.send_menu_message(update, INSURANCE_MENU)

    async def handle_immigration_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show immigration services menu."""
        await self.send_menu_message(update, IMMIGRATION_MENU)

    async def handle_healthcare_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show healthcare services menu."""
        await self.send_menu_message(update, HEALTHCARE_MENU)

    async def handle_sports_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show sports activities menu."""
        await self.send_menu_message(update, SPORTS_MENU)

    async def handle_education_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show educational resources menu."""
        await self.send_menu_message(update, EDUCATION_MENU)

    async def handle_lifetips_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show life tips menu."""
        await self.send_menu_message(update, LIFETIPS_MENU)
