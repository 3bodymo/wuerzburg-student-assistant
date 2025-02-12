import logging
from app.utils.logger import setup_loggers
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from app.bot.db import get_db
from .base import BaseHandler
from app.db.models import Apartment, GeneralInfo, Insurance, UsefulApp, TelecomProvider, Bank
from sqlalchemy import func

logger = logging.getLogger(__name__)
conversation_logger = setup_loggers()

class CaseSpecificHandlers(BaseHandler):
    """Handlers for case-specific information."""
    async def list_apartments(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Lists random available apartments from the database."""
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

    async def handle_insurance_health(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle health insurance command."""
        if not await self.check_access(update):
            return
            
        async with get_db() as db:
            insurances = db.query(Insurance).filter(
                Insurance.category.in_(['Public Health Insurance', 'Private Health Insurance'])
            ).all()
            
            if not insurances:
                await update.message.reply_text("No health insurance information available.")
                return
                
            # Send header message
            await update.message.reply_text("🏥 Health Insurance Options")
            
            # Send each insurance company as a separate message
            for insurance in insurances:
                message = (
                    f"🏢 *{insurance.company_name}*\n\n"
                    f"📋 Type: {insurance.category}\n\n"
                    f"ℹ️ {insurance.description}\n\n"
                    f"🔗 [Visit Website]({insurance.company_url})"
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
                    logger.error(f"Error sending insurance message: {e}")
                    continue

    async def handle_insurance_private(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle private insurance command."""
        if not await self.check_access(update):
            return
            
        async with get_db() as db:
            insurances = db.query(Insurance).filter(
                Insurance.category == 'Private Insurance'
            ).all()
            
            if not insurances:
                await update.message.reply_text("No private insurance information available.")
                return
                
            # Send header message
            await update.message.reply_text("🔒 Private Insurance Options")
            
            # Send each insurance company as a separate message
            for insurance in insurances:
                message = (
                    f"🏢 *{insurance.company_name}*\n\n"
                    f"ℹ️ {insurance.description}\n\n"
                    f"🔗 [Visit Website]({insurance.company_url})"
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
                    logger.error(f"Error sending insurance message: {e}")
                    continue

    async def handle_lifetips_apps(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle useful apps command."""
        if not await self.check_access(update):
            return
            
        async with get_db() as db:
            apps = db.query(UsefulApp).all()
            
            if not apps:
                await update.message.reply_text("No app information available.")
                return
                
            # Send header message
            await update.message.reply_text("📱 Useful Apps for Students")
            
            # Send each app as a separate message
            for app in apps:
                message = (
                    f"📱 *{app.name}*\n\n"
                    f"🏷️ Category: {app.category}\n\n"
                    f"ℹ️ {app.description}\n\n"
                )
                
                # Add store links if available
                store_links = []
                if app.app_store_url:
                    store_links.append(f"[App Store]({app.app_store_url})")
                if app.play_store_url:
                    store_links.append(f"[Play Store]({app.play_store_url})")
                    
                if store_links:
                    message += "🔗 " + " | ".join(store_links)
                
                try:
                    await update.message.reply_text(
                        message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    await asyncio.sleep(0.5)  # Small delay to prevent flood limits
                except Exception as e:
                    logger.error(f"Error sending app message: {e}")
                    continue

    async def handle_lifetips_telecom(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle telecom providers command."""
        if not await self.check_access(update):
            return
            
        async with get_db() as db:
            providers = db.query(TelecomProvider).all()
            
            if not providers:
                await update.message.reply_text("No telecom provider information available.")
                return
                
            # Send header message
            await update.message.reply_text("📱 Telecom Providers")
            
            # Send each provider as a separate message
            for provider in providers:
                message = (
                    f"📡 *{provider.name}*\n\n"
                    f"ℹ️ {provider.description}\n\n"
                    f"🔗 [Visit Website]({provider.website_url})"
                )
                try:
                    await update.message.reply_text(
                        message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    await asyncio.sleep(0.5)  # Small delay to prevent flood limits
                except Exception as e:
                    logger.error(f"Error sending provider message: {e}")
                    continue

    async def handle_lifetips_bank(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle bank information command."""
        if not await self.check_access(update):
            return
            
        async with get_db() as db:
            banks = db.query(Bank).all()
            
            if not banks:
                await update.message.reply_text("No bank information available.")
                return
                
            # Send header message
            await update.message.reply_text("🏦 Bank Options for Students")
            
            # Send each bank as a separate message
            for bank in banks:
                message = (
                    f"🏦 *{bank.name}*\n\n"
                    f"ℹ️ {bank.description}\n\n"
                    f"💳 Free student plan: {'✅ Available' if bank.free_student_plan_available else '❌ Not available'}\n\n"
                    f"🔗 [Visit Website]({bank.website_url})"
                )
                try:
                    await update.message.reply_text(
                        message,
                        parse_mode='Markdown',
                        disable_web_page_preview=True
                    )
                    await asyncio.sleep(0.5)  # Small delay to prevent flood limits
                except Exception as e:
                    logger.error(f"Error sending bank message: {e}")
                    continue

    async def handle_sports_skating(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle skating places information."""
        if not await self.check_access(update):
            return
        
        async with get_db() as db:
            places = db.query(GeneralInfo).filter(GeneralInfo.category == "Skating Places").all()
            if not places:
                await update.message.reply_text("No skating places information available.")
                return
                
            # Send header message
            await update.message.reply_text("⛸️ Skating Places in Würzburg")
            
            # Send each place as a separate message
            for place in places:
                try:
                    await update.message.reply_text(
                        f"🏟️ *{place.title}*\n\n"
                        f"ℹ️ {place.description}",
                        parse_mode='Markdown'
                    )
                    await asyncio.sleep(0.5)  # Small delay to prevent flood limits
                except Exception as e:
                    logger.error(f"Error sending skating place message: {e}")
                    continue

    async def handle_sports_hiking(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle hiking trails information."""
        if not await self.check_access(update):
            return
        
        async with get_db() as db:
            trails = db.query(GeneralInfo).filter(GeneralInfo.category == "Hiking Trails").all()
            if not trails:
                await update.message.reply_text("No hiking trails information available.")
                return
                
            # Send header message
            await update.message.reply_text("🏃‍♂️ Hiking Trails around Würzburg")
            
            # Send each trail as a separate message
            for trail in trails:
                try:
                    await update.message.reply_text(
                        f"🏃‍♂️ *{trail.title}*\n\n"
                        f"ℹ️ {trail.description}",
                        parse_mode='Markdown'
                    )
                    await asyncio.sleep(0.5)  # Small delay to prevent flood limits
                except Exception as e:
                    logger.error(f"Error sending hiking trail message: {e}")
                    continue

    async def handle_sports_clubs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle sports clubs information."""
        if not await self.check_access(update):
            return
        
        async with get_db() as db:
            clubs = db.query(GeneralInfo).filter(GeneralInfo.category == "Sports Clubs").all()
            if not clubs:
                await update.message.reply_text("No sports clubs information available.")
                return
                
            # Send header message
            await update.message.reply_text("⚽ Sports Clubs in Würzburg")
            
            # Send each club as a separate message
            for club in clubs:
                try:
                    await update.message.reply_text(
                        f"🏆 *{club.title}*\n\n"
                        f"ℹ️ {club.description}",
                        parse_mode='Markdown'
                    )
                    await asyncio.sleep(0.5)  # Small delay to prevent flood limits
                except Exception as e:
                    logger.error(f"Error sending sports club message: {e}")
                    continue
