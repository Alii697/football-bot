import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8125436332:AAF4WayR1rziUC1HBKsF2prm19DHRlO2zy8"
ADMIN_ID = 8398088226

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    points INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    user_id INTEGER,
    game TEXT,
    choice TEXT
)
""")

conn.commit()

current_game = {"name": None}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚽ Futbol prognoz botiga xush kelibsiz!")

async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    game_name = " ".join(context.args)
    current_game["name"] = game_name

    keyboard = [
        [InlineKeyboardButton("P1 (10)", callback_data="P1"),
         InlineKeyboardButton("X (10)", callback_data="X"),
         InlineKeyboardButton("P2 (10)", callback_data="P2")],
        [InlineKeyboardButton("Over 2.5 (5)", callback_data="OVER"),
         InlineKeyboardButton("Under 2.5 (5)", callback_data="UNDER")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"⚽ {game_name}\n\nNatijani tanlang:",
        reply_markup=reply_markup
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    username = query.from_user.username

    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
                   (user_id, username))

    cursor.execute("INSERT INTO predictions (user_id, game, choice) VALUES (?, ?, ?)",
                   (user_id, current_game["name"], query.data))

    conn.commit()

    await query.edit_message_text("✅ Tanlov qabul qilindi!")

async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    real_result = context.args[0]

    cursor.execute("SELECT user_id, choice FROM predictions WHERE game=?",
                   (current_game["name"],))
    rows = cursor.fetchall()

    for user_id, choice in rows:
        if choice == real_result:
            if choice in ["P1", "X", "P2"]:
                cursor.execute("UPDATE users SET points = points + 10 WHERE user_id=?",
                               (user_id,))
            else:
                cursor.execute("UPDATE users SET points = points + 5 WHERE user_id=?",
                               (user_id,))

    conn.commit()
    await update.message.reply_text("✅ Natija hisoblandi!")

async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT username, points FROM users ORDER BY points DESC L

