#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
קובץ הגדרות עבור בוט טלגרם לניהול משימות
"""

import os
import pytz
from datetime import time

class Config:
    """הגדרות בוט"""
    
    # הגדרות בסיסיות
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    DATABASE_NAME = 'todo_tasks.db'
    
    # הגדרות זמן ואזור
    TIMEZONE = pytz.timezone('Asia/Jerusalem')
    DAILY_REMINDER_TIME = time(hour=9, minute=0)  # 9:00 בבוקר
    
    # הגדרות הודעות
    MAX_TASK_LENGTH = 500  # אורך מקסימלי למשימה
    MAX_CATEGORY_LENGTH = 50  # אורך מקסימלי לשם קטגוריה
    MAX_TASKS_PER_PAGE = 10  # מספר משימות בעמוד
    
    # קטגוריות ברירת מחדל
    DEFAULT_CATEGORIES = [
        ('עבודה', '💼'),
        ('לימודים', '📚'),
        ('אישי', '🏠'),
        ('כללי', '➕'),
        ('בריאות', '🏥'),
        ('קניות', '🛒'),
        ('נסיעות', '✈️'),
        ('חברים', '👥'),
    ]
    
    # הגדרות לוגים
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # הודעות המערכת
    class Messages:
        WELCOME = """
🤖 **ברוך הבא לבוט ניהול המשימות המתקדם!**

📝 **פקודות זמינות:**
• `/add` - הוספת משימה חדשה
• `/list` - הצגת משימות לפי קטגוריה
• `/categories` - ניהול קטגוריות
• `/summary` - סיכום משימות פתוחות
• `/stats` - סטטיסטיקות אישיות
• `/settings` - הגדרות אישיות

💡 **טיפים:**
• השתמש בכפתורים המהירים לניווט קל
• הוסף קטגוריות מותאמות אישית
• קבל תזכורות יומיות לניהול יעיל

בואו נתחיל לנהל את המשימות שלך ביעילות! 🚀
        """
        
        NO_TASKS = """
🎉 **מעולה!**

אין לך משימות פתוחות כרגע.
זמן טוב להוסיף משימות חדשות! 📝

השתמש ב-/add כדי להתחיל.
        """
        
        TASK_ADDED = "✅ **המשימה נוספה בהצלחה!**"
        TASK_COMPLETED = "🎉 **כל הכבוד! המשימה הושלמה!**"
        TASK_DELETED = "🗑 **המשימה נמחקה בהצלחה!**"
        
        CATEGORY_ADDED = "✅ **הקטגוריה נוספה בהצלחה!**"
        CATEGORY_EXISTS = "❌ **שגיאה:** הקטגוריה כבר קיימת."
        
        DAILY_REMINDER_TITLE = "🌅 **בוקר טוב!**"
        DAILY_REMINDER_MOTIVATION = "💪 **בואו נתקדם היום!**"
        
        ERROR_GENERAL = "❌ **אירעה שגיאה.** אנא נסה שוב."
        ERROR_TASK_NOT_FOUND = "❌ **המשימה לא נמצאה.**"
        ERROR_INVALID_INPUT = "❌ **קלט לא תקין.** אנא נסה שוב."
        
        HELP_ADD_TASK = "📝 **הוספת משימה חדשה**\n\nאנא כתוב את תוכן המשימה:"
        HELP_SELECT_CATEGORY = "📂 **בחר קטגוריה למשימה:**"
        HELP_ADD_CATEGORY = "📂 **הוספת קטגוריה חדשה**\n\nאנא כתוב את שם הקטגוריה החדשה:"
    
    # הגדרות מתקדמות
    class Advanced:
        # הפעלת תכונות נוספות
        ENABLE_STATISTICS = True
        ENABLE_REMINDERS = True
        ENABLE_CATEGORIES_EMOJI = True
        ENABLE_TASK_PRIORITIES = False  # לעתיד
        ENABLE_DUE_DATES = False  # לעתיד
        ENABLE_RECURRING_TASKS = False  # לעתיד
        
        # הגדרות ביצועים
        DATABASE_TIMEOUT = 30  # שניות
        MAX_CONCURRENT_USERS = 100
        CACHE_TIMEOUT = 300  # 5 דקות
        
        # הגדרות אבטחה
        RATE_LIMIT_PER_MINUTE = 30  # מספר בקשות מקסימלי לדקה למשתמש
        ADMIN_USER_IDS = []  # רשימת מזהי מנהלים
        
        # הגדרות גיבוי
        BACKUP_ENABLED = True
        BACKUP_INTERVAL_HOURS = 24
        BACKUP_KEEP_DAYS = 7

    @classmethod
    def validate(cls):
        """בדיקת תקינות הגדרות"""
        errors = []
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        
        if cls.MAX_TASK_LENGTH <= 0:
            errors.append("MAX_TASK_LENGTH must be positive")
        
        if cls.MAX_CATEGORY_LENGTH <= 0:
            errors.append("MAX_CATEGORY_LENGTH must be positive")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True

    @classmethod
    def get_user_timezone(cls, user_id: int):
        """קבלת אזור זמן של משתמש (לעתיד - כרגע מחזיר ברירת מחדל)"""
        # בעתיד ניתן לשמור הגדרות משתמש במסד נתונים
        return cls.TIMEZONE

# הגדרות לסביבות שונות
class DevelopmentConfig(Config):
    """הגדרות לסביבת פיתוח"""
    LOG_LEVEL = 'DEBUG'
    DATABASE_NAME = 'todo_tasks_dev.db'

class ProductionConfig(Config):
    """הגדרות לסביבת ייצור"""
    LOG_LEVEL = 'WARNING'
    DATABASE_NAME = 'todo_tasks_prod.db'

class TestingConfig(Config):
    """הגדרות לבדיקות"""
    LOG_LEVEL = 'ERROR'
    DATABASE_NAME = ':memory:'  # מסד נתונים זמני בזיכרון
    class Advanced(Config.Advanced):
        ENABLE_REMINDERS = False

# בחירת הגדרות לפי משתנה סביבה
ENV = os.getenv('BOT_ENV', 'development').lower()

if ENV == 'production':
    config = ProductionConfig
elif ENV == 'testing':
    config = TestingConfig
else:
    config = DevelopmentConfig

# ייצוא ההגדרות הנוכחיות
__all__ = ['config']
