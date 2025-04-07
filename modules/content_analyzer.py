from typing import Dict, List, Optional
from textblob import TextBlob
from collections import Counter
import re
from datetime import datetime

class ContentAnalyzer:
    def __init__(self):
        self.sentiment_threshold = 0.1
        self.engagement_weights = {
            'likes': 1,
            'comments': 2,
            'shares': 3,
            'saves': 4
        }

    def analyze_post(self, content: str, metrics: Dict) -> Dict:
        """Analiza el contenido de un post y sus métricas"""
        try:
            # Análisis de sentimiento
            blob = TextBlob(content)
            sentiment = blob.sentiment.polarity

            # Análisis de hashtags
            hashtags = re.findall(r'#(\w+)', content)
            hashtag_stats = self._analyze_hashtags(hashtags)

            # Análisis de longitud y estructura
            structure_analysis = self._analyze_structure(content)

            # Análisis de engagement
            engagement_score = self._calculate_engagement_score(metrics)

            return {
                'sentiment': {
                    'score': round(sentiment, 2),
                    'classification': self._classify_sentiment(sentiment)
                },
                'hashtags': hashtag_stats,
                'structure': structure_analysis,
                'engagement': engagement_score,
                'recommendations': self._generate_recommendations(
                    sentiment,
                    hashtag_stats,
                    structure_analysis,
                    engagement_score
                )
            }
        except Exception as e:
            return {'error': str(e)}

    def _analyze_hashtags(self, hashtags: List[str]) -> Dict:
        """Analiza la efectividad de los hashtags utilizados"""
        if not hashtags:
            return {
                'count': 0,
                'effectiveness': 0,
                'suggestions': ['Considera usar hashtags relevantes para aumentar la visibilidad']
            }

        # Análisis básico de hashtags
        count = len(hashtags)
        effectiveness = min(count / 30 * 100, 100)  # 30 hashtags como máximo recomendado

        suggestions = []
        if count < 5:
            suggestions.append('Aumenta el número de hashtags relevantes (5-15 recomendados)')
        elif count > 30:
            suggestions.append('Reduce el número de hashtags (máximo 30 recomendados)')

        return {
            'count': count,
            'effectiveness': round(effectiveness, 2),
            'suggestions': suggestions
        }

    def _analyze_structure(self, content: str) -> Dict:
        """Analiza la estructura del contenido"""
        words = len(content.split())
        sentences = len(TextBlob(content).sentences)
        chars = len(content)

        readability = self._calculate_readability(words, sentences, chars)

        return {
            'length': {
                'words': words,
                'sentences': sentences,
                'chars': chars
            },
            'readability': readability,
            'optimal': 50 <= words <= 200
        }

    def _calculate_readability(self, words: int, sentences: int, chars: int) -> float:
        """Calcula un índice de legibilidad simplificado"""
        if sentences == 0 or words == 0:
            return 0.0

        avg_sentence_length = words / sentences
        avg_word_length = chars / words

        # Índice simplificado (0-100)
        readability = 100 - (avg_sentence_length * 0.5 + avg_word_length * 5)
        return max(0, min(100, readability))

    def _calculate_engagement_score(self, metrics: Dict) -> Dict:
        """Calcula un puntaje de engagement ponderado"""
        total_score = 0
        max_score = 0

        for metric, weight in self.engagement_weights.items():
            if metric in metrics:
                total_score += metrics[metric] * weight
                max_score += weight

        if max_score == 0:
            return {
                'score': 0,
                'level': 'No hay datos suficientes'
            }

        score = (total_score / max_score) * 100
        return {
            'score': round(score, 2),
            'level': self._classify_engagement(score)
        }

    def _classify_sentiment(self, score: float) -> str:
        """Clasifica el sentimiento del contenido"""
        if score > self.sentiment_threshold:
            return 'Positivo'
        elif score < -self.sentiment_threshold:
            return 'Negativo'
        return 'Neutral'

    def _classify_engagement(self, score: float) -> str:
        """Clasifica el nivel de engagement"""
        if score >= 75:
            return 'Excelente'
        elif score >= 50:
            return 'Bueno'
        elif score >= 25:
            return 'Regular'
        return 'Bajo'

    def _generate_recommendations(self, sentiment: float, hashtags: Dict,
                                structure: Dict, engagement: Dict) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        recommendations = []

        # Recomendaciones de sentimiento
        if sentiment < 0:
            recommendations.append(
                'El tono del contenido es negativo. Considera usar un enfoque más positivo '
                'para mejorar la conexión con tu audiencia.'
            )

        # Recomendaciones de estructura
        if not structure['optimal']:
            if structure['length']['words'] < 50:
                recommendations.append(
                    'El contenido es demasiado corto. Agrega más contexto y valor para '
                    'tu audiencia.'
                )
            elif structure['length']['words'] > 200:
                recommendations.append(
                    'El contenido es muy largo. Considera dividirlo en múltiples posts o '
                    'resumir los puntos principales.'
                )

        # Recomendaciones de engagement
        if engagement['score'] < 50:
            recommendations.append(
                'El engagement es bajo. Prueba incluir llamados a la acción más claros y '
                'preguntas para fomentar la participación.'
            )

        # Incluir sugerencias de hashtags
        recommendations.extend(hashtags.get('suggestions', []))

        return recommendations