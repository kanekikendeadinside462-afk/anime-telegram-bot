import aiohttp
import json
import re
from config import YANDEX_API_KEY, YANDEX_FOLDER_ID, NEURAL_NETWORK_TYPE

class NeuralNetworkHelper:
    def __init__(self):
        self.type = NEURAL_NETWORK_TYPE
    
    async def get_anime_recommendations(self, user_query: str):
        """Получение рекомендаций от нейросети"""
        if self.type != "yandex":
            return None
        
        prompt = f"""
Ты - эксперт по аниме. Пользователь хочет получить рекомендации аниме.
Запрос пользователя: {user_query}

Дай 3 рекомендации аниме в формате JSON. Отвечай только JSON, без лишнего текста.
Формат:
[
    {{
        "title": "Название аниме",
        "description": "Краткое описание (1-2 предложения)",
        "rating": "Рейтинг от 1 до 10 (если знаешь)",
        "reason": "Почему это аниме подходит под запрос"
    }}
]
"""
        
        return await self._get_yandex_recommendations(prompt)
    
    async def _get_yandex_recommendations(self, prompt: str):
        """Использование YandexGPT"""
        try:
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            headers = {
                "Authorization": f"Api-Key {YANDEX_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.6,
                    "maxTokens": 800
                },
                "messages": [
                    {"role": "system", "text": "Ты - эксперт по аниме. Отвечай только в формате JSON, без пояснений."},
                    {"role": "user", "text": prompt}
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    result = await response.json()
                    
                    if 'result' in result:
                        content = result['result']['alternatives'][0]['message']['text']
                        # Извлекаем JSON из ответа
                        json_match = re.search(r'\[.*\]', content, re.DOTALL)
                        if json_match:
                            return json.loads(json_match.group())
        except Exception as e:
            print(f"YandexGPT error: {e}")
        
        return None
    
    async def analyze_request(self, text: str):
        """Анализ запроса пользователя"""
        if self.type != "yandex":
            return "🔮 Нейросеть временно недоступна. Используй команды /random или /genre для подбора аниме!"
        
        prompt = f"""
Проанализируй запрос пользователя об аниме: "{text}"

Если пользователь просит рекомендацию - дай советы и предложи конкретные аниме.
Если спрашивает о конкретном аниме - расскажи о нем.
Если просто общается - поддержи диалог.

Ответь дружелюбно, информативно, используй эмодзи.
"""
        
        try:
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            headers = {
                "Authorization": f"Api-Key {YANDEX_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.7,
                    "maxTokens": 500
                },
                "messages": [
                    {"role": "system", "text": "Ты - дружелюбный помощник по аниме."},
                    {"role": "user", "text": prompt}
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    result = await response.json()
                    if 'result' in result:
                        return result['result']['alternatives'][0]['message']['text']
        except Exception as e:
            print(f"YandexGPT analyze error: {e}")
        
        return "🔮 Нейросеть временно недоступна. Попробуй позже или используй команды /random, /genre!"
    
    async def analyze_quiz_answers(self, answers: list):
        """Анализ ответов квиза"""
        if self.type != "yandex":
            return None
        
        prompt = f"""
На основе ответов пользователя в квизе подбери 3 аниме.
Ответы пользователя: {answers}

Верни JSON с рекомендациями:
[
    {{
        "title": "Название аниме",
        "description": "Краткое описание"
    }}
]
"""
        
        return await self._get_yandex_recommendations(prompt)