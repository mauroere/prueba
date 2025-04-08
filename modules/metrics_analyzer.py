from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class EngagementMetrics:
    likes: int = 0
    comments: int = 0
    shares: int = 0
    saves: int = 0
    views: int = 0
    followers: int = 0
    posts: int = 0

    @property
    def engagement_rate(self) -> float:
        """Calcula la tasa de engagement considerando múltiples métricas"""
        if self.followers == 0 or self.posts == 0:
            return 0.0
        
        total_interactions = self.likes + (self.comments * 2) + (self.shares * 3) + (self.saves * 4) + (self.views * 0.1)
        return (total_interactions / self.posts / self.followers) * 100

    @property
    def quality_score(self) -> float:
        """Calcula un puntaje de calidad basado en la proporción de interacciones"""
        total_interactions = self.likes + self.comments + self.shares + self.saves
        if total_interactions == 0:
            return 0.0
        
        weighted_score = (
            (self.comments / total_interactions) * 0.3 +
            (self.shares / total_interactions) * 0.4 +
            (self.saves / total_interactions) * 0.3
        )
        return weighted_score * 100

class MetricsAnalyzer:
    def __init__(self):
        self.metrics_history: Dict[str, List[EngagementMetrics]] = {}

    def add_metrics(self, username: str, metrics: EngagementMetrics) -> None:
        """Agrega métricas nuevas al historial"""
        if username not in self.metrics_history:
            self.metrics_history[username] = []
        self.metrics_history[username].append(metrics)

    def get_growth_rate(self, username: str, days: int = 30) -> Dict[str, float]:
        """Calcula la tasa de crecimiento en diferentes métricas"""
        if username not in self.metrics_history or len(self.metrics_history[username]) < 2:
            return {'error': 'Datos insuficientes para calcular crecimiento'}

        metrics = self.metrics_history[username]
        current = metrics[-1]
        previous = metrics[0]

        return {
            'followers_growth': ((current.followers - previous.followers) / previous.followers) * 100,
            'engagement_growth': current.engagement_rate - previous.engagement_rate,
            'quality_growth': current.quality_score - previous.quality_score
        }

    def analyze_performance(self, username: str) -> Dict:
        """Realiza un análisis completo del rendimiento"""
        if username not in self.metrics_history:
            return {'error': 'No hay datos disponibles para este usuario'}

        metrics = self.metrics_history[username][-1]  # Últimas métricas
        growth = self.get_growth_rate(username)

        performance_score = (
            metrics.engagement_rate * 0.4 +
            metrics.quality_score * 0.3 +
            (growth.get('followers_growth', 0) * 0.3)
        )

        return {
            'current_metrics': {
                'engagement_rate': round(metrics.engagement_rate, 2),
                'quality_score': round(metrics.quality_score, 2),
                'followers': metrics.followers
            },
            'growth_metrics': {
                key: round(value, 2) for key, value in growth.items()
                if not isinstance(value, str)
            },
            'performance_score': round(performance_score, 2),
            'recommendations': self._generate_recommendations(metrics, growth)
        }

    def _generate_recommendations(self, metrics: EngagementMetrics, growth: Dict[str, float]) -> List[str]:
        """Genera recomendaciones basadas en el análisis de métricas"""
        recommendations = []

        # Análisis de engagement
        if metrics.engagement_rate < 3.0:
            recommendations.append(
                'El engagement rate está por debajo del ideal. Considera aumentar la interacción '
                'con tu audiencia y crear contenido más participativo.'
            )

        # Análisis de calidad de interacciones
        if metrics.quality_score < 40:
            recommendations.append(
                'La calidad de las interacciones puede mejorar. Enfócate en generar contenido '
                'que promueva comentarios y compartidos en lugar de solo likes.'
            )

        # Análisis de crecimiento
        if growth.get('followers_growth', 0) < 5:
            recommendations.append(
                'El crecimiento de seguidores es bajo. Considera implementar estrategias de '
                'colaboración y mejorar la visibilidad de tu contenido.'
            )

        # Análisis de balance de métricas
        if metrics.comments / metrics.likes < 0.05:
            recommendations.append(
                'La proporción de comentarios es baja. Intenta incluir llamados a la acción '
                'y preguntas en tus publicaciones para fomentar la conversación.'
            )

        return recommendations