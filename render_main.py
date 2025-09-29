#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
גרסה מותאמת ל-Render של בוט ניהול המשימות
"""

import os
import sys
import logging
import asyncio
from main import TodoBot

def setup_render_logging():
    """הגדרת לוגים מותאמת ל-Render"""
    
    # הגדרת רמת לוגים על פי סביבה
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout,
        force=True
    )
    
    # השקטת לוגים מיותרים
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('telegram').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

def validate_environment():
    """בדיקת משתני סביבה נדרשים"""
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ שגיאה: TELEGRAM_BOT_TOKEN לא נמצא!")
        print("\n💡 הוראות הגדרה:")
        print("1. כנס להגדרות ה-Service ב-Render")
        print("2. לך ל-Environment Variables")
        print("3. הוסף: TELEGRAM_BOT_TOKEN = <הטוקן שלך>")
        print("4. שמור ופרוס מחדש")
        return None
    
    return token

def create_render_health_check():
    """יצירת בדיקת בריאות פשוטה ל-Render"""
    
    # יצירת קובץ health check
    health_file = '/tmp/bot_health.txt'
    
    try:
        with open(health_file, 'w') as f:
            f.write(f"Bot running at {os.environ.get('RENDER_SERVICE_NAME', 'unknown')}")
        
        return True
    except Exception as e:
        logging.error(f"Failed to create health check: {e}")
        return False

def main():
    """פונקציה ראשית מותאמת ל-Render"""
    
    # הגדרת לוגים
    logger = setup_render_logging()
    
    logger.info("🚀 מתחיל בוט טלגרם ב-Render...")
    
    # הדפסת מידע על הסביבה
    service_name = os.getenv('RENDER_SERVICE_NAME', 'Unknown')
    region = os.getenv('RENDER_SERVICE_REGION', 'Unknown')
    
    logger.info(f"🔧 Service: {service_name}")
    logger.info(f"🌍 Region: {region}")
    logger.info(f"🐍 Python: {sys.version}")
    
    # בדיקת משתני סביבה
    token = validate_environment()
    if not token:
        sys.exit(1)
    
    logger.info(f"🔑 טוקן נטען בהצלחה: {token[:10]}...")
    
    # יצירת health check
    if create_render_health_check():
        logger.info("✅ Health check נוצר בהצלחה")
    
    # יצירת הבוט
    try:
        bot = TodoBot(token)
        logger.info("🤖 בוט נוצר בהצלחה")
        
        # הפעלת הבוט
        logger.info("🎯 מתחיל polling...")
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 הבוט הופסק על ידי משתמש")
    except Exception as e:
        logger.error(f"❌ שגיאה קריטית: {e}")
        logger.exception("פרטי השגיאה:")
        sys.exit(1)
    finally:
        logger.info("👋 הבוט נסגר")

if __name__ == '__main__':
    main()