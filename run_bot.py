#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
קובץ הפעלה מרכזי לבוט טלגרם עם כל התכונות המתקדמות
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
import signal
import argparse

# הוספת הנתיב הנוכחי לחיפוש מודולים
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ייבוא הבוט והתכונות
from main import TodoBot
from enhanced_features import EnhancedTodoBot
from config import config

class AdvancedTodoBot(TodoBot, EnhancedTodoBot):
    """בוט משולב עם כל התכונות המתקדמות"""
    
    def __init__(self, token: str, enable_enhanced_features: bool = True):
        TodoBot.__init__(self, token)
        EnhancedTodoBot.__init__(self, self.db_name)
        self.enable_enhanced = enable_enhanced_features
        
        # הגדרת לוגרים מתקדמים
        self.setup_advanced_logging()
    
    def setup_advanced_logging(self):
        """הגדרת מערכת לוגים מתקדמת"""
        # יצירת תיקיית לוגים
        os.makedirs('logs', exist_ok=True)
        
        # לוגר ראשי
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format=config.LOG_FORMAT,
            handlers=[
                logging.FileHandler(f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # לוגר פעילות משתמשים
        self.activity_logger = logging.getLogger('user_activity')
        activity_handler = logging.FileHandler(f'logs/activity_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8')
        activity_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.activity_logger.addHandler(activity_handler)
        self.activity_logger.setLevel(logging.INFO)
    
    def log_user_activity(self, user_id: int, username: str, action: str, details: str = ""):
        """רישום פעילות משתמש"""
        self.activity_logger.info(f"User {user_id} (@{username}) - {action} - {details}")
    
    def init_database(self):
        """יצירת מסד נתונים עם תכונות מתקדמות"""
        super().init_database()
        if self.enable_enhanced:
            self.init_enhanced_database()
    
    def setup_handlers(self):
        """הגדרת handlers עם תכונות מתקדמות"""
        super().setup_handlers()
        
        if self.enable_enhanced:
            # הוספת פקודות מתקדמות
            from telegram.ext import CommandHandler
            
            self.application.add_handler(CommandHandler("stats", self.stats_command))
            self.application.add_handler(CommandHandler("chart", self.show_productivity_chart))
            self.application.add_handler(CommandHandler("backup", self.backup_command))
            self.application.add_handler(CommandHandler("search", self.search_command))
    
    async def backup_command(self, update, context):
        """פקודת גיבוי"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "unknown"
        
        try:
            backup_file = await self.backup_user_data(user_id)
            
            await update.message.reply_document(
                document=open(backup_file, 'rb'),
                filename=f"backup_{username}_{datetime.now().strftime('%Y%m%d')}.json",
                caption="💾 **הגיבוי שלך מוכן!**\n\nשמור את הקובץ במקום בטוח."
            )
            
            # מחיקת הקובץ הזמני
            os.remove(backup_file)
            
            self.log_user_activity(user_id, username, "BACKUP", "Successfully created backup")
            
        except Exception as e:
            await update.message.reply_text("❌ שגיאה ביצירת הגיבוי. אנא נסה שוב מאוחר יותר.")
            logging.error(f"Backup error for user {user_id}: {e}")
    
    async def search_command(self, update, context):
        """פקודת חיפוש משימות"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "unknown"
        
        if not context.args:
            await update.message.reply_text(
                "🔍 **חיפוש במשימות**\n\n"
                "שימוש: `/search [מילת חיפוש]`\n"
                "דוגמה: `/search דוח`"
            )
            return
        
        search_query = " ".join(context.args)
        results = self.search_tasks(user_id, search_query)
        
        if not results:
            await update.message.reply_text(f"🔍 לא נמצאו משימות עבור '{search_query}'")
            return
        
        message = f"🔍 **תוצאות חיפוש עבור '{search_query}':**\n\n"
        
        for task_id, content, category, created_at in results[:10]:  # מקסימום 10 תוצאות
            message += f"📋 {content}\n"
            message += f"📂 {category} | 🆔 #{task_id}\n\n"
        
        if len(results) > 10:
            message += f"... ועוד {len(results) - 10} תוצאות נוספות"
        
        await update.message.reply_text(message)
        self.log_user_activity(user_id, username, "SEARCH", f"Query: '{search_query}', Results: {len(results)}")
    
    async def enhanced_add_task(self, user_id: int, content: str, category: str):
        """הוספת משימה מתקדמת עם ניתוח"""
        # הוספת המשימה הרגילה
        task_id = self.add_task(user_id, content, category)
        
        if self.enable_enhanced:
            # ניתוח התוכן לחילוץ תגיות
            import re
            
            # חיפוש תגיות (#tag)
            tags = re.findall(r'#(\w+)', content)
            
            if tags:
                # הוספת התגיות למשימה
                self.add_task_with_tags(user_id, content, category, tags)
            
            # רישום פעילות לסטטיסטיקות
            self.record_user_activity(user_id, 'task_created')
        
        return task_id
    
    def run_with_monitoring(self):
        """הרצת הבוט עם מעקב מתקדם"""
        def signal_handler(signum, frame):
            print(f"\n🛑 התקבל אות סיום ({signum})")
            print("💾 שומר נתונים...")
            
            # כאן ניתן להוסיף לוגיקת סגירה נקייה
            if hasattr(self, 'application') and self.application.running:
                self.application.stop()
            
            print("✅ הבוט נסגר בהצלחה")
            sys.exit(0)
        
        # הגדרת טיפול באותות סיום
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        print("🤖 מתחיל בוט מתקדם לניהול משימות...")
        print(f"📊 תכונות מתקדמות: {'✅ מופעל' if self.enable_enhanced else '❌ מבוטל'}")
        print(f"📁 מסד נתונים: {self.db_name}")
        print(f"📋 רמת לוגים: {config.LOG_LEVEL}")
        print("🚀 הבוט פועל! לחץ Ctrl+C לעצירה\n")
        
        try:
            self.run()
        except KeyboardInterrupt:
            print("\n🛑 הבוט הופסק על ידי המשתמש")
        except Exception as e:
            print(f"❌ שגיאה קריטית: {e}")
            logging.error(f"Critical error: {e}", exc_info=True)
        finally:
            print("👋 להתראות!")

def create_systemd_service():
    """יצירת קובץ שירות systemd להרצה אוטומטית"""
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    python_path = sys.executable
    
    service_content = f"""[Unit]
Description=Telegram Todo Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory={current_dir}
Environment=PATH={os.environ.get('PATH', '')}
Environment=TELEGRAM_BOT_TOKEN={os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TOKEN_HERE')}
ExecStart={python_path} {current_dir}/run_bot.py --production
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    with open('telegram-todo-bot.service', 'w') as f:
        f.write(service_content)
    
    print("📝 נוצר קובץ שירות: telegram-todo-bot.service")
    print("\n📋 הוראות התקנה:")
    print("1. sudo cp telegram-todo-bot.service /etc/systemd/system/")
    print("2. sudo systemctl daemon-reload")
    print("3. sudo systemctl enable telegram-todo-bot.service")
    print("4. sudo systemctl start telegram-todo-bot.service")
    print("5. sudo systemctl status telegram-todo-bot.service")

def main():
    """פונקציה ראשית עם תמיכה בארגומנטים"""
    parser = argparse.ArgumentParser(description='Telegram Todo Bot - מתקדם')
    parser.add_argument('--production', action='store_true', help='הרצה במצב ייצור')
    parser.add_argument('--no-enhanced', action='store_true', help='ביטול תכונות מתקדמות')
    parser.add_argument('--create-service', action='store_true', help='יצירת קובץ שירות systemd')
    parser.add_argument('--token', type=str, help='טוקן בוט טלגרם')
    parser.add_argument('--webhook', action='store_true', help='הפעלת מצב Webhook (מאזין ל-$PORT)')
    parser.add_argument('--polling', action='store_true', help='כפיית מצב Polling (מתעלם מ-$PORT)')
    
    args = parser.parse_args()
    
    if args.create_service:
        create_systemd_service()
        return
    
    # קביעת סביבת הפעלה
    if args.production:
        os.environ['BOT_ENV'] = 'production'
    
    # קבלת הטוקן
    token = args.token or os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ שגיאה: לא נמצא טוקן בוט!")
        print("\n💡 דרכים להגדיר טוקן:")
        print("1. משתנה סביבה: export TELEGRAM_BOT_TOKEN='your_token'")
        print("2. ארגומנט: python run_bot.py --token 'your_token'")
        print("3. קובץ .env בתיקיית הפרויקט")
        return 1
    
    # בדיקת תקינות הגדרות
    try:
        config.validate()
    except ValueError as e:
        print(f"❌ שגיאה בהגדרות: {e}")
        return 1
    
    # יצירת ובוט
    enable_enhanced = not args.no_enhanced
    bot = AdvancedTodoBot(token, enable_enhanced_features=enable_enhanced)
    
    # בחירת מצב הרצה: Webhook כאשר מוגדר PORT (Render) אלא אם נכפה polling
    port_env = os.getenv('PORT')
    use_webhook = args.webhook or (port_env is not None and not args.polling)

    # הרצת הבוט
    try:
        if use_webhook:
            port = int(port_env or os.getenv('WEBHOOK_PORT', '10000'))
            url_path = os.getenv('WEBHOOK_PATH', token)
            external_url = os.getenv('WEBHOOK_URL') or os.getenv('RENDER_EXTERNAL_URL')
            webhook_url = None
            if external_url:
                external_url = external_url.rstrip('/')
                webhook_url = f"{external_url}/{url_path}"

            print("🤖 מתחיל בוט במצב Webhook...")
            print(f"🛰 מאזין על 0.0.0.0:{port} | path=/{url_path}")
            if webhook_url:
                print(f"🌐 Webhook URL: {webhook_url}")
            else:
                print("⚠️ לא הוגדרה כתובת WEBHOOK_URL/RENDER_EXTERNAL_URL — השרת יאזין מקומית בלבד")

            bot.run_webhook(port=port, url_path=url_path, webhook_url=webhook_url)
        else:
            bot.run_with_monitoring()
        return 0
    except Exception as e:
        print(f"❌ שגיאה בהפעלת הבוט: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)