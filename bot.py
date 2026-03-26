import os
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен из переменной
TOKEN = os.environ.get("BOT_TOKEN", "")

# Данные аниме для демонстрации (временно, пока не подключим AniList)
POPULAR_ANIME = [
    {"title": "Атака Титанов", "rating": "9.0", "genres": ["Экшен", "Драма"], "year": 2013},
    {"title": "Врата Штейна", "rating": "9.1", "genres": ["Sci-Fi", "Триллер"], "year": 2011},
    {"title": "Магическая битва", "rating": "8.8", "genres": ["Экшен", "Фэнтези"], "year": 2020},
    {"title": "Клинок, рассекающий демонов", "rating": "8.9", "genres": ["Экшен", "Фэнтези"], "year": 2019},
    {"title": "Ванпанчмен", "rating": "8.7", "genres": ["Экшен", "Комедия"], "year": 2015},
]

RATED_ANIME = [
    {"title": "Fullmetal Alchemist: Brotherhood", "rating": "9.2", "genres": ["Экшен", "Приключения"], "year": 2009},
    {"title": "Тетрадь смерти", "rating": "9.0", "genres": ["Триллер", "Детектив"], "year": 2006},
    {"title": "Код Гиас", "rating": "8.9", "genres": ["Экшен", "Драма"], "year": 2006},
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎲 Случайное аниме", callback_data="random")],
        [InlineKeyboardButton("🎭 По жанру", callback_data="genre")],
        [InlineKeyboardButton("🤖 Рекомендация", callback_data="recommend")],
        [InlineKeyboardButton("🔥 Популярные", callback_data="popular")],
        [InlineKeyboardButton("⭐ Топ по рейтингу", callback_data="rated")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌟 Привет! Я аниме-бот!\n\nВыбери действие:",
        reply_markup=reply_markup
    )

async def random_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    anime = random.choice(POPULAR_ANIME)
    text = f"🎲 *Случайное аниме:*\n\n"
    text += f"*{anime['title']}*\n"
    text += f"⭐ Рейтинг: {anime['rating']}\n"
    text += f"🎭 Жанры: {', '.join(anime['genres'])}\n"
    text += f"📅 Год: {anime['year']}"
    
    keyboard = [[InlineKeyboardButton("🎲 Еще", callback_data="random")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def popular_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔥 *Популярные аниме:*\n\n"
    for i, anime in enumerate(POPULAR_ANIME[:3], 1):
        text += f"{i}. *{anime['title']}* - ⭐ {anime['rating']}\n"
    
    keyboard = [[InlineKeyboardButton("🎲 Другое", callback_data="random")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def rated_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "⭐ *Топ по рейтингу:*\n\n"
    for i, anime in enumerate(RATED_ANIME, 1):
        text += f"{i}. *{anime['title']}* - ⭐ {anime['rating']}\n"
        text += f"   🎭 {', '.join(anime['genres'])} | 📅 {anime['year']}\n\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def genre_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    genres = [
        "Экшен", "Приключения", "Комедия", "Драма", 
        "Фэнтези", "Романтика", "Научная фантастика", "Ужасы"
    ]
    
    keyboard = []
    for genre in genres:
        keyboard.append([InlineKeyboardButton(genre, callback_data=f"genre_{genre}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎭 Выбери жанр:", reply_markup=reply_markup)

async def genre_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    genre = query.data.replace("genre_", "")
    
    # Поиск аниме по жанру (временная заглушка)
    anime_list = {
        "Экшен": ["Атака Титанов", "Магическая битва", "Ванпанчмен"],
        "Комедия": ["Ванпанчмен", "Gintama", "Ковбой Бибоп"],
        "Драма": ["Врата Штейна", "Твоё имя", "Тихий голос"],
        "Романтика": ["Твоё имя", "Торадора", "Сакурасо"],
        "Фэнтези": ["Атака Титанов", "Магическая битва", "Врата Штейна"],
        "Научная фантастика": ["Врата Штейна", "Код Гиас", "Евангелион"],
        "Приключения": ["One Piece", "Hunter x Hunter", "Fullmetal Alchemist"],
        "Ужасы": ["Another", "Paranoia Agent", "Тетрадь смерти"]
    }
    
    animes = anime_list.get(genre, ["Нет рекомендаций"])
    anime = random.choice(animes)
    
    text = f"🎭 *Жанр: {genre}*\n\n✨ Рекомендую: *{anime}*"
    
    keyboard = [[InlineKeyboardButton("🎭 Другой жанр", callback_data="genre")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)

async def recommend_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Нейросеть поможет выбрать аниме!*\n\n"
        "Напиши, что ты хочешь посмотреть, например:\n"
        "- Посоветуй аниме про приключения\n"
        "- Что-то похожее на Наруто\n"
        "- Аниме с глубоким сюжетом"
    )
    context.user_data['waiting_for_recommend'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if context.user_data.get('waiting_for_recommend'):
        await update.message.reply_text("🔮 Обрабатываю запрос...")
        
        # Временная заглушка для рекомендаций
        recommendations = [
            "🎯 *Атака Титанов* - эпичное фэнтези о борьбе с гигантами",
            "🎯 *Врата Штейна* - научная фантастика о путешествиях во времени",
            "🎯 *Магическая битва* - динамичный экшен про магию и проклятия"
        ]
        
        response = "🎯 *Рекомендации:*\n\n" + "\n\n".join(recommendations)
        await update.message.reply_text(response, parse_mode='Markdown')
        context.user_data['waiting_for_recommend'] = False
    else:
        await update.message.reply_text(
            "Используй кнопки или команды:\n"
            "/start - главное меню\n"
            "/random - случайное аниме\n"
            "/popular - популярные\n"
            "/genre - по жанру\n"
            "/recommend - рекомендация нейросети\n"
            "/rated - топ по рейтингу"
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "random":
        anime = random.choice(POPULAR_ANIME)
        text = f"🎲 *Случайное аниме:*\n\n*{anime['title']}*\n⭐ {anime['rating']}\n🎭 {', '.join(anime['genres'])}"
        await query.edit_message_text(text, parse_mode='Markdown')
    
    elif data == "popular":
        text = "🔥 *Популярные аниме:*\n\n"
        for i, anime in enumerate(POPULAR_ANIME[:3], 1):
            text += f"{i}. *{anime['title']}* - ⭐ {anime['rating']}\n"
        await query.edit_message_text(text, parse_mode='Markdown')
    
    elif data == "rated":
        text = "⭐ *Топ по рейтингу:*\n\n"
        for i, anime in enumerate(RATED_ANIME, 1):
            text += f"{i}. *{anime['title']}* - ⭐ {anime['rating']}\n"
        await query.edit_message_text(text, parse_mode='Markdown')
    
    elif data == "genre":
        await genre_selection(update, context)
    
    elif data == "recommend":
        await recommend_start(update, context)
    
    elif data.startswith("genre_"):
        await genre_callback(update, context)

def main():
    if not TOKEN:
        logger.error("BOT_TOKEN not found!")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("random", random_anime))
    app.add_handler(CommandHandler("popular", popular_anime))
    app.add_handler(CommandHandler("rated", rated_anime))
    app.add_handler(CommandHandler("genre", genre_selection))
    app.add_handler(CommandHandler("recommend", recommend_start))
    
    # Обработчики кнопок
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("🚀 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()