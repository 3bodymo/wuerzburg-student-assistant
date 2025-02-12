from telegram import Update
from telegram.ext import ContextTypes
from app.bot.db import get_db
from .base import BaseHandler

class GeneralInfoHandlers(BaseHandler):
    """Handlers for information commands."""
    async def handle_immigration_registration(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "City Registration")

    async def handle_immigration_permit(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "Residence Permit Application")

    async def handle_healthcare_doctor(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "Visiting a Doctor")

    async def handle_healthcare_emergency(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "Medical On-Call Service")

    async def handle_apartment_studentwerk(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "Studentwerk Apartments")

    async def handle_apartment_company(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "Apartments Under Company Management")

    async def handle_education_german(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "German Language Courses")

    async def handle_education_scholarships(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "Scholarships")

    async def handle_education_erasmus(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "Erasmus Semester Abroad")

    async def handle_sports_university(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "University Sports Center")

    async def handle_lifetips_transport(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "Free Public Transport")

    async def handle_lifetips_deutschlandticket(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "Deutschland Ticket")

    async def handle_lifetips_waste(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "Waste Separation")
            
    async def handle_lifetips_legal(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "Free Legal Services")
            
    async def handle_lifetips_rundfunk(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
       async with get_db() as db:
            await self.send_info_message(update, db, "Radio and TV Tax (Rundfunkbeitrag)")
            
    async def handle_lifetips_daily(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        async with get_db() as db:
            await self.send_info_message(update, db, "Important Daily Life Info")
            
    async def handle_newarrival(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle new arrival information."""
        async with get_db() as db:
            await self.send_info_message(update, db, "New Student Checklist")