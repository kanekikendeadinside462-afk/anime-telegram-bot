import logging
import random
from anime_recommender import AnimeRecommender

logger = logging.getLogger(__name__)

class NeuralNetworkHelper:
    def __init__(self):
        self.recommender = AnimeRecommender()
        # Готовая база аниме для рекомендаций
        self.anime_db = [
            {"title": "Атака Титанов", "desc": "Эпичное фэнтези о борьбе человечества с гигантскими титанами", "rating": "9.0", "genre": "Экшен", "year": 2013},
            {"title": "Врата Штейна", "desc": "Научная фантастика о путешествиях во времени и последствиях", "rating": "9.1", "genre": "Sci-Fi", "year": 2011},
            {"title": "Магическая битва", "desc": "Динамичный экшен про магию, проклятия и сильных героев", "rating": "8.8", "genre": "Экшен", "year": 2020},
            {"title": "Клинок, рассекающий демонов", "desc": "Красивое аниме о борьбе с демонами", "rating": "8.9", "genre": "Экшен", "year": 2019},
            {"title": "Ванпанчмен", "desc": "Комедийный экшен про героя, который побеждает всех с одного удара", "rating": "8.7", "genre": "Комедия", "year": 2015},
            {"title": "Тетрадь смерти", "desc": "Психологический триллер о противостоянии гениев", "rating": "9.0", "genre": "Триллер", "year": 2006},
            {"title": "Стальной алхимик", "desc": "Глубокая история о братстве, жертвах и поиске истины", "rating": "9.1", "genre": "Приключения", "year": 2009},
            {"title": "Твоё имя", "desc": "Трогательная романтическая история о связи судеб", "rating": "8.9", "genre": "Романтика", "year": 2016},
            {"title": "One Punch Man", "desc": "Сатирический экшен о самом сильном герое", "rating": "8.7", "genre": "Комедия", "year": 2015},
            {"title": "Код Гиас", "desc": "Эпичная история о мести и переустройстве мира", "rating": "8.9", "genre": "Экшен", "year": 2006},
            {"title": "Хантер х Хантер", "desc": "Приключения юного охотника в поисках отца", "rating": "9.0", "genre": "Приключения", "year": 2011},
            {"title": "Торадора", "desc": "Школьная романтическая комедия", "rating": "8.6", "genre": "Романтика", "year": 2008},
            {"title": "Re:Zero", "desc": "Тёмное фэнтези с возвращением во времени", "rating": "8.7", "genre": "Фэнтези", "year": 2016},
            {"title": "Токийский гуль", "desc": "Мрачная история о существах, питающихся людьми", "rating": "8.2", "genre": "Ужасы", "year": 2014},
            {"title": "Паразит", "desc": "Научная фантастика о вторжении паразитов", "rating": "8.8", "genre": "Ужасы", "year": 2014},
        ]
    
    async def get_anime_recommendations(self, user_query: str):
        """Получение рекомендаций аниме"""
        logger.info(f"Запрос на рекомендацию: {user_query}")
        
        query_lower = user_query.lower()
        
        # Словарь ключевых слов и соответствующих жанров
        keywords = {
            "приключени": "Приключения",
            "экшен": "Экшен",
            "боевик": "Экшен",
            "романтик": "Романтика",
            "любов": "Романтика",
            "комеди": "Комедия",
            "смешн": "Комедия",
            "драма": "Драма",
            "грустн": "Драма",
            "фэнтези": "Фэнтези",
            "маги": "Фэнтези",
            "ужас": "Ужасы",
            "страшн": "Ужасы",
            "научн": "Sci-Fi",
            "фантастик": "Sci-Fi",
            "триллер": "Триллер",
            "психолог": "Триллер",
            "спорт": "Спорт"
        }
        
        # Определяем жанр
        detected_genre = None
        for keyword, genre in keywords.items():
            if keyword in query_lower:
                detected_genre = genre
                logger.info(f"Определён жанр: {genre}")
                break
        
        # Фильтруем аниме по жанру
        if detected_genre:
            filtered = [a for a in self.anime_db if a['genre'] == detected_genre]
        else:
            filtered = self.anime_db.copy()
        
        # Если ничего не нашли, берём всё
        if not filtered:
            filtered = self.anime_db
        
        # Берём 3 случайных аниме
        recommendations = random.sample(filtered, min(3, len(filtered)))
        
        # Форматируем результат
        result = []
        for anime in recommendations:
            result.append({
                "title": anime['title'],
                "description": anime['desc'],
                "rating": anime['rating'],
                "reason": f"По твоему запросу подходит это {anime['genre']} аниме" if detected_genre else "Это популярное аниме"
            })
        
        logger.info(f"Найдено {len(result)} рекомендаций")
        return result
    
    async def analyze_request(self, text: str):
        """Анализ запроса пользователя"""
        query_lower = text.lower()
        
        # Приветствие
        if "привет" in query_lower:
            return "🦇 *Приветствую, искатель!* Готов погрузиться во тьму аниме?\n\nНапиши что хочешь посмотреть, например:\n- посоветуй аниме про приключения\n- что-то романтичное\n- мрачное аниме"
        
        # Помощь
        if "помощ" in query_lower or "help" in query_lower:
            return "🦇 *Помощь:*\n\n/start — главное меню\n/random — случайное аниме\n/genre — по жанру\n/recommend — рекомендации\n/popular — популярные\n/rated — топ рейтинга\n\nИли просто напиши, что хочешь посмотреть!"
        
        # Получаем рекомендации
        recommendations = await self.get_anime_recommendations(text)
        
        if recommendations:
            response = "🔮 *Тьма шепчет...*\n\n"
            for i, rec in enumerate(recommendations, 1):
                response += f"{i}. 🎬 *{rec['title']}*\n"
                response += f"   📜 {rec['description']}\n"
                response += f"   ⭐ Рейтинг: {rec['rating']}/10\n"
                response += f"   💀 *Почему:* {rec['reason']}\n\n"
            response += "_Да будет так..._"
            return response
        
        return "🌙 *Тьма не может разобрать твой запрос...*\n\nПопробуй:\n• посоветуй аниме про приключения\n• что-то романтичное\n• мрачное аниме\n• экшен с магией"
    
    async def analyze_quiz_answers(self, answers: list):
        """Анализ ответов квиза"""
        return await self.get_anime_recommendations(" ".join(answers))