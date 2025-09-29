#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
סקריפט גיבוי לפני פריסה ב-Render
"""

import os
import shutil
import zipfile
from datetime import datetime
import json

def create_deployment_backup():
    """יצירת גיבוי מלא לפני פריסה"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"telegram_bot_backup_{timestamp}"
    
    print("📦 יוצר גיבוי לפני פריסה ב-Render...")
    
    # רשימת קבצים חשובים
    important_files = [
        'main.py',
        'render_main.py', 
        'requirements_render.txt',
        'requirements.txt',
        'schema.sql',
        'config.py',
        'enhanced_features.py',
        'run_bot.py',
        '.env.example',
        'README.md',
        'RENDER_DEPLOYMENT.md',
        'USAGE_EXAMPLES.md',
        'UPGRADE_SUGGESTIONS.md',
        'PROJECT_SUMMARY.md'
    ]
    
    # יצירת תיקיית גיבוי
    backup_dir = f"backups/{backup_name}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # העתקת קבצים
    copied_files = []
    for file in important_files:
        if os.path.exists(file):
            shutil.copy2(file, backup_dir)
            copied_files.append(file)
            print(f"✅ {file}")
        else:
            print(f"⚠️  {file} - לא נמצא")
    
    # יצירת מידע על הגיבוי
    backup_info = {
        "timestamp": timestamp,
        "backup_name": backup_name,
        "files_count": len(copied_files),
        "files": copied_files,
        "notes": "גיבוי לפני פריסה ב-Render"
    }
    
    with open(f"{backup_dir}/backup_info.json", 'w', encoding='utf-8') as f:
        json.dump(backup_info, f, ensure_ascii=False, indent=2)
    
    # יצירת קובץ ZIP
    zip_path = f"backups/{backup_name}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(backup_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, backup_dir)
                zipf.write(file_path, arcname)
    
    # מחיקת תיקיית העבודה
    shutil.rmtree(backup_dir)
    
    print(f"\n🎯 גיבוי הושלם בהצלחה!")
    print(f"📁 קובץ: {zip_path}")
    print(f"📊 קבצים: {len(copied_files)}")
    print(f"📅 תאריך: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    return zip_path

def create_render_checklist():
    """יצירת רשימת בדיקות לפני פריסה"""
    
    checklist = """
📋 רשימת בדיקות לפני פריסה ב-Render:

🔧 הכנה:
□ יצרתי repository ב-GitHub
□ העליתי את כל הקבצים
□ קיבלתי טוקן מ-@BotFather
□ בדקתי שהבוט עובד מקומית

🌐 Render:
□ נרשמתי ל-Render.com
□ יצרתי Web Service חדש
□ חיברתי את ה-GitHub repository
□ הגדרתי Build Command: pip install -r requirements_render.txt
□ הגדרתי Start Command: python render_main.py
□ הוספתי TELEGRAM_BOT_TOKEN למשתני הסביבה

✅ בדיקה סופית:
□ הבוט עובד בטלגרם
□ הלוגים ב-Render נראים תקינים
□ פקודת /start עובדת
□ פקודת /add עובדת
□ הנתונים נשמרים

🚀 מוכן לשימוש!
    """
    
    with open('render_checklist.txt', 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print("\n📋 נוצרה רשימת בדיקות: render_checklist.txt")

if __name__ == '__main__':
    print("🚀 הכנה לפריסה ב-Render\n")
    
    # יצירת גיבוי
    backup_path = create_deployment_backup()
    
    # יצירת רשימת בדיקות
    create_render_checklist()
    
    print("\n" + "="*50)
    print("🎯 השלבים הבאים:")
    print("1. העלה את הקבצים ל-GitHub")
    print("2. כנס ל-Render.com ויצור Web Service")
    print("3. עקוב אחר הוראות ב-RENDER_DEPLOYMENT.md")
    print("4. בדוק את רשימת הבדיקות ב-render_checklist.txt")
    print("="*50)
    print("🍀 בהצלחה! 🚀")