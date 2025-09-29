-- סכמת מסד נתונים עבור בוט טלגרם לניהול משימות
-- מסד נתונים: SQLite

-- טבלת משימות
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,          -- מזהה ייחודי
    user_id INTEGER NOT NULL,                      -- מזהה משתמש טלגרם
    content TEXT NOT NULL,                         -- תוכן המשימה
    status TEXT DEFAULT 'open',                    -- סטטוס: open/done
    category TEXT DEFAULT 'כללי',                  -- קטגוריה
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- תאריך יצירה
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- תאריך עדכון אחרון
    
    -- אינדקסים לביצועים טובים יותר
    INDEX idx_tasks_user_status (user_id, status),
    INDEX idx_tasks_user_category (user_id, category),
    INDEX idx_tasks_created_at (created_at)
);

-- טבלת קטגוריות
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,          -- מזהה ייחודי
    user_id INTEGER NOT NULL,                      -- מזהה משתמש (0 = קטגוריות ברירת מחדל)
    name TEXT NOT NULL,                            -- שם הקטגוריה
    emoji TEXT DEFAULT '📂',                       -- אימוג'י לקטגוריה
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- תאריך יצירה
    
    -- מניעת כפילות של קטגוריות לאותו משתמש
    UNIQUE(user_id, name),
    
    -- אינדקס לחיפוש מהיר
    INDEX idx_categories_user (user_id)
);

-- הכנסת קטגוריות ברירת מחדל (user_id = 0 = זמין לכולם)
INSERT OR IGNORE INTO categories (user_id, name, emoji) VALUES 
(0, 'עבודה', '💼'),
(0, 'לימודים', '📚'),
(0, 'אישי', '🏠'),
(0, 'כללי', '➕');

-- טבלת הגדרות משתמש (אופציונלי - לעתיד)
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY,                   -- מזהה משתמש טלגרם
    timezone TEXT DEFAULT 'Asia/Jerusalem',        -- אזור זמן
    reminder_time TEXT DEFAULT '09:00',            -- שעת תזכורת יומית
    language TEXT DEFAULT 'he',                    -- שפה
    notifications_enabled BOOLEAN DEFAULT TRUE,    -- הפעלת התראות
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- טבלת סטטיסטיקות (אופציונלי - לעתיד)
CREATE TABLE IF NOT EXISTS task_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,                            -- תאריך (YYYY-MM-DD)
    tasks_created INTEGER DEFAULT 0,               -- משימות שנוצרו
    tasks_completed INTEGER DEFAULT 0,             -- משימות שהושלמו
    tasks_deleted INTEGER DEFAULT 0,               -- משימות שנמחקו
    
    UNIQUE(user_id, date),
    INDEX idx_stats_user_date (user_id, date)
);

-- Views לדוחות ושאילתות נפוצות

-- תצוגה של משימות פעילות עם פרטי קטגוריה
CREATE VIEW IF NOT EXISTS active_tasks_view AS
SELECT 
    t.id,
    t.user_id,
    t.content,
    t.status,
    t.category,
    c.emoji as category_emoji,
    t.created_at,
    t.updated_at
FROM tasks t
LEFT JOIN categories c ON (t.category = c.name AND (c.user_id = t.user_id OR c.user_id = 0))
WHERE t.status = 'open'
ORDER BY t.category, t.created_at DESC;

-- תצוגה של סיכום משימות לפי קטגוריה
CREATE VIEW IF NOT EXISTS task_summary_view AS
SELECT 
    user_id,
    category,
    COUNT(*) as total_tasks,
    SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) as open_tasks,
    SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) as completed_tasks
FROM tasks
GROUP BY user_id, category
ORDER BY user_id, category;

-- טריגרים לעדכון אוטומטי של תאריכים

-- עדכון updated_at בעת שינוי משימה
CREATE TRIGGER IF NOT EXISTS update_task_timestamp 
    AFTER UPDATE ON tasks
BEGIN
    UPDATE tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- עדכון updated_at בעת שינוי הגדרות משתמש
CREATE TRIGGER IF NOT EXISTS update_user_settings_timestamp 
    AFTER UPDATE ON user_settings
BEGIN
    UPDATE user_settings SET updated_at = CURRENT_TIMESTAMP WHERE user_id = NEW.user_id;
END;