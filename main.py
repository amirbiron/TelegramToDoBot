#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בוט טלגרם לניהול משימות (To-Do Bot)
מאת: כותב תוכן טכנולוגי
"""

import sqlite3
import logging
import asyncio
from datetime import datetime, time
from typing import Dict, List, Optional
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import pytz
from config import config

# הגדרת לוגים
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# הגדרות גלובליות
DB_NAME = 'todo_tasks.db'
TIMEZONE = pytz.timezone('Asia/Jerusalem')

class TodoBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.user_states: Dict[int, str] = {}
        self.pending_tasks: Dict[int, Dict] = {}
        self.db_name = config.DATABASE_NAME
        
    def init_database(self):
        """יצירת מסד הנתונים והטבלאות"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # טבלת משימות
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                status TEXT DEFAULT 'open',
                category TEXT DEFAULT 'כללי',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # טבלת קטגוריות
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                emoji TEXT DEFAULT '📂',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, name)
            )
        ''')
        
        # הוספת קטגוריות ברירת מחדל
        default_categories = [
            ('עבודה', '💼'),
            ('לימודים', '📚'),
            ('אישי', '🏠'),
            ('כללי', '➕')
        ]
        
        for category, emoji in default_categories:
            cursor.execute('''
                INSERT OR IGNORE INTO categories (user_id, name, emoji) 
                VALUES (0, ?, ?)
            ''', (category, emoji))
        
        conn.commit()
        conn.close()
        
    def get_user_categories(self, user_id: int) -> List[tuple]:
        """קבלת קטגוריות של משתמש"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, emoji FROM categories 
            WHERE user_id = ? OR user_id = 0
            ORDER BY name
        ''', (user_id,))
        
        categories = cursor.fetchall()
        conn.close()
        return categories
        
    def add_category(self, user_id: int, name: str, emoji: str = '📂'):
        """הוספת קטגוריה חדשה"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO categories (user_id, name, emoji) 
                VALUES (?, ?, ?)
            ''', (user_id, name, emoji))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
            
    def add_task(self, user_id: int, content: str, category: str = 'כללי'):
        """הוספת משימה חדשה"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (user_id, content, category) 
            VALUES (?, ?, ?)
        ''', (user_id, content, category))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
        
    def get_tasks(self, user_id: int, category: str = None, status: str = 'open') -> List[tuple]:
        """קבלת משימות לפי קטגוריה וסטטוס"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT id, content, category, created_at 
                FROM tasks 
                WHERE user_id = ? AND category = ? AND status = ?
                ORDER BY created_at DESC
            ''', (user_id, category, status))
        else:
            cursor.execute('''
                SELECT id, content, category, created_at 
                FROM tasks 
                WHERE user_id = ? AND status = ?
                ORDER BY category, created_at DESC
            ''', (user_id, status))
            
        tasks = cursor.fetchall()
        conn.close()
        return tasks
        
    def update_task_status(self, task_id: int, user_id: int, status: str):
        """עדכון סטטוס משימה"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tasks 
            SET status = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ? AND user_id = ?
        ''', (status, task_id, user_id))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
        
    def delete_task(self, task_id: int, user_id: int):
        """מחיקת משימה"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM tasks 
            WHERE id = ? AND user_id = ?
        ''', (task_id, user_id))
        
        affected = cursor.rowcount
        conn.commit()
        conn.close()
        return affected > 0
        
    def get_task_summary(self, user_id: int) -> Dict:
        """קבלת סיכום משימות לפי קטגוריה"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, COUNT(*) as count 
            FROM tasks 
            WHERE user_id = ? AND status = 'open'
            GROUP BY category
            ORDER BY category
        ''', (user_id,))
        
        summary = {}
        for category, count in cursor.fetchall():
            summary[category] = count
            
        conn.close()
        return summary

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """פקודת התחלה"""
        welcome_message = """
🤖 **ברוך הבא לבוט ניהול המשימות!**

📝 **פקודות זמינות:**
• `/add` - הוספת משימה חדשה
• `/list` - הצגת משימות לפי קטגוריה
• `/categories` - ניהול קטגוריות
• `/done` - סימון משימה כבוצעה
• `/delete` - מחיקת משימה
• `/summary` - סיכום משימות פתוחות

💡 **טיפ:** השתמש בכפתורים המהירים כדי לנווט בקלות!

בואו נתחיל לנהל את המשימות שלך ביעילות! 🚀
        """
        await update.message.reply_text(welcome_message, parse_mode='Markdown')

    async def add_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """הוספת משימה חדשה"""
        user_id = update.effective_user.id
        self.user_states[user_id] = 'waiting_task_content'
        
        await update.message.reply_text(
            "📝 **הוספת משימה חדשה**\n\n"
            "אנא כתוב את תוכן המשימה:",
            parse_mode='Markdown'
        )

    async def categories_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """הצגת וניהול קטגוריות"""
        user_id = update.effective_user.id
        categories = self.get_user_categories(user_id)
        
        keyboard = []
        for category, emoji in categories:
            keyboard.append([InlineKeyboardButton(
                f"{emoji} {category}", 
                callback_data=f"view_category_{category}"
            )])
        
        keyboard.append([InlineKeyboardButton(
            "➕ הוסף קטגוריה חדשה", 
            callback_data="add_new_category"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = "📂 **הקטגוריות שלך:**\n\n"
        message += "בחר קטגוריה לצפייה במשימות או הוסף קטגוריה חדשה:"
        
        await update.message.reply_text(
            message, 
            reply_markup=reply_markup, 
            parse_mode='Markdown'
        )

    async def list_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """הצגת משימות"""
        user_id = update.effective_user.id
        categories = self.get_user_categories(user_id)
        
        keyboard = []
        for category, emoji in categories:
            task_count = len(self.get_tasks(user_id, category))
            button_text = f"{emoji} {category}"
            if task_count > 0:
                button_text += f" ({task_count})"
            
            keyboard.append([InlineKeyboardButton(
                button_text, 
                callback_data=f"list_category_{category}"
            )])
        
        keyboard.append([InlineKeyboardButton(
            "📋 כל המשימות", 
            callback_data="list_all_tasks"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📋 **המשימות שלך**\n\n"
            "בחר קטגוריה לצפייה במשימות:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def summary_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """סיכום משימות פתוחות"""
        user_id = update.effective_user.id
        summary = self.get_task_summary(user_id)
        
        if not summary:
            await update.message.reply_text(
                "🎉 **מעולה!**\n\n"
                "אין לך משימות פתוחות כרגע.\n"
                "זמן טוב להוסיף משימות חדשות! 📝"
            )
            return
        
        message = "📊 **סיכום המשימות הפתוחות שלך:**\n\n"
        total_tasks = 0
        
        for category, count in summary.items():
            categories = self.get_user_categories(user_id)
            emoji = '📂'
            for cat_name, cat_emoji in categories:
                if cat_name == category:
                    emoji = cat_emoji
                    break
            
            message += f"{emoji} **{category}:** {count} משימות\n"
            total_tasks += count
        
        message += f"\n📈 **סך הכל:** {total_tasks} משימות פתוחות"
        
        keyboard = [[InlineKeyboardButton(
            "📋 צפה במשימות", 
            callback_data="list_all_tasks"
        )]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message, 
            reply_markup=reply_markup, 
            parse_mode='Markdown'
        )

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בלחיצות על כפתורים"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data.startswith('list_category_'):
            category = data.replace('list_category_', '')
            await self.show_category_tasks(query, user_id, category)
            
        elif data == 'list_all_tasks':
            await self.show_all_tasks(query, user_id)
            
        elif data.startswith('task_done_'):
            task_id = int(data.replace('task_done_', ''))
            await self.mark_task_done(query, user_id, task_id)
            
        elif data.startswith('task_delete_'):
            task_id = int(data.replace('task_delete_', ''))
            await self.delete_task_callback(query, user_id, task_id)
            
        elif data == 'add_new_category':
            self.user_states[user_id] = 'waiting_category_name'
            await query.edit_message_text(
                "📂 **הוספת קטגוריה חדשה**\n\n"
                "אנא כתוב את שם הקטגוריה החדשה:"
            )

    async def show_category_tasks(self, query, user_id: int, category: str):
        """הצגת משימות של קטגוריה מסוימת"""
        tasks = self.get_tasks(user_id, category)
        
        if not tasks:
            await query.edit_message_text(
                f"📂 **קטגוריה: {category}**\n\n"
                "אין משימות פתוחות בקטגוריה זו.\n"
                "השתמש ב-/add כדי להוסיף משימה חדשה! 📝"
            )
            return
        
        message = f"📂 **משימות בקטגוריה: {category}**\n\n"
        keyboard = []
        
        for task_id, content, _, created_at in tasks:
            message += f"• {content}\n"
            keyboard.append([
                InlineKeyboardButton("✅ בוצע", callback_data=f"task_done_{task_id}"),
                InlineKeyboardButton("🗑 מחק", callback_data=f"task_delete_{task_id}")
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 חזור לקטגוריות", callback_data="back_to_categories")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup)

    async def show_all_tasks(self, query, user_id: int):
        """הצגת כל המשימות"""
        tasks = self.get_tasks(user_id)
        
        if not tasks:
            await query.edit_message_text(
                "🎉 **מעולה!**\n\n"
                "אין לך משימות פתוחות כרגע.\n"
                "השתמש ב-/add כדי להוסיף משימה חדשה! 📝"
            )
            return
        
        message = "📋 **כל המשימות הפתוחות שלך:**\n\n"
        keyboard = []
        current_category = None
        
        for task_id, content, category, created_at in tasks:
            if category != current_category:
                if current_category is not None:
                    message += "\n"
                
                # מציאת האימוג'י של הקטגוריה
                categories = self.get_user_categories(user_id)
                emoji = '📂'
                for cat_name, cat_emoji in categories:
                    if cat_name == category:
                        emoji = cat_emoji
                        break
                
                message += f"**{emoji} {category}:**\n"
                current_category = category
            
            message += f"• {content}\n"
            keyboard.append([
                InlineKeyboardButton("✅ בוצע", callback_data=f"task_done_{task_id}"),
                InlineKeyboardButton("🗑 מחק", callback_data=f"task_delete_{task_id}")
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)

    async def mark_task_done(self, query, user_id: int, task_id: int):
        """סימון משימה כבוצעה"""
        success = self.update_task_status(task_id, user_id, 'done')
        
        if success:
            await query.answer("✅ המשימה סומנה כבוצעה!")
            # רענון התצוגה
            await self.show_all_tasks(query, user_id)
        else:
            await query.answer("❌ שגיאה בעדכון המשימה")

    async def delete_task_callback(self, query, user_id: int, task_id: int):
        """מחיקת משימה"""
        success = self.delete_task(task_id, user_id)
        
        if success:
            await query.answer("🗑 המשימה נמחקה!")
            # רענון התצוגה
            await self.show_all_tasks(query, user_id)
        else:
            await query.answer("❌ שגיאה במחיקת המשימה")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בהודעות טקסט"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if user_id not in self.user_states:
            await update.message.reply_text(
                "👋 שלום! השתמש ב-/start כדי לראות את הפקודות הזמינות."
            )
            return
        
        state = self.user_states[user_id]
        
        if state == 'waiting_task_content':
            # שמירת תוכן המשימה והמעבר לבחירת קטגוריה
            self.pending_tasks[user_id] = {'content': text}
            categories = self.get_user_categories(user_id)
            
            keyboard = []
            for category, emoji in categories:
                keyboard.append([InlineKeyboardButton(
                    f"{emoji} {category}", 
                    callback_data=f"select_category_{category}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            self.user_states[user_id] = 'waiting_category_selection'
            
            await update.message.reply_text(
                f"📝 **משימה:** {text}\n\n"
                "📂 **בחר קטגוריה:**",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        elif state == 'waiting_category_name':
            # הוספת קטגוריה חדשה
            if self.add_category(user_id, text):
                del self.user_states[user_id]
                await update.message.reply_text(
                    f"✅ **הקטגוריה '{text}' נוספה בהצלחה!**\n\n"
                    "עכשיו תוכל להשתמש בה בעת הוספת משימות חדשות.",
                    parse_mode='Markdown'
                )
            else:
                await update.message.reply_text(
                    f"❌ **שגיאה:** הקטגוריה '{text}' כבר קיימת.\n"
                    "אנא בחר שם אחר."
                )

    async def handle_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בבחירת קטגוריה למשימה חדשה"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        if query.data.startswith('select_category_'):
            category = query.data.replace('select_category_', '')
            
            if user_id in self.pending_tasks:
                content = self.pending_tasks[user_id]['content']
                task_id = self.add_task(user_id, content, category)
                
                # ניקוי זמני
                del self.pending_tasks[user_id]
                del self.user_states[user_id]
                
                await query.edit_message_text(
                    f"✅ **המשימה נוספה בהצלחה!**\n\n"
                    f"📝 **משימה:** {content}\n"
                    f"📂 **קטגוריה:** {category}\n"
                    f"🆔 **מזהה:** #{task_id}",
                    parse_mode='Markdown'
                )

    async def daily_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """תזכורת יומית - רק לדוגמה, צריך להגדיר את ה-user_id"""
        # כאן תצטרך להוסיף לוגיקה לשליחה לכל המשתמשים הרשומים
        # לעת עתה זה רק דוגמה למשתמש אחד
        user_id = 123456789  # החלף למזהה המשתמש שלך
        
        summary = self.get_task_summary(user_id)
        
        if summary:
            message = "🌅 **בוקר טוב!**\n\n"
            message += "📊 **סיכום המשימות הפתוחות שלך:**\n\n"
            
            total_tasks = 0
            for category, count in summary.items():
                categories = self.get_user_categories(user_id)
                emoji = '📂'
                for cat_name, cat_emoji in categories:
                    if cat_name == category:
                        emoji = cat_emoji
                        break
                
                message += f"{emoji} {category}: {count} משימות\n"
                total_tasks += count
            
            message += f"\n💪 **בואו נתקדם היום! סך הכל {total_tasks} משימות מחכות לך.**"
            
            await context.bot.send_message(chat_id=user_id, text=message, parse_mode='Markdown')

    def setup_handlers(self):
        """הגדרת הטיפול בפקודות"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("add", self.add_command))
        self.application.add_handler(CommandHandler("list", self.list_command))
        self.application.add_handler(CommandHandler("categories", self.categories_command))
        self.application.add_handler(CommandHandler("summary", self.summary_command))
        
        self.application.add_handler(CallbackQueryHandler(
            self.handle_category_selection, 
            pattern=r'^select_category_'
        ))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_message
        ))
        
        # הגדרת תזכורת יומית לשעה 9:00
        job_queue = self.application.job_queue
        job_queue.run_daily(
            self.daily_reminder,
            time=time(hour=9, minute=0, tzinfo=TIMEZONE),
            name='daily_reminder'
        )

    def run(self):
        """הרצת הבוט"""
        self.init_database()
        self.setup_handlers()
        
        print("🤖 הבוט מתחיל לפעול...")
        print("📱 לחץ Ctrl+C כדי לעצור")
        
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """פונקציה ראשית"""
    # קריאת הטוקן ממשתנה סביבה או קובץ
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ שגיאה: לא נמצא טוקן בוט!")
        print("💡 הוסף את הטוקן כמשתנה סביבה:")
        print("   export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        print("או ערוך את הקוד והוסף את הטוקן ישירות.")
        return
    
    bot = TodoBot(token)
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\n🛑 הבוט הופסק על ידי המשתמש")
    except Exception as e:
        print(f"❌ שגיאה: {e}")

if __name__ == '__main__':
    main()