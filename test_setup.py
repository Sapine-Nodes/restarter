#!/usr/bin/env python3
"""
Simple test script to verify the application setup
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        import flask
        import requests
        import telegram
        from apscheduler.schedulers.background import BackgroundScheduler
        print("✅ All dependencies imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_modules():
    """Test that all custom modules can be imported"""
    print("\nTesting custom modules...")
    try:
        import config
        import telegram_notifier
        import workflow_executor
        import app
        print("✅ All custom modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Module import error: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    try:
        import config
        print(f"  Bot Token: {'Set' if config.TELEGRAM_BOT_TOKEN else 'Not Set'}")
        print(f"  Chat ID: {'Set' if config.TELEGRAM_CHAT_ID else 'Not Set (⚠️  Required for notifications)'}")
        print(f"  Repo URL: {config.REPO_URL}")
        print(f"  Workflow Interval: {config.WORKFLOW_INTERVAL_HOURS} hours")
        print(f"  Workflow Duration: {config.WORKFLOW_DURATION_HOURS} hours")
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_telegram():
    """Test Telegram connection (if configured)"""
    print("\nTesting Telegram connection...")
    try:
        from telegram_notifier import TelegramNotifier
        import config
        
        if not config.TELEGRAM_CHAT_ID:
            print("⚠️  TELEGRAM_CHAT_ID not set. Skipping Telegram test.")
            print("   Set TELEGRAM_CHAT_ID to enable Telegram notifications.")
            return True
        
        notifier = TelegramNotifier()
        # Try to send a test message
        success = notifier.send_message("🧪 Test message from VPS Workflow Automation")
        
        if success:
            print("✅ Telegram connection successful! Check your Telegram for the test message.")
        else:
            print("⚠️  Failed to send Telegram message. Check your bot token and chat ID.")
        
        return True
    except Exception as e:
        print(f"❌ Telegram test error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("VPS Workflow Automation - Setup Test")
    print("=" * 60)
    
    results = []
    results.append(test_imports())
    results.append(test_modules())
    results.append(test_config())
    results.append(test_telegram())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed! The application is ready to run.")
        print("\nTo start the server, run:")
        print("  python app.py")
        print("\nOr with gunicorn:")
        print("  gunicorn app:app")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
