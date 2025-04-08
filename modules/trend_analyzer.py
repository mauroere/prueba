import os
from typing import Dict, List
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .logger_config import LoggerConfig
from .metrics_analyzer import MetricsAnalyzer
from .cache_manager import CacheManager

# Cargar variables de entorno
load_dotenv()

class TrendAnalyzer:
    def __init__(self):
        self.logger = LoggerConfig.get_logger('trend_analyzer')
        self.metrics_analyzer = MetricsAnalyzer()
        self.cache = CacheManager()
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
    def analyze_trends(self, tienda_url: str, historico_data: Dict = None) -> Dict:
        """Analiza tendencias y predice métricas futuras"""
        try:
            # Obtener datos históricos
            if not historico_data:
                historico_data = self._get_historical_data(tienda_url)
            
            # Preparar datos para el modelo
            X, y = self._prepare_data(historico_data)
            
            # Entrenar modelo
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            
            # Generar predicciones
            predictions = self._generate_predictions(X_scaled)
            
            # Identificar tendencias emergentes
            trends = self._identify_trends(historico_data, predictions)
            
            return {
                'predictions': predictions,
                'trends': trends,
                'recommendations': self._generate_recommendations(trends)
            }
        except Exception as e:
            self.logger.error(f'Error en análisis de tendencias: {str(e)}')
            return {'error': str(e)}
    
    def _get_historical_data(self, tienda_url: str) -> Dict:
        """Obtiene datos históricos de la tienda"""
        try:
            # Intentar obtener del caché primero
            cache_key = f'historical_data_{tienda_url}'
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data
            
            # Si no está en caché, obtener métricas históricas
            metrics = self.metrics_analyzer.get_metrics(tienda_url)
            
            # Procesar y estructurar datos
            historical_data = {
                'ventas': metrics.get('ventas_historicas', []),
                'visitas': metrics.get('visitas_historicas', []),
                'conversion': metrics.get('tasa_conversion_historica', []),
                'tendencias_busqueda': metrics.get('tendencias_busqueda', [])
            }
            
            # Guardar en caché
            self.cache.set(cache_key, historical_data)
            
            return historical_data
        except Exception as e:
            self.logger.error(f'Error obteniendo datos históricos: {str(e)}')
            return {}
    
    def _prepare_data(self, historico_data: Dict) -> tuple:
        """Prepara los datos para el modelo predictivo"""
        try:
            # Convertir datos a DataFrame
            df = pd.DataFrame(historico_data)
            
            # Crear features
            X = df[['ventas', 'visitas', 'conversion']].values
            y = df['tendencias_busqueda'].values
            
            return X, y
        except Exception as e:
            self.logger.error(f'Error preparando datos: {str(e)}')
            return np.array([]), np.array([])
    
    def _generate_predictions(self, X_scaled: np.ndarray) -> Dict:
        """Genera predicciones para las próximas semanas"""
        try:
            # Predecir próximas 4 semanas
            future_predictions = self.model.predict(X_scaled[-4:])
            
            # Estructurar predicciones
            dates = [(datetime.now() + timedelta(weeks=i)).strftime('%Y-%m-%d') 
                     for i in range(1, 5)]
            
            return {
                'fechas': dates,
                'valores': future_predictions.tolist()
            }
        except Exception as e:
            self.logger.error(f'Error generando predicciones: {str(e)}')
            return {}
    
    def _identify_trends(self, historico_data: Dict, predictions: Dict) -> List[Dict]:
        """Identifica tendencias emergentes basadas en datos históricos y predicciones"""
        try:
            trends = []
            
            # Analizar cambios significativos
            for metric in ['ventas', 'visitas', 'conversion']:
                if metric in historico_data:
                    current = historico_data[metric][-1]
                    predicted = predictions['valores'][-1]
                    change = ((predicted - current) / current) * 100
                    
                    if abs(change) > 10:  # Cambio significativo > 10%
                        trends.append({
                            'metric': metric,
                            'change': change,
                            'direction': 'up' if change > 0 else 'down'
                        })
            
            return trends
        except Exception as e:
            self.logger.error(f'Error identificando tendencias: {str(e)}')
            return []
    
    def _generate_recommendations(self, trends: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en las tendencias identificadas"""
        recommendations = []
        
        for trend in trends:
            metric = trend['metric']
            direction = trend['direction']
            change = abs(trend['change'])
            
            if metric == 'ventas':
                if direction == 'up':
                    recommendations.append(
                        f'Se prevé un aumento del {change:.1f}% en ventas. '
                        'Considera aumentar el inventario y preparar campañas promocionales.'
                    )
                else:
                    recommendations.append(
                        f'Se prevé una disminución del {change:.1f}% en ventas. '
                        'Considera realizar promociones especiales y revisar la estrategia de precios.'
                    )
            
            elif metric == 'visitas':
                if direction == 'up':
                    recommendations.append(
                        f'Se espera un aumento del {change:.1f}% en el tráfico. '
                        'Optimiza la velocidad del sitio y prepara contenido nuevo.'
                    )
                else:
                    recommendations.append(
                        f'Se prevé una caída del {change:.1f}% en el tráfico. '
                        'Considera invertir en marketing digital y mejorar el SEO.'
                    )
            
            elif metric == 'conversion':
                if direction == 'up':
                    recommendations.append(
                        f'La tasa de conversión podría aumentar un {change:.1f}%. '
                        'Prepara el inventario y optimiza el proceso de checkout.'
                    )
                else:
                    recommendations.append(
                        f'La tasa de conversión podría caer un {change:.1f}%. '
                        'Revisa la usabilidad del sitio y las objeciones de compra comunes.'
                    )
        
        return recommendations