import requests
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Handles sending notifications to Telegram bot"""
    
    def __init__(self, bot_token=None, chat_id=None):
        self.bot_token = bot_token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, message, parse_mode='HTML'):
        """Send a message to the configured Telegram chat"""
        if not self.chat_id:
            logger.warning("TELEGRAM_CHAT_ID not set. Message not sent: %s", message)
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Message sent to Telegram successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send message to Telegram: {e}")
            return False
    
    def send_formatted_message(self, title, details):
        """Send a formatted message with title and details"""
        message = f"<b>{title}</b>\n\n{details}"
        return self.send_message(message)
    
    def send_workflow_start(self, workflow_id):
        """Send workflow start notification"""
        message = f"🚀 <b>New VPS Workflow Started</b>\n\nWorkflow ID: {workflow_id}\nStatus: Initializing..."
        return self.send_message(message)
    
    def send_workflow_step(self, workflow_id, step, status="In Progress"):
        """Send workflow step notification"""
        emoji = "⏳" if status == "In Progress" else "✅" if status == "Success" else "❌"
        message = f"{emoji} <b>Workflow {workflow_id}</b>\n\nStep: {step}\nStatus: {status}"
        return self.send_message(message)
    
    def send_sshx_url(self, workflow_id, url):
        """Send SSHX URL notification"""
        message = f"🔗 <b>SSHX URL Ready</b>\n\nWorkflow ID: {workflow_id}\n\nURL: <code>{url}</code>\n\nYou can now access the VPS via this link!"
        return self.send_message(message)
    
    def send_workflow_end(self, workflow_id, success=True):
        """Send workflow end notification"""
        emoji = "✅" if success else "❌"
        status = "Completed Successfully" if success else "Failed"
        message = f"{emoji} <b>Workflow Ended</b>\n\nWorkflow ID: {workflow_id}\nStatus: {status}"
        return self.send_message(message)
    
    def send_error(self, workflow_id, error_message):
        """Send error notification"""
        message = f"❌ <b>Workflow Error</b>\n\nWorkflow ID: {workflow_id}\n\nError: {error_message}"
        return self.send_message(message)
