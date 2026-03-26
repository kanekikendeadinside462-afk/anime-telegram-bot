import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN
from anime_recommender import AnimeRecommender
from neural_network import NeuralNetworkHelper
from database import Database

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AnimeBot:
    def __init__(self):
        self.recommender = AnimeRecommender()
        self.neural = NeuralNetworkHelper()
        self.db = Database()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        self.db.add_user(user.id, user.username)
        
        welcome_text = f"""
🌟 Привет, {user.first_name}! Я аниме-бот с нейросетью!

Я помогу тебе выбрать аниме для просмотра:

🎲 /random - случайное аниме
🎭 /genre - выбрать по жанру
🤖 /recommend - рекомендация от нейросети
🔥 /popular - популярные аниме
⭐ /rated - топ по рейтингу
🔍 /search [название] - поиск аниме
❓ /help - помощь

Просто напиши, что хочешь посмотреть!
        """
        
        await update.message.reply_text(welcome_text)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        help_text = """
📚 *Команды:*

/start - начать работу
/random - случайное аниме
/genre - выбрать по жанру
/recommend - рекомендация от нейросети
/popular - топ популярных аниме
/rated - топ рейтинговых аниме
/search [название] - поиск аниме
/help - помощь

💡 *Примеры запросов:*
- "Посоветуй аниме про приключения"
- "Какое аниме похоже на Наруто?"
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def random_anime(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Случайное аниме"""
        await update.message.reply_text("🔍 Ищу случайное аниме...")
        anime = self.recommender.get_random_anime()
        if anime:
            await self.send_anime_info(update, anime)
        else:
            await update.message.reply_text("😔 Не удалось получить аниме. Попробуй позже!")
    
    async def genre_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор жанра"""
        genres = ["Экшен", "Приключения", "Комедия", "Драма", "Фэнтези", "Романтика", "Научная фантастика", "Ужасы", "Триллер"]
        
        keyboard = []
        for genre in genres:
            keyboard.append([InlineKeyboardButton(genre, callback_data=f"genre_{genre}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🎭 Выбери жанр:", reply_markup=reply_markup)
    
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
    
    async def search_anime(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Поиск аниме"""
        if not context.args:
            await update.message.reply_text("🔍 Напиши название после команды, например:\n/search Наруто")
            return
        
        query = " ".join(context.args)
        await update.message.reply_text(f"🔍 Ищу: {query}...")
        
        results = self.recommender.search_anime(query)
        if results:
            for anime in results[:3]:
                await self.send_anime_info(update, anime)
        else:
            await update.message.reply_text("😔 Ничего не найдено. Попробуй другое название!")
    
    async def neural_recommendation_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запуск нейросетевой рекомендации"""
        await update.message.reply_text(
            "🤖 *Напиши, что ты хочешь посмотреть!*\n\n"
            "Например: 'Посоветуй аниме про самураев с глубоким сюжетом'",
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_neural'] = True
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text
        
        # Проверяем, ждет ли пользователь рекомендацию от нейросети
        if context.user_data.get('waiting_for_neural'):
            await update.message.reply_text("🔮 Нейросеть анализирует твой запрос... Подожди немного!")
            
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
                    "😔 Извини, не удалось получить рекомендации. "
                    "Попробуй переформулировать запрос или используй команды /random, /genre!"
                )
            
            context.user_data['waiting_for_neural'] = False
        else:
            # Обычный запрос к нейросети
            await update.message.reply_text("🔍 Обрабатываю запрос...")
            response = await self.neural.analyze_request(text)
            await update.message.reply_text(response, parse_mode='Markdown')
    
    async def send_anime_info(self, update: Update, anime: dict):
        """Отправка информации об аниме"""
        genres_text = ', '.join(anime.get('genres', ['Не указаны'])) if anime.get('genres') else 'Не указаны'
        
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
            [InlineKeyboardButton("🤖 Еще рекомендации", callback_data="neural_recommend")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Если есть картинка, отправляем с фото
        if anime.get('image_url'):
            try:
                await update.message.reply_photo(
                    photo=anime['image_url'],
                    caption=text,
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            except Exception as e:
                print(f"Ошибка отправки фото: {e}")
                await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data == "random":
            await self.random_anime(update, context)
        elif data == "genre":
            await self.genre_selection(update, context)
        elif data == "neural_recommend":
            await self.neural_recommendation_start(update, context)
        elif data == "popular":
            await self.popular_anime(update, context)
        elif data == "rated":
            await self.rated_anime(update, context)
        elif data.startswith("genre_"):
            genre = data.replace("genre_", "")
            await update.message.reply_text(f"🔍 Ищу аниме в жанре {genre}...")
            anime = self.recommender.get_anime_by_genre(genre)
            if anime:
                await self.send_anime_info(update, anime)
            else:
                await update.message.reply_text(f"😔 Не нашел аниме в жанре {genre}. Попробуй другой жанр!")
        elif data.startswith("like_"):
            anime_id = data.replace("like_", "")
            self.db.add_like(update.effective_user.id, anime_id)
            await query.edit_message_text("❤️ Спасибо! Учту твой вкус для следующих рекомендаций!")
    
    async def run(self):
        """Запуск бота"""
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Регистрация обработчиков
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("random", self.random_anime))
        self.application.add_handler(CommandHandler("genre", self.genre_selection))
        self.application.add_handler(CommandHandler("recommend", self.neural_recommendation_start))
        self.application.add_handler(CommandHandler("popular", self.popular_anime))
        self.application.add_handler(CommandHandler("rated", self.rated_anime))
        self.application.add_handler(CommandHandler("search", self.search_anime))
        
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("🚀 Бот запущен!")
        
        # Запускаем бота
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Держим бота запущенным
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            await self.application.stop()

if __name__ == "__main__":
    import asyncio
    bot = AnimeBot()
    
    # Создаем новый event loop для Railway
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(bot.run())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()