import os
import logging
import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from anime_recommender import AnimeRecommender
from neural_network import NeuralNetworkHelper
from database import Database
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnimeBot:
    def __init__(self):
        self.recommender = AnimeRecommender()
        self.neural = NeuralNetworkHelper()
        self.db = Database()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Главное меню"""
        user = update.effective_user
        self.db.add_user(user.id, user.username)
        
        keyboard = [
            [InlineKeyboardButton("🦇 Случайное аниме", callback_data="main_random")],
            [InlineKeyboardButton("🎭 По жанру", callback_data="main_genre")],
            [InlineKeyboardButton("🔮 Рекомендация", callback_data="main_recommend")],
            [InlineKeyboardButton("🔥 Популярные", callback_data="main_popular")],
            [InlineKeyboardButton("⭐ Топ рейтинга", callback_data="main_rated")],
            [InlineKeyboardButton("🔍 Поиск", callback_data="main_search")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = (
            f"🦇 *Добро пожаловать в Тёмную Библиотеку, {user.first_name}...*\n\n"
            "Я хранитель аниме-знаний. Выбери своё оружие:\n\n"
            "🦇 Случайное аниме — пусть судьба решит\n"
            "🎭 По жанру — найди своё проклятие\n"
            "🔮 Рекомендация — я угадаю твои желания\n"
            "🔥 Популярные — что пьёт кровь масс\n"
            "⭐ Топ рейтинга — лучшие из лучших\n"
            "🔍 Поиск — ищи по имени\n\n"
            "_Тьма знает твои вкусы..._"
        )
        
        if update.callback_query:
            await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def show_random(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query_message=None):
        """Показать случайное аниме"""
        target = query_message or update.message
        await target.reply_text("🦇 *Призываю судьбу...*", parse_mode='Markdown')
        anime = self.recommender.get_random_anime()
        if anime:
            await self.send_anime_info(target, anime, show_back=True)
        else:
            await target.reply_text("🌙 *Тьма молчит... Попробуй позже*", parse_mode='Markdown')
    
    async def show_popular(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query_message=None):
        """Показать популярные аниме"""
        target = query_message or update.message
        await target.reply_text("🔥 *Пробуждаю популярность...*", parse_mode='Markdown')
        animes = self.recommender.get_popular_anime()
        if animes:
            for anime in animes[:3]:
                await self.send_anime_info(target, anime, show_back=True)
        else:
            await target.reply_text("🌙 *Ничего не найдено...*", parse_mode='Markdown')
    
    async def show_rated(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query_message=None):
        """Показать топ по рейтингу"""
        target = query_message or update.message
        await target.reply_text("⭐ *Взываю к великим...*", parse_mode='Markdown')
        animes = self.recommender.get_top_rated_anime()
        if animes:
            for anime in animes[:3]:
                await self.send_anime_info(target, anime, show_back=True)
        else:
            await target.reply_text("🌙 *Тьма хранит тайны...*", parse_mode='Markdown')
    
    async def show_genres(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать список жанров"""
        genres = [
            ("⚔️ Экшен", "Экшен"),
            ("🗺️ Приключения", "Приключения"),
            ("😈 Комедия", "Комедия"),
            ("💀 Драма", "Драма"),
            ("🔮 Фэнтези", "Фэнтези"),
            ("🥀 Романтика", "Романтика"),
            ("🤖 Sci-Fi", "Научная фантастика"),
            ("🩸 Ужасы", "Ужасы"),
            ("🎭 Триллер", "Триллер"),
        ]
        
        keyboard = []
        for display, value in genres:
            keyboard.append([InlineKeyboardButton(display, callback_data=f"genre_{value}")])
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "🦇 *Выбери свой путь...*\n\n_Каждый жанр — это врата в новый мир_",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "🦇 *Выбери свой путь...*",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def show_search_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать запрос на поиск"""
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "🔍 *Введи название аниме...*\n\n_Я найду его даже в самой тёмной бездне_",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "🔍 *Введи название аниме...*",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        context.user_data['waiting_for_search'] = True
    
    async def show_recommend_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать запрос на рекомендацию"""
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "🔮 *Я слышу твои желания...*\n\n"
                "Напиши, что ты хочешь увидеть, например:\n"
                "🦇 *Посоветуй аниме про вампиров*\n"
                "🗡️ *Что-то мрачное и глубокое*\n"
                "🎭 *Аниме, где герой теряет всё*",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "🔮 *Напиши, что ты хочешь посмотреть...*",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        context.user_data['waiting_for_recommend'] = True
    
    async def handle_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка поиска"""
        text = update.message.text
        await update.message.reply_text(f"🔍 *Ищу {text}...*", parse_mode='Markdown')
        results = self.recommender.search_anime(text)
        
        if results:
            for anime in results[:3]:
                await self.send_anime_info(update.message, anime, show_back=True)
        else:
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "🌙 *Ничего не найдено... Попробуй другое имя*",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        context.user_data['waiting_for_search'] = False
    
    async def handle_recommend(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка рекомендации"""
        text = update.message.text
        msg = await update.message.reply_text("🔮 *Анализирую твою душу...*", parse_mode='Markdown')
        recommendations = await self.neural.get_anime_recommendations(text)
        
        if recommendations:
            response = "🦇 *Тьма шепчет...*\n\n"
            for i, rec in enumerate(recommendations[:3], 1):
                response += f"{i}. *{rec.get('title', 'Неизвестно')}*\n"
                response += f"   📜 {rec.get('description', 'Описание отсутствует')}\n"
                if rec.get('rating'):
                    response += f"   ⭐ {rec.get('rating')}/10\n"
                if rec.get('reason'):
                    response += f"   💀 *Почему:* {rec.get('reason')}\n"
                response += "\n"
            response += "_Да будет так..._"
            
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await msg.edit_text(
                "🌙 *Тьма молчит... Попробуй переформулировать запрос*",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        
        context.user_data['waiting_for_recommend'] = False
    
    async def handle_genre(self, update: Update, context: ContextTypes.DEFAULT_TYPE, genre: str):
        """Обработка выбора жанра"""
        await update.callback_query.message.reply_text(f"🎭 *Ищу в жанре {genre}...*", parse_mode='Markdown')
        anime = self.recommender.get_anime_by_genre(genre)
        if anime:
            await self.send_anime_info(update.callback_query.message, anime, show_back=True)
        else:
            keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="main_genre")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.message.reply_text(
                f"🌙 *Не нашел аниме в жанре {genre}...*",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
    
    async def send_anime_info(self, message, anime: dict, show_back: bool = False):
        """Отправка информации об аниме с постером"""
        genres_text = ' • '.join(anime.get('genres', ['Таинственный']))
        
        text = f"""
🦇 *{anime.get('title', 'Имя потеряно')}*

📜 *Свиток:* 
{anime.get('description', 'Описание скрыто во тьме')[:500]}...

⚰️ *Рейтинг:* ⭐ {anime.get('rating', '???')}/10
🎭 *Жанры:* {genres_text}
📅 *Год:* {anime.get('year', '???')}
🎬 *Эпизоды:* {anime.get('episodes', '???')}

_Прикоснись к тени..._
        """
        
        keyboard = [
            [InlineKeyboardButton("🦇 Понравилось", callback_data=f"like_{anime.get('id')}"),
             InlineKeyboardButton("🎲 Другое", callback_data="main_random")],
        ]
        if show_back:
            keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if anime.get('image_url'):
            try:
                await message.reply_photo(
                    photo=anime['image_url'],
                    caption=text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Ошибка отправки фото: {e}")
                await message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка всех кнопок"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        # Главные кнопки
        if data == "main_menu":
            await self.start(update, context)
        
        elif data == "main_random":
            await self.show_random(update, context, query.message)
        
        elif data == "main_popular":
            await self.show_popular(update, context, query.message)
        
        elif data == "main_rated":
            await self.show_rated(update, context, query.message)
        
        elif data == "main_genre":
            await self.show_genres(update, context)
        
        elif data == "main_search":
            await self.show_search_prompt(update, context)
        
        elif data == "main_recommend":
            await self.show_recommend_prompt(update, context)
        
        # Кнопки жанров
        elif data.startswith("genre_"):
            genre = data.replace("genre_", "")
            await self.handle_genre(update, context, genre)
        
        # Кнопка лайка
        elif data.startswith("like_"):
            anime_id = data.replace("like_", "")
            self.db.add_like(update.effective_user.id, anime_id)
            await query.edit_message_text(
                "🦇 *Тьма запомнила твой выбор...*\n\n_Благодарю, искатель_",
                parse_mode='Markdown'
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        if context.user_data.get('waiting_for_search'):
            await self.handle_search(update, context)
        elif context.user_data.get('waiting_for_recommend'):
            await self.handle_recommend(update, context)
        else:
            await update.message.reply_text(
                "🦇 *Используй команды или кнопки...*\n\n"
                "/start — начать ритуал",
                parse_mode='Markdown'
            )
    
    async def run(self):
        """Запуск бота"""
        app = Application.builder().token(BOT_TOKEN).build()
        
        app.add_handler(CommandHandler("start", self.start))
        
        app.add_handler(CallbackQueryHandler(self.button_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("🦇 Бот пробудился из тьмы!")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        
        await asyncio.Event().wait()

if __name__ == "__main__":
    bot = AnimeBot()
    asyncio.run(bot.run())