import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import func
from app.bot.db import get_db
from app.db.models import Apartment, Place, WhatsAppGroup
from .base import BaseHandler
import logging
from app.utils.logger import setup_loggers

logger = logging.getLogger(__name__)
conversation_logger = setup_loggers()

class ListHandlers(BaseHandler):
    """Handlers for list commands."""
    async def list_groups(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List WhatsApp groups."""
        if not await self.check_access(update):
            await update.message.reply_text("Sorry, this bot is currently in development mode.")
            return

        async with get_db() as db:
            groups = db.query(WhatsAppGroup).all()
            if not groups:
                await update.message.reply_text("No WhatsApp groups available at the moment.")
                return

            # Send header message
            await update.message.reply_text("👥 Available Student WhatsApp Groups")
            
            # Send each group as a separate message
            for group in groups:
                message = (
                    f"📱 *{group.name}*\n\n"
                    f"🏷️ Category: {group.category}\n\n"
                    f"ℹ️ {group.description}\n\n"
                    f"🔗 [Join Group]({group.invite_link})"
                )
                try:
                    await update.message.reply_text(
                        message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    # Add small delay to prevent flood limits
                    await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error(f"Error sending group message: {e}")
                    continue

    async def list_apartments(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Lists random available apartments from the database.

        Args:
            update (Update): The Telegram update object.
            context (ContextTypes.DEFAULT_TYPE): The context object for the handler.

        Returns:
            None: This function doesn't return anything.
                Sends multiple messages:
                - Text description of each apartment
                - Optional image if available
        """
        if not await self.check_access(update):
            return
            
        async with get_db() as db:
            # Get 5 random apartments
            apartments = db.query(Apartment).order_by(func.random()).limit(5).all()
            if not apartments:
                await update.message.reply_text("No apartments available at the moment.")
                return

            for apt in apartments:
                # Prepare text message
                text = (
                    f"🏢 {apt.title}\n\n"
                    f"📍 {apt.address}\n\n"
                    f"📅 Available from: {apt.available_from}\n\n"
                    f"💶 Price: €{int(apt.price)}\n\n"
                    f"📐 Size: {int(apt.size)}m²{f', {apt.rooms} rooms' if apt.rooms else ''}\n\n"
                    f"🔗 More details:\n{apt.details_link}\n"
                )
                
                try:
                    # Send image with caption if image_url exists
                    if apt.image_url:
                        await update.message.reply_photo(
                            photo=apt.image_url,
                            caption=text,
                            parse_mode='HTML'
                        )
                    else:
                        # Send text only if no image
                        await update.message.reply_text(text)
                except Exception as e:
                    logger.error(f"Error sending apartment message: {e}")
                    # Fallback to text-only if image sending fails
                    await update.message.reply_text(text)

    async def _list_places_by_category(self, update: Update, category: str, emoji: str) -> None:
        """Helper method to list places by category."""
        if not await self.check_access(update):
            return

        async with get_db() as db:
            places = db.query(Place).filter(Place.category == category).all()
            if not places:
                await update.message.reply_text(f"No {category.lower()} available at the moment.")
                return

            # Send header message
            await update.message.reply_text(f"{emoji} {category.title()}")
            
            # Send each place as a separate message
            for place in places:
                message = (
                    f"🏢 *{place.name}*\n\n"
                    f"ℹ️ Description: {place.description}\n"
                    f"📍 Address: {place.address}\n"
                )
                if place.price_range:
                    message += f"💰 Price: {place.price_range}\n"
                message += f"⭐ Rating: {place.rating}"
                
                try:
                    await update.message.reply_text(
                        message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    # Add small delay to prevent flood limits
                    await asyncio.sleep(0.5)
                except Exception as e:
                    continue

    async def list_restaurants(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List restaurants."""
        await self._list_places_by_category(update, "restaurant", "🍽️")

    async def list_cafes(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List cafes."""
        await self._list_places_by_category(update, "cafe", "☕")

    async def list_attractions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List tourist attractions."""
        await self._list_places_by_category(update, "tourist attraction", "🎯")

    async def list_libraries(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List libraries."""
        await self._list_places_by_category(update, "library", "📚")

    async def list_supermarkets(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List supermarkets."""
        await self._list_places_by_category(update, "supermarket", "🛒")

    async def list_homegoods(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List home goods stores."""
        await self._list_places_by_category(update, "home goods", "🏠")

    async def list_drugs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List drugstores."""
        await self._list_places_by_category(update, "drugstore", "💄")

