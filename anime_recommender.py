import random
from anilist_api import AniListAPI

class AnimeRecommender:
    def __init__(self):
        self.api = AniListAPI()
    
    def get_random_anime(self):
        """Случайное аниме из популярных"""
        popular = self.api.get_popular_anime(50)
        if popular:
            anime = random.choice(popular)
            return self.api.format_anime_for_bot(anime)
        return None
    
    def get_popular_anime(self):
        """Популярные аниме"""
        popular = self.api.get_popular_anime(5)
        return [self.api.format_anime_for_bot(anime) for anime in popular]
    
    def get_top_rated_anime(self):
        """Топ рейтинговых аниме"""
        top = self.api.get_top_rated_anime(5)
        return [self.api.format_anime_for_bot(anime) for anime in top]
    
    def get_anime_by_genre(self, genre):
        """Поиск по жанру"""
        results = self.api.search_by_genre(genre)
        if results:
            anime = random.choice(results)
            return self.api.format_anime_for_bot(anime)
        return None
    
    def search_anime(self, query):
        """Поиск аниме"""
        results = self.api.search_anime(query)
        if results:
            return [self.api.format_anime_for_bot(anime) for anime in results[:5]]
        return []
    
    def get_quiz_questions(self):
        """Вопросы для квиза"""
        return [
            {"text": "🎭 Какой жанр аниме тебе нравится больше всего?\n\nНапиши один из: экшен, романтика, комедия, драма, фэнтези, научная фантастика, приключения, ужасы, триллер"},
            {"text": "⏱️ Сколько эпизодов ты хочешь смотреть?\n\nНапиши: короткое (1-12), среднее (13-26), длинное (50+)"},
            {"text": "😊 Какое настроение у аниме должно быть?\n\nНапиши: веселое, серьезное, грустное, вдохновляющее, романтичное"},
            {"text": "❤️ Назови одно-два аниме, которые тебе очень понравились (для примера)"}
        ]
    
    def get_recommendations_by_preferences(self, answers):
        """Рекомендации на основе ответов"""
        # Пытаемся определить жанр из ответов
        genres_to_try = ["экшен", "романтика", "комедия", "драма", "фэнтези", "приключения"]
        
        for answer in answers:
            answer_lower = answer.lower()
            for genre in genres_to_try:
                if genre in answer_lower:
                    return self.get_anime_by_genre(genre)
        
        # Если не нашли жанр, возвращаем случайное популярное аниме
        popular = self.api.get_popular_anime(1)
        if popular:
            return self.api.format_anime_for_bot(popular[0])
        return None