#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
תכונות מתקדמות לבוט ניהול המשימות
"""

import sqlite3
import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import seaborn as sns

class EnhancedTodoBot:
    """תכונות מתקדמות לבוט המשימות"""
    
    def __init__(self, db_name: str = 'todo_tasks.db'):
        self.db_name = db_name
        
    def init_enhanced_database(self):
        """יצירת טבלאות מתקדמות"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # טבלת סטטיסטיקות יומיות
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                tasks_created INTEGER DEFAULT 0,
                tasks_completed INTEGER DEFAULT 0,
                tasks_deleted INTEGER DEFAULT 0,
                productivity_score REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            )
        ''')
        
        # טבלת הגדרות משתמש
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY,
                reminder_time TEXT DEFAULT '09:00',
                timezone TEXT DEFAULT 'Asia/Jerusalem',
                notifications_enabled BOOLEAN DEFAULT TRUE,
                preferred_language TEXT DEFAULT 'he',
                theme_color TEXT DEFAULT 'blue',
                daily_goal INTEGER DEFAULT 3,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # טבלת תגיות למשימות
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                tag_name TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE CASCADE,
                UNIQUE(task_id, tag_name)
            )
        ''')
        
        # טבלת משימות חוזרות
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recurring_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                category TEXT DEFAULT 'כללי',
                frequency TEXT NOT NULL, -- daily, weekly, monthly
                next_due_date TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_user_activity(self, user_id: int, activity_type: str):
        """רישום פעילות משתמש לסטטיסטיקות"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # יצירת רשומה אם לא קיימת
        cursor.execute('''
            INSERT OR IGNORE INTO daily_stats (user_id, date) 
            VALUES (?, ?)
        ''', (user_id, today))
        
        # עדכון הסטטיסטיקה המתאימה
        if activity_type == 'task_created':
            cursor.execute('''
                UPDATE daily_stats 
                SET tasks_created = tasks_created + 1 
                WHERE user_id = ? AND date = ?
            ''', (user_id, today))
        elif activity_type == 'task_completed':
            cursor.execute('''
                UPDATE daily_stats 
                SET tasks_completed = tasks_completed + 1 
                WHERE user_id = ? AND date = ?
            ''', (user_id, today))
        elif activity_type == 'task_deleted':
            cursor.execute('''
                UPDATE daily_stats 
                SET tasks_deleted = tasks_deleted + 1 
                WHERE user_id = ? AND date = ?
            ''', (user_id, today))
        
        # חישוב ציון פרודוקטיביות
        cursor.execute('''
            SELECT tasks_created, tasks_completed, tasks_deleted 
            FROM daily_stats 
            WHERE user_id = ? AND date = ?
        ''', (user_id, today))
        
        result = cursor.fetchone()
        if result:
            created, completed, deleted = result
            # פורמולה פשוטה לציון פרודוקטיביות
            productivity = (completed * 2) + created - (deleted * 0.5)
            productivity = max(0, productivity)  # לא יכול להיות שלילי
            
            cursor.execute('''
                UPDATE daily_stats 
                SET productivity_score = ? 
                WHERE user_id = ? AND date = ?
            ''', (productivity, user_id, today))
        
        conn.commit()
        conn.close()
    
    def get_user_statistics(self, user_id: int, days: int = 30) -> Dict:
        """קבלת סטטיסטיקות משתמש"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        cursor.execute('''
            SELECT 
                SUM(tasks_created) as total_created,
                SUM(tasks_completed) as total_completed,
                SUM(tasks_deleted) as total_deleted,
                AVG(productivity_score) as avg_productivity,
                COUNT(DISTINCT date) as active_days
            FROM daily_stats 
            WHERE user_id = ? AND date >= ? AND date <= ?
        ''', (user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        result = cursor.fetchone()
        
        # סטטיסטיקות נוכחיות
        cursor.execute('''
            SELECT COUNT(*) as open_tasks
            FROM tasks 
            WHERE user_id = ? AND status = 'open'
        ''', (user_id,))
        
        open_tasks = cursor.fetchone()[0]
        
        # סטטיסטיקות לפי קטגוריה
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM tasks 
            WHERE user_id = ? AND status = 'done'
            GROUP BY category
            ORDER BY count DESC
            LIMIT 5
        ''', (user_id,))
        
        top_categories = cursor.fetchall()
        
        conn.close()
        
        stats = {
            'total_created': result[0] or 0,
            'total_completed': result[1] or 0,
            'total_deleted': result[2] or 0,
            'avg_productivity': result[3] or 0,
            'active_days': result[4] or 0,
            'open_tasks': open_tasks,
            'top_categories': top_categories,
            'completion_rate': (result[1] / result[0] * 100) if result[0] and result[0] > 0 else 0
        }
        
        return stats
    
    def create_productivity_chart(self, user_id: int, days: int = 14) -> BytesIO:
        """יצירת גרף פרודוקטיביות"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        cursor.execute('''
            SELECT date, tasks_created, tasks_completed, productivity_score
            FROM daily_stats 
            WHERE user_id = ? AND date >= ? AND date <= ?
            ORDER BY date
        ''', (user_id, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
        
        data = cursor.fetchall()
        conn.close()
        
        if not data:
            return None
        
        # הכנת הגרף
        plt.style.use('seaborn-v0_8')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle('📊 הסטטיסטיקות שלך', fontsize=16, fontweight='bold')
        
        dates = [datetime.strptime(row[0], '%Y-%m-%d') for row in data]
        created = [row[1] for row in data]
        completed = [row[2] for row in data]
        productivity = [row[3] for row in data]
        
        # גרף עליון - משימות שנוצרו ובוצעו
        ax1.plot(dates, created, marker='o', label='משימות שנוצרו', color='skyblue', linewidth=2)
        ax1.plot(dates, completed, marker='s', label='משימות שבוצעו', color='lightgreen', linewidth=2)
        ax1.set_title('פעילות יומית', fontweight='bold')
        ax1.set_ylabel('מספר משימות')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # גרף תחתון - ציון פרודוקטיביות
        ax2.bar(dates, productivity, color='orange', alpha=0.7, label='ציון פרודוקטיביות')
        ax2.set_title('ציון פrודoקטיביות יומי', fontweight='bold')
        ax2.set_ylabel('ציון')
        ax2.set_xlabel('תאריך')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # עיצוב התאריכים
        for ax in [ax1, ax2]:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # שמירה לזיכרון
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='PNG', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer
    
    def get_motivational_message(self, user_id: int) -> str:
        """יצירת הודעת מוטיבציה מותאמת אישית"""
        stats = self.get_user_statistics(user_id, days=7)
        
        completed = stats['total_completed']
        completion_rate = stats['completion_rate']
        
        if completed == 0:
            return "🌟 בואו נתחיל! אין כמו ההתחלה של משימה ראשונה!"
        
        if completion_rate >= 80:
            return f"🔥 אלוף! השלמת {completed} משימות השבוע עם {completion_rate:.0f}% הצלחה!"
        elif completion_rate >= 60:
            return f"💪 עבודה טובה! השלמת {completed} משימות השבוע. עוד קצת ונגיע ל-80%!"
        elif completion_rate >= 40:
            return f"📈 בדרך הנכונה! השלמת {completed} משימות. בואו נתמקד היום!"
        else:
            return f"🎯 בואו נתחיל מחדש! השבוע נוכל להשיג יותר מ-{completed} משימות!"

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """הצגת סטטיסטיקות מתקדמות"""
        user_id = update.effective_user.id
        stats = self.get_user_statistics(user_id)
        
        message = f"""
📊 **הסטטיסטיקות שלך (30 ימים אחרונים)**

📈 **פעילות כללית:**
• משימות שנוצרו: {stats['total_created']}
• משימות שבוצעו: {stats['total_completed']}
• משימות פתוחות: {stats['open_tasks']}
• אחוז השלמה: {stats['completion_rate']:.1f}%

🎯 **ציון פרודוקטיביות ממוצע:** {stats['avg_productivity']:.1f}
📅 **ימי פעילות:** {stats['active_days']} מתוך 30

🏆 **הקטגוריות המובילות:**
"""
        
        for i, (category, count) in enumerate(stats['top_categories'][:3], 1):
            if i == 1:
                medal = "🥇"
            elif i == 2:
                medal = "🥈"
            else:
                medal = "🥉"
            message += f"{medal} {category}: {count} משימות\n"
        
        # הוספת הודעת מוטיבציה
        motivation = self.get_motivational_message(user_id)
        message += f"\n💪 **המוטיבציה שלך:** {motivation}"
        
        keyboard = [
            [InlineKeyboardButton("📊 גרף פרודוקטיביות", callback_data="show_chart")],
            [InlineKeyboardButton("⚙️ הגדרות", callback_data="user_settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

    async def show_productivity_chart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """הצגת גרף פרודוקטיביות"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        
        try:
            chart_buffer = self.create_productivity_chart(user_id)
            
            if chart_buffer:
                await query.message.reply_photo(
                    photo=chart_buffer,
                    caption="📊 **הגרף שלך מוכן!**\n\nכאן תוכל לראות את ההתקדמות שלך בשבועיים האחרונים."
                )
            else:
                await query.edit_message_text("📊 אין מספיק נתונים ליצירת גרף. המשך לעבוד ובקרוב יהיה לך גרף מרשים!")
                
        except Exception as e:
            await query.edit_message_text("❌ שגיאה ביצירת הגרף. אנא נסה שוב מאוחר יותר.")

    def add_task_with_tags(self, user_id: int, content: str, category: str, tags: List[str] = None):
        """הוספת משימה עם תגיות"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # הוספת המשימה
        cursor.execute('''
            INSERT INTO tasks (user_id, content, category) 
            VALUES (?, ?, ?)
        ''', (user_id, content, category))
        
        task_id = cursor.lastrowid
        
        # הוספת תגיות אם יש
        if tags:
            for tag in tags:
                tag = tag.strip().lower()
                if tag:
                    cursor.execute('''
                        INSERT OR IGNORE INTO task_tags (task_id, tag_name) 
                        VALUES (?, ?)
                    ''', (task_id, tag))
        
        conn.commit()
        conn.close()
        
        # רישום פעילות
        self.record_user_activity(user_id, 'task_created')
        
        return task_id

    def search_tasks(self, user_id: int, query: str) -> List[tuple]:
        """חיפוש משימות לפי תוכן או תגיות"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT DISTINCT t.id, t.content, t.category, t.created_at
            FROM tasks t
            LEFT JOIN task_tags tt ON t.id = tt.task_id
            WHERE t.user_id = ? 
            AND t.status = 'open'
            AND (
                t.content LIKE ? 
                OR t.category LIKE ?
                OR tt.tag_name LIKE ?
            )
            ORDER BY t.created_at DESC
        ''', (user_id, f'%{query}%', f'%{query}%', f'%{query}%'))
        
        results = cursor.fetchall()
        conn.close()
        
        return results

    async def backup_user_data(self, user_id: int) -> str:
        """יצירת גיבוי של נתוני המשתמש"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # קבלת כל הנתונים של המשתמש
        cursor.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,))
        tasks = cursor.fetchall()
        
        cursor.execute('SELECT * FROM categories WHERE user_id = ?', (user_id,))
        categories = cursor.fetchall()
        
        cursor.execute('SELECT * FROM daily_stats WHERE user_id = ?', (user_id,))
        stats = cursor.fetchall()
        
        conn.close()
        
        backup_data = {
            'user_id': user_id,
            'backup_date': datetime.now().isoformat(),
            'tasks': tasks,
            'categories': categories,
            'stats': stats
        }
        
        # שמירת הגיבוי לקובץ
        backup_filename = f'backup_user_{user_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)
        
        return backup_filename