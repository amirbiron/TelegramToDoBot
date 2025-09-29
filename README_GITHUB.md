# 🤖 בוט טלגרם לניהול משימות - Todo Bot

> **בוט מתקדם לניהול משימות בטלגרם עם ממשק נוח, קטגוריות מותאמות אישית ותזכורות יומיות**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Telegram Bot API](https://img.shields.io/badge/Bot%20API-7.0+-blue.svg)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Deploy to Render](https://img.shields.io/badge/Deploy-Render-purple.svg)](https://render.com)

## ✨ תכונות עיקריות

### 📝 **ניהול משימות חכם**
- ✅ הוספת משימות עם קטגוriות מותאמות אישית
- 🗂️ ארגון לפי קטגוריות: עבודה, לימודים, אישי וכו'
- ⚡ ממשק נוח עם כפתורים מהירים
- 🔍 חיפוש משימות מתקדם
- 📊 מעקב אחר התקדמות

### 🎯 **תכונות מתקדמות**
- 📈 סטטיסטיקות אישיות עם גרפים
- 🔔 תזכורות יומיות חכמות (9:00 בבוקר)
- 💾 גיבוי אוטומטי של נתונים
- 🏷️ תגיות אוטומטיות (#חשוב #דחוף)
- 🎮 מערכת מוטיבציה והישגים

## 🚀 התקנה מהירה

### אפשרות 1: פריסה ב-Render (מומלץ - חינמי!)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. **לחץ על הכפתור למעלה**
2. **הוסף את הטוקן** של הבוט ממשתנה הסביבה `TELEGRAM_BOT_TOKEN`
3. **המתן לבנייה** (2-3 דקות)
4. **הבוט מוכן!** 🎉

### אפשרות 2: הרצה מקומית

```bash
# שכפל את הפרויקט
git clone https://github.com/YOUR_USERNAME/telegram-todo-bot.git
cd telegram-todo-bot

# התקן ספריות
pip install -r requirements.txt

# הגדר טוקן
export TELEGRAM_BOT_TOKEN="your_bot_token_here"

# הרץ את הבוט
python main.py
```

## 📱 כיצד להשיג טוקן בוט

1. שלח הודעה ל-[@BotFather](https://t.me/botfather) בטלגרם
2. שלח `/newbot` ובחר שם לבוט שלך
3. העתק את הטוקן שתקבל
4. השתמש בו במשתנה הסביבה `TELEGRAM_BOT_TOKEN`

## 💻 פקודות הבוט

| פקודה | תיאור | דוגמה |
|-------|--------|--------|
| `/start` | התחלת העבודה והדרכה | `/start` |
| `/add` | הוספת משימה חדשה | `/add` |
| `/list` | הצגת משימות לפי קטגוריה | `/list` |
| `/categories` | ניהול קטגוריות | `/categories` |
| `/summary` | סיכום משימות פתוחות | `/summary` |
| `/stats` | סטטיסטיקות מתקדמות | `/stats` |
| `/search [מילה]` | חיפוש במשימות | `/search דוח` |
| `/backup` | יצירת גיבוי נתונים | `/backup` |

## 🎯 דוגמאות שימוש

### הוספת משימה עם תגיות
```
👤 שלח: לסיים פרויקט האתר #דחוף #עבודה
🤖 הבוט יזהה אוטומטית את התגיות ויארגן את המשימה
```

### תזכורת יומית אוטומטית
```
🌅 בוקר טוב!

📊 סיכום המשימות הפתוחות שלך:
💼 עבודה: 3 משימות
📚 לימודים: 1 משימות
🏠 אישי: 2 משימות

💪 בואו נתקדם היום! סך הכל 6 משימות מחכות לך.
```

## 🏗️ ארכיטקטורה טכנית

### מבנה הפרויקט
```
telegram_todo_bot/
├── main.py                 # בוט ראשי עם כל התכונות הבסיסיות
├── render_main.py         # גרסה מותאמת לפריסה ב-Render
├── enhanced_features.py   # תכונות מתקדמות (סטטיסטיקות, גרפים)
├── config.py             # הגדרות מרכזיות
├── schema.sql            # מבנה מסד הנתונים
├── requirements.txt      # ספריות לפיתוח מלא
├── requirements_render.txt # ספריות מינימליות לפריסה
└── docs/                 # תיעוד מפורט
```

### מסד נתונים
- **SQLite** - קל ויעיל לבוטי טלגרם
- **טבלת משימות** - עם סטטוס, קטגוריה ותאריכים
- **טבלת קטגוריות** - מותאמות אישית עם אימוג'ים
- **טבלת סטטיסטיקות** - למעקב ביצועים

## 📊 תכונות מתקדמות

### סטטיסטיקות וגרפים
- גרפי פרודוקטיביות אישיים
- מעקב אחר הרגלי עבודה
- ציון פרודוקטיביות יומי
- דוחות מפורטים לפי קטגוריה

### מערכת גיבויים
- גיבוי אוטומטי בפקודה אחת
- ייצוא נתונים לקבצי JSON
- שחזור נתונים מגיבויים

### חיפוש מתקדם
- חיפוש לפי תוכן משימה
- חיפוש לפי תגיות (#tag)
- חיפוש לפי קטגוריה
- תוצאות מדורגות לפי רלוונטיות

## 🔧 התאמות אישיות

### שינוי שעת התזכורת
```python
# בקובץ config.py
DAILY_REMINDER_TIME = time(hour=8, minute=30)  # 8:30 בבוקר
```

### הוספת קטגוריות ברירת מחדל
```python
DEFAULT_CATEGORIES = [
    ('עבודה', '💼'),
    ('לימודים', '📚'), 
    ('בריאות', '🏥'),    # קטגוריה חדשה
    ('קניות', '🛒'),     # קטגוריה חדשה
]
```

## 🌟 תכנון עתידי

- 🌐 **ממשק ווב** - צפייה ועריכה דרך דפדפן
- 🔄 **סנכרון ענן** - גיבוי אוטומטי ל-Google Drive
- 🤝 **תכונות צוותיות** - שיתוף משימות עם חברים
- 🧠 **בינה מלאכותית** - חיזוי זמני השלמה
- 📱 **אפליקציה** - PWA לטלפונים חכמים
- 🔗 **אינטגרציות** - Google Calendar, Trello, Notion

## 🤝 תרומה לפרויקט

נשמח לקבל תרומות! אנא:

1. **Fork** את הפרויקט
2. צור **branch** חדש (`git checkout -b feature/AmazingFeature`)
3. **Commit** את השינויים (`git commit -m 'Add AmazingFeature'`)
4. **Push** ל-branch (`git push origin feature/AmazingFeature`)
5. פתח **Pull Request**

### רעיונות לתרומה
- 🌍 תרגום לשפות נוספות
- 🎨 שיפור עיצוב ההודעות
- 📊 גרפים וסטטיסטיקות נוספות
- 🔌 אינטגרציות עם שירותים חיצוניים
- 🧪 בדיקות אוטומטיות

## 📄 רישיון

פרויקט זה מוגש תחת רישיון MIT - ראה קובץ [LICENSE](LICENSE) לפרטים.

## 🆘 תמיכה ועזרה

### תיעוד מפורט
- 📖 [מדריך שימוש מלא](USAGE_EXAMPLES.md)
- 🚀 [הרצה ב-Render](RENDER_DEPLOYMENT.md)
- 💡 [רעיונות לשיפור](UPGRADE_SUGGESTIONS.md)
- 📋 [סיכום הפרויקט](PROJECT_SUMMARY.md)

### דרכי קשר
- 🐛 **באגים:** פתח Issue ב-GitHub
- 💡 **רעיונות:** Discussions או Pull Request
- ❓ **שאלות:** בדוק קודם את התיעוד

## 🏆 אודות הפרויקט

פרויקט זה נוצר על ידי כותב תוכן טכנולוגי המתמחה בחדשות אנדרואיד ובינה מלאכותית. 
המטרה: ליצור כלי פרודוקטיביות מעשי ונגיש לקהל הישראלי.

**תכונות ייחודיות:**
- 🇮🇱 ממשק מלא בעברית
- ⏰ אזור זמן ישראלי
- 🎯 התמקדות בפשטות ויעילות
- 📚 תיעוד מקיף ברמה מקצועית

---

<div align="center">

**⭐ אם הפרויקט עזר לך, אנא תן כוכב ושתף עם חברים! ⭐**

[![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/telegram-todo-bot.svg?style=social)](https://github.com/YOUR_USERNAME/telegram-todo-bot/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/telegram-todo-bot.svg?style=social)](https://github.com/YOUR_USERNAME/telegram-todo-bot/network/members)

**עשוי בישראל 🇮🇱 עם ❤️ ו-☕**

</div>