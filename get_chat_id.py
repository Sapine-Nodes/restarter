#!/usr/bin/env python3
"""
Helper script to get your Telegram Chat ID
Usage: python get_chat_id.py YOUR_BOT_TOKEN
"""

import sys
import requests

def get_chat_id(bot_token):
    """Get chat ID by fetching updates from Telegram bot"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('result'):
            print("❌ No messages found!")
            print("\n📝 To get your chat ID:")
            print("1. Start a chat with your bot on Telegram")
            print("2. Send any message to the bot")
            print("3. Run this script again")
            print("\nOr use @userinfobot on Telegram to get your chat ID directly.")
            return
        
        print("✅ Found chat messages!\n")
        seen_chats = set()
        
        for update in data['result']:
            if 'message' in update:
                chat = update['message']['chat']
                chat_id = chat['id']
                chat_type = chat.get('type', 'unknown')
                
                if chat_id not in seen_chats:
                    seen_chats.add(chat_id)
                    
                    if chat_type == 'private':
                        name = f"{chat.get('first_name', '')} {chat.get('last_name', '')}".strip()
                        username = chat.get('username', 'N/A')
                        print(f"👤 Private Chat")
                        print(f"   Name: {name}")
                        print(f"   Username: @{username}")
                        print(f"   Chat ID: {chat_id}")
                        print()
                    else:
                        title = chat.get('title', 'Unknown')
                        print(f"👥 Group Chat: {title}")
                        print(f"   Chat ID: {chat_id}")
                        print()
        
        if seen_chats:
            print("\n💡 Add one of these Chat IDs to your .env file:")
            print("   TELEGRAM_CHAT_ID=<your_chat_id>")
        
    except requests.RequestException as e:
        print(f"❌ Error connecting to Telegram: {e}")
        print("\n⚠️  Please check your bot token and internet connection.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python get_chat_id.py YOUR_BOT_TOKEN")
        print("\n📝 Get your bot token from @BotFather on Telegram")
        sys.exit(1)
    
    bot_token = sys.argv[1]
    get_chat_id(bot_token)
