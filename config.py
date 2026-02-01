import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8362379114:AAFg_bOXNSu5uiLagudbPGS4Hshjg53NAmM')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')  # Set this to your chat ID

# GitHub Repository Configuration
REPO_URL = os.getenv('REPO_URL', 'https://github.com/Arpitraj02/sapine-nodes-api')

# Workflow Configuration
WORKFLOW_INTERVAL_HOURS = int(os.getenv('WORKFLOW_INTERVAL_HOURS', '5'))
WORKFLOW_DURATION_HOURS = int(os.getenv('WORKFLOW_DURATION_HOURS', '5'))

# Flask Configuration
PORT = int(os.getenv('PORT', '10000'))
HOST = os.getenv('HOST', '0.0.0.0')

# Working Directory
WORK_DIR = os.getenv('WORK_DIR', '/tmp/workflow')
