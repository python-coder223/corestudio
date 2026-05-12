# CoreStudio — Flask versiya

Minecraft mod va plugin platformasi. React/Supabase loyihasining Flask + HTML/CSS/JS ko'chirması.

## Ishga tushirish

```bash
# 1. Virtual muhit yaratish
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Kutubxonalarni o'rnatish
pip install -r requirements.txt

# 3. Dasturni ishga tushirish
python app.py
```

Brauzerda oching: http://localhost:5000

## Admin panel

URL: http://localhost:5000/admin  
Parol: `admin123`

> `app.py` ichida `ADMIN_PASSWORD` ni o'zgartiring!

## Struktura

```
corestudio/
├── app.py                  # Flask app, routes, SQLAlchemy model
├── requirements.txt
├── uploads/
│   ├── files/              # .jar, .zip fayllar
│   └── images/             # Loyiha rasmlari
└── templates/
    ├── base.html           # Header, footer, Tailwind CDN
    ├── index.html          # Bosh sahifa (hero, stats, cards)
    ├── list.html           # Modlar / Pluginlar ro'yxati
    ├── project.html        # Loyiha detail sahifasi
    ├── admin.html          # Admin login + dashboard
    └── partials/
        └── project_card.html  # Qayta ishlatiladigan karta
```

## Ma'lumotlar bazasi

SQLite (`corestudio.db`) — birinchi ishga tushirilganda avtomatik yaratiladi.

| Ustun        | Tur     | Tavsif                        |
|-------------|---------|-------------------------------|
| id          | UUID    | Birlamchi kalit               |
| name        | TEXT    | Loyiha nomi                   |
| type        | TEXT    | `mod` yoki `plugin`           |
| description | TEXT    | Tavsif                        |
| version     | TEXT    | Versiya (masalan: 1.0.0)      |
| mc_version  | TEXT    | Minecraft versiyasi           |
| loader      | TEXT    | Forge, Fabric, Spigot...      |
| author      | TEXT    | Muallif                       |
| downloads   | INTEGER | Yuklab olishlar soni          |
| file_url    | TEXT    | Fayl URL (local yoki tashqi)  |
| image_url   | TEXT    | Rasm URL                      |
| created_at  | DATETIME| Yaratilgan vaqt               |
