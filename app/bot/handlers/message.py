import logging
import re
from telegram import Update
from telegram.ext import ContextTypes
from telegram.error import NetworkError, TimedOut
from app.services.rag_service import RAGService
from app.utils.logger import log_conversation
from app.bot.constants import ERROR_NETWORK, ERROR_TIMEOUT, ERROR_UNEXPECTED, ERROR_PROCESSING
from .base import BaseHandler

logger = logging.getLogger(__name__)
rag_service = RAGService()

class MessageHandlers(BaseHandler):
    """Handlers for messages and errors."""    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle user messages and respond using RAG."""
        if not await self.check_access(update):
            return

        user_message = update.message.text
        try:
            # Send typing action while processing
            await update.message.chat.send_action(action="typing")
            answer, sources = rag_service.query(user_message)
            
            # Log the conversation
            log_conversation(
                user_id=update.message.from_user.id,
                username=update.message.from_user.username or "Unknown",
                message=user_message,
                response=answer
            )
            
            escaped_answer = self._escape_markdown(answer)
            await update.message.reply_text(
                escaped_answer,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(ERROR_PROCESSING)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle errors in the application."""
        logger.error(f"Exception while handling an update: {context.error}")
        
        if isinstance(context.error, NetworkError):
            message = ERROR_NETWORK
        elif isinstance(context.error, TimedOut):
            message = ERROR_TIMEOUT
        else:
            message = ERROR_UNEXPECTED
        
        if update and update.message:
            try:
                await update.message.reply_text(message)
            except Exception as e:
                logger.error(f"Error sending error message: {e}")
                
    def _escape_markdown(self, text: str) -> str:
        """Escapes special characters for Markdown formatting."""
        escape_chars = r'\*_`\['
        return re.sub(f'([{escape_chars}])', r'\\\1', text)
