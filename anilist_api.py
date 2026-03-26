import requests
import re
import random

class AniListAPI:
    def __init__(self):
        self.graphql_url = "https://graphql.anilist.co"
    
    def search_anime(self, query):
        """Поиск аниме по названию"""
        graphql_query = """
        query ($search: String) {
            Page(page: 1, perPage: 10) {
                media(search: $search, type: ANIME) {
                    id
                    title {
                        romaji
                        english
                        native
                    }
                    description
                    averageScore
                    genres
                    episodes
                    coverImage {
                        large
                    }
                    seasonYear
                }
            }
        }
        """
        
        variables = {"search": query}
        
        try:
            response = requests.post(
                self.graphql_url,
                json={"query": graphql_query, "variables": variables}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("Page", {}).get("media", [])
        except Exception as e:
            print(f"Ошибка поиска: {e}")
        
        return []
    
    def get_popular_anime(self, limit=10):
        """Получение популярных аниме"""
        graphql_query = """
        query ($limit: Int) {
            Page(page: 1, perPage: $limit) {
                media(sort: POPULARITY_DESC, type: ANIME) {
                    id
                    title { romaji english }
                    description
                    averageScore
                    genres
                    episodes
                    coverImage { large }
                    seasonYear
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.graphql_url,
                json={"query": graphql_query, "variables": {"limit": limit}}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("Page", {}).get("media", [])
        except Exception as e:
            print(f"Ошибка получения популярных: {e}")
        
        return []
    
    def get_top_rated_anime(self, limit=10):
        """Получение топ-рейтинговых аниме"""
        graphql_query = """
        query ($limit: Int) {
            Page(page: 1, perPage: $limit) {
                media(sort: SCORE_DESC, type: ANIME) {
                    id
                    title { romaji english }
                    description
                    averageScore
                    genres
                    episodes
                    coverImage { large }
                    seasonYear
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.graphql_url,
                json={"query": graphql_query, "variables": {"limit": limit}}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("Page", {}).get("media", [])
        except Exception as e:
            print(f"Ошибка получения топовых: {e}")
        
        return []
    
    def search_by_genre(self, genre):
        """Поиск аниме по жанру"""
        # Сопоставление русских жанров с английскими для AniList
        genre_map = {
            "экшен": "Action",
            "романтика": "Romance",
            "комедия": "Comedy",
            "драма": "Drama",
            "фэнтези": "Fantasy",
            "научная фантастика": "Sci-Fi",
            "приключения": "Adventure",
            "ужасы": "Horror",
            "триллер": "Thriller",
            "мистика": "Mystery",
            "спорт": "Sports",
            "повседневность": "Slice of Life"
        }
        
        # Если жанр на русском, переводим
        if genre.lower() in genre_map:
            genre = genre_map[genre.lower()]
        
        graphql_query = """
        query ($genre: String) {
            Page(page: 1, perPage: 10) {
                media(genre_in: [$genre], type: ANIME) {
                    id
                    title { romaji english }
                    description
                    averageScore
                    genres
                    episodes
                    coverImage { large }
                    seasonYear
                }
            }
        }
        """
        
        try:
            response = requests.post(
                self.graphql_url,
                json={"query": graphql_query, "variables": {"genre": genre}}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", {}).get("Page", {}).get("media", [])
        except Exception as e:
            print(f"Ошибка поиска по жанру: {e}")
        
        return []
    
    def format_anime_for_bot(self, anime):
        """Форматирование аниме для отправки в Telegram"""
        title = anime.get('title', {})
        title_text = title.get('english') or title.get('romaji') or title.get('native', 'Название неизвестно')
        
        description = anime.get('description', '')
        # Убираем HTML теги из описания
        description = re.sub(r'<[^>]+>', '', description)
        description = description[:500] + "..." if len(description) > 500 else description
        if not description:
            description = "Описание отсутствует"
        
        rating = anime.get('averageScore', 0)
        rating_text = f"{rating/10:.1f}" if rating else "Н/Д"
        
        return {
            'id': anime.get('id'),
            'title': title_text,
            'description': description,
            'rating': rating_text,
            'genres': anime.get('genres', []),
            'year': anime.get('seasonYear', 'Н/Д'),
            'episodes': anime.get('episodes', 'Н/Д'),
            'image_url': anime.get('coverImage', {}).get('large', None)
        }