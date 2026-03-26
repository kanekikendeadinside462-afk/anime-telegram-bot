import aiohttp
import json
import re
import random
import logging
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID, NEURAL_NETWORK_TYPE
from anime_recommender import AnimeRecommender

logger = logging.getLogger(__name__)

class NeuralNetworkHelper:
    def __init__(self):
        self.type = NEURAL_NETWORK_TYPE
        self.recommender = AnimeRecommender()
        logger.info("NeuralNetworkHelper инициализирован")
    
    async def get_anime_recommendations(self, user_query: str):
        """Получение рекомендаций аниме"""
        logger.info(f"Получен запрос на рекомендацию: {user_query}")
        
        # Анализируем запрос, чтобы понять жанр
        genres = {
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
            "научн": "Научная фантастика",
            "фантастик": "Научная фантастика",
            "триллер": "Триллер",
            "спорт": "Спорт",
            "повседневн": "Повседневность"
        }
        
        # Определяем жанр из запроса
        detected_genre = None
        query_lower = user_query.lower()
        
        for keyword, genre in genres.items():
            if keyword in query_lower:
                detected_genre = genre
                logger.info(f"Определён жанр: {genre} по ключевому слову: {keyword}")
                break
        
        # Получаем аниме по жанру
        if detected_genre:
            anime = self.recommender.get_anime_by_genre(detected_genre)
            if anime:
                logger.info(f"Найдено аниме: {anime.get('title')}")
                return [self._format_recommendation(anime, detected_genre)]
        
        # Если не нашли по жанру, пробуем популярные
        logger.info("Пробуем получить популярные аниме")
        popular = self.recommender.get_popular_anime()
        if popular:
            logger.info(f"Получено {len(popular)} популярных аниме")
            recommendations = []
            for anime in popular[:3]:
                recommendations.append(self._format_recommendation(anime, "популярное"))
            return recommendations
        
        # Если совсем ничего не нашли
        logger.warning("Не удалось найти аниме для рекомендации")
        return None
    
    def _format_recommendation(self, anime: dict, reason: str):
        """Форматирование рекомендации"""
        title = anime.get('title', 'Неизвестно')
        description = anime.get('description', 'Описание отсутствует')[:200]
        rating = anime.get('rating', 'Н/Д')
        
        return {
            "title": title,
            "description": description,
            "rating": rating,
            "reason": f"По твоему запросу подходит это {reason} аниме"
        }
    
    async def analyze_request(self, text: str):
        """Анализ запроса пользователя"""
        logger.info(f"Анализ запроса: {text}")
        query_lower = text.lower()
        
        # Приветствие
        if "привет" in query_lower:
            return "🦇 *Приветствую, искатель!* Готов погрузиться во тьму аниме?"
        
        # Помощь
        if "помощ" in query_lower or "help" in query_lower:
            return "🦇 *Помощь:*\n/start — главное меню\n/random — случайное аниме\n/genre — по жанру\n/recommend — рекомендации\n/popular — популярные\n/rated — топ рейтинга"
        
        # Получаем рекомендации
        recommendations = await self.get_anime_recommendations(text)
        
        if recommendations:
            response = "🔮 *Тьма шепчет...*\n\n"
            for rec in recommendations:
                response += f"🎬 *{rec['title']}*\n"
                response += f"📜 {rec['description']}\n"
                response += f"⭐ {rec['rating']}/10\n"
                response += f"💀 *Почему:* {rec['reason']}\n\n"
            response += "_Да будет так..._"
            return response
        
        return "🌙 *Тьма не может разобрать твой запрос...*\n\nПопробуй один из вариантов:\n• Посоветуй аниме про приключения\n• Что-то романтичное\n• Мрачное аниме\n• Экшен с магией"
    
    async def analyze_quiz_answers(self, answers: list):
        """Анализ ответов квиза"""
        return await self.get_anime_recommendations(" ".join(answers))