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

# Настройка логирования
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
            [InlineKeyboardButton("🎲 Случайное аниме", callback_data="random")],
            [InlineKeyboardButton("🎭 По жанру", callback_data="genre")],
            [InlineKeyboardButton("🤖 Рекомендация от нейросети", callback_data="recommend")],
            [InlineKeyboardButton("🔥 Популярные", callback_data="popular")],
            [InlineKeyboardButton("⭐ Топ по рейтингу", callback_data="rated")],
            [InlineKeyboardButton("🔍 Поиск", callback_data="search")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🌟 Привет, {user.first_name}! Я аниме-бот с нейросетью YandexGPT!\n\n"
            "Выбери действие:",
            reply_markup=reply_markup
        )
    
    async def random_anime(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Случайное аниме"""
        await update.message.reply_text("🔍 Ищу случайное аниме...")
        anime = self.recommender.get_random_anime()
        if anime:
            await self.send_anime_info(update, anime)
        else:
            await update.message.reply_text("😔 Не удалось получить аниме. Попробуй позже!")
    
    async def popular_anime(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Популярные аниме"""
        await update.message.reply_text("🔥 Загружаю популярные аниме...")
        animes = self.recommender.get_popular_anime()
        for anime in animes[:3]:
            await self.send_anime_info(update, anime)
    
    async def rated_anime(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Топ по рейтингу"""
        await update.message.reply_text("⭐ Загружаю топ по рейтингу...")
        animes = self.recommender.get_top_rated_anime()
        for anime in animes[:3]:
            await self.send_anime_info(update, anime)
    
    async def genre_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор жанра"""
        genres = [
            "Экшен", "Приключения", "Комедия", "Драма", 
            "Фэнтези", "Романтика", "Научная фантастика", "Ужасы", "Триллер"
        ]
        
        keyboard = [[InlineKeyboardButton(genre, callback_data=f"genre_{genre}")] for genre in genres]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text("🎭 Выбери жанр:", reply_markup=reply_markup)
    
    async def search_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запрос на поиск"""
        await update.message.reply_text("🔍 Введи название аниме для поиска:")
        context.user_data['waiting_for_search'] = True
    
    async def recommend_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запрос рекомендации от нейросети"""
        await update.message.reply_text(
            "🤖 *Нейросеть YandexGPT поможет выбрать аниме!*\n\n"
            "Напиши, что ты хочешь посмотреть, например:\n"
            "- Посоветуй аниме про приключения\n"
            "- Что-то похожее на Наруто\n"
            "- Аниме с глубоким сюжетом\n"
            "- Романтическое аниме"
        )
        context.user_data['waiting_for_recommend'] = True
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text
        
        # Поиск аниме
        if context.user_data.get('waiting_for_search'):
            await update.message.reply_text(f"🔍 Ищу: {text}...")
            results = self.recommender.search_anime(text)
            
            if results:
                for anime in results[:3]:
                    await self.send_anime_info(update, anime)
            else:
                await update.message.reply_text("😔 Ничего не найдено. Попробуй другое название!")
            
            context.user_data['waiting_for_search'] = False
        
        # Рекомендация от нейросети
        elif context.user_data.get('waiting_for_recommend'):
            await update.message.reply_text("🔮 Нейросеть анализирует запрос... Подожди немного!")
            
            recommendations = await self.neural.get_anime_recommendations(text)
            
            if recommendations:
                response = "🎯 *Нейросеть рекомендует:*\n\n"
                for i, rec in enumerate(recommendations[:3], 1):
                    response += f"{i}. *{rec.get('title', 'Неизвестно')}*\n"
                    response += f"   📝 {rec.get('description', 'Описание отсутствует')}\n"
                    if rec.get('rating'):
                        response += f"   ⭐ Рейтинг: {rec.get('rating')}\n"
                    if rec.get('reason'):
                        response += f"   💡 *Почему:* {rec.get('reason')}\n"
                    response += "\n"
                
                await update.message.reply_text(response, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    "😔 Не удалось получить рекомендации. "
                    "Попробуй переформулировать запрос или используй команды /random, /genre!"
                )
            
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
    
    async def send_anime_info(self, update: Update, anime: dict):
        """Отправка информации об аниме с постером"""
        genres_text = ', '.join(anime.get('genres', ['Не указаны']))
        
        text = f"""
🎬 *{anime.get('title', 'Название неизвестно')}*

📝 *Описание:*
{anime.get('description', 'Описание отсутствует')}

⭐ *Рейтинг:* {anime.get('rating', 'Н/Д')}/10
🎭 *Жанры:* {genres_text}
📅 *Год:* {anime.get('year', 'Н/Д')}
🎥 *Эпизоды:* {anime.get('episodes', 'Н/Д')}
        """
        
        keyboard = [
            [InlineKeyboardButton("👍 Понравилось", callback_data=f"like_{anime.get('id')}"),
             InlineKeyboardButton("🎲 Другое", callback_data="random")],
            [InlineKeyboardButton("🤖 Рекомендации", callback_data="recommend")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправка с постером
        if anime.get('image_url'):
            try:
                await update.message.reply_photo(
                    photo=anime['image_url'],
                    caption=text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            except Exception as e:
                logger.error(f"Ошибка отправки фото: {e}")
                await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка кнопок"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "random":
            await query.message.reply_text("🔍 Ищу случайное аниме...")
            anime = self.recommender.get_random_anime()
            if anime:
                await self.send_anime_info(query.message, anime)
            else:
                await query.message.reply_text("😔 Не удалось получить аниме!")
        
        elif data == "popular":
            await query.message.reply_text("🔥 Загружаю популярные аниме...")
            animes = self.recommender.get_popular_anime()
            for anime in animes[:3]:
                await self.send_anime_info(query.message, anime)
        
        elif data == "rated":
            await query.message.reply_text("⭐ Загружаю топ по рейтингу...")
            animes = self.recommender.get_top_rated_anime()
            for anime in animes[:3]:
                await self.send_anime_info(query.message, anime)
        
        elif data == "genre":
            genres = ["Экшен", "Приключения", "Комедия", "Драма", "Фэнтези", "Романтика", "Научная фантастика", "Ужасы"]
            keyboard = [[InlineKeyboardButton(g, callback_data=f"genre_{g}")] for g in genres]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("🎭 Выбери жанр:", reply_markup=reply_markup)
        
        elif data == "recommend":
            await query.message.reply_text(
                "🤖 *Напиши, что ты хочешь посмотреть!*\n\n"
                "Например: 'Посоветуй аниме про приключения'",
                parse_mode='Markdown'
            )
            context.user_data['waiting_for_recommend'] = True
        
        elif data == "search":
            await query.message.reply_text("🔍 Введи название аниме для поиска:")
            context.user_data['waiting_for_search'] = True
        
        elif data.startswith("genre_"):
            genre = data.replace("genre_", "")
            await query.message.reply_text(f"🔍 Ищу аниме в жанре {genre}...")
            anime = self.recommender.get_anime_by_genre(genre)
            if anime:
                await self.send_anime_info(query.message, anime)
            else:
                await query.message.reply_text(f"😔 Не нашел аниме в жанре {genre}!")
        
        elif data.startswith("like_"):
            anime_id = data.replace("like_", "")
            self.db.add_like(update.effective_user.id, anime_id)
            await query.edit_message_text("❤️ Спасибо! Учту твой вкус!")
    
    async def run(self):
        """Запуск бота"""
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Команды
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("random", self.random_anime))
        app.add_handler(CommandHandler("popular", self.popular_anime))
        app.add_handler(CommandHandler("rated", self.rated_anime))
        app.add_handler(CommandHandler("genre", self.genre_selection))
        app.add_handler(CommandHandler("recommend", self.recommend_start))
        
        # Кнопки и сообщения
        app.add_handler(CallbackQueryHandler(self.button_callback))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("🚀 Бот запущен!")
        app.run_polling()

if __name__ == "__main__":
    bot = AnimeBot()
    bot.run()