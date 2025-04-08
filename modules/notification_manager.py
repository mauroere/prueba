import os
from typing import Dict, List
from datetime import datetime
import json
from dotenv import load_dotenv
from .logger_config import LoggerConfig
from .metrics_analyzer import MetricsAnalyzer
from .competitor_analyzer import CompetitorAnalyzer
from .trend_analyzer import TrendAnalyzer

# Cargar variables de entorno
load_dotenv()

class NotificationManager:
    def __init__(self):
        self.logger = LoggerConfig.get_logger('notification_manager')
        self.metrics_analyzer = MetricsAnalyzer()
        self.competitor_analyzer = CompetitorAnalyzer()
        self.trend_analyzer = TrendAnalyzer()
        self.notification_types = {
            'metric_alert': 'Alerta de Métrica',
            'competitor_alert': 'Alerta de Competidor',
            'trend_alert': 'Alerta de Tendencia',
            'performance_alert': 'Alerta de Rendimiento'
        }
    
    def check_alerts(self, tienda_url: str) -> List[Dict]:
        """Verifica y genera alertas basadas en diferentes métricas y eventos"""
        try:
            alerts = []
            
            # Verificar alertas de métricas
            metric_alerts = self._check_metric_alerts(tienda_url)
            alerts.extend(metric_alerts)
            
            # Verificar alertas de competidores
            competitor_alerts = self._check_competitor_alerts(tienda_url)
            alerts.extend(competitor_alerts)
            
            # Verificar alertas de tendencias
            trend_alerts = self._check_trend_alerts(tienda_url)
            alerts.extend(trend_alerts)
            
            # Verificar alertas de rendimiento
            performance_alerts = self._check_performance_alerts(tienda_url)
            alerts.extend(performance_alerts)
            
            return self._format_alerts(alerts)
        except Exception as e:
            self.logger.error(f'Error verificando alertas: {str(e)}')
            return []
    
    def _check_metric_alerts(self, tienda_url: str) -> List[Dict]:
        """Verifica alertas relacionadas con métricas clave"""
        try:
            alerts = []
            metrics = self.metrics_analyzer.get_metrics(tienda_url)
            
            # Verificar cambios significativos en métricas
            for metric, value in metrics.items():
                if isinstance(value, (int, float)):
                    threshold = self._get_metric_threshold(metric)
                    if abs(value) > threshold:
                        alerts.append({
                            'type': 'metric_alert',
                            'metric': metric,
                            'value': value,
                            'threshold': threshold,
                            'timestamp': datetime.now().isoformat()
                        })
            
            return alerts
        except Exception as e:
            self.logger.error(f'Error en alertas de métricas: {str(e)}')
            return []
    
    def _check_competitor_alerts(self, tienda_url: str) -> List[Dict]:
        """Verifica alertas relacionadas con actividades de competidores"""
        try:
            alerts = []
            competitor_data = self.competitor_analyzer._get_store_info(tienda_url)
            
            # Verificar cambios en competidores
            if 'error' not in competitor_data:
                for key, value in competitor_data.items():
                    if self._is_significant_change(key, value):
                        alerts.append({
                            'type': 'competitor_alert',
                            'change_type': key,
                            'details': value,
                            'timestamp': datetime.now().isoformat()
                        })
            
            return alerts
        except Exception as e:
            self.logger.error(f'Error en alertas de competidores: {str(e)}')
            return []
    
    def _check_trend_alerts(self, tienda_url: str) -> List[Dict]:
        """Verifica alertas relacionadas con tendencias emergentes"""
        try:
            alerts = []
            trend_data = self.trend_analyzer.analyze_trends(tienda_url)
            
            if 'error' not in trend_data:
                for trend in trend_data.get('trends', []):
                    if abs(trend.get('change', 0)) > 15:  # Cambio significativo > 15%
                        alerts.append({
                            'type': 'trend_alert',
                            'trend_type': trend['metric'],
                            'change': trend['change'],
                            'direction': trend['direction'],
                            'timestamp': datetime.now().isoformat()
                        })
            
            return alerts
        except Exception as e:
            self.logger.error(f'Error en alertas de tendencias: {str(e)}')
            return []
    
    def _check_performance_alerts(self, tienda_url: str) -> List[Dict]:
        """Verifica alertas relacionadas con el rendimiento de la tienda"""
        try:
            alerts = []
            metrics = self.metrics_analyzer.get_metrics(tienda_url)
            
            # Verificar métricas de rendimiento
            performance_metrics = {
                'tiempo_carga': metrics.get('tiempo_carga', 0),
                'tasa_rebote': metrics.get('tasa_rebote', 0),
                'tasa_error': metrics.get('tasa_error', 0)
            }
            
            for metric, value in performance_metrics.items():
                threshold = self._get_performance_threshold(metric)
                if value > threshold:
                    alerts.append({
                        'type': 'performance_alert',
                        'metric': metric,
                        'value': value,
                        'threshold': threshold,
                        'timestamp': datetime.now().isoformat()
                    })
            
            return alerts
        except Exception as e:
            self.logger.error(f'Error en alertas de rendimiento: {str(e)}')
            return []
    
    def _get_metric_threshold(self, metric: str) -> float:
        """Obtiene el umbral para una métrica específica"""
        thresholds = {
            'ventas': 1000,
            'visitas': 500,
            'conversion': 5,
            'abandono_carrito': 30
        }
        return thresholds.get(metric, 0)
    
    def _get_performance_threshold(self, metric: str) -> float:
        """Obtiene el umbral para una métrica de rendimiento específica"""
        thresholds = {
            'tiempo_carga': 3.0,  # segundos
            'tasa_rebote': 60,    # porcentaje
            'tasa_error': 5       # porcentaje
        }
        return thresholds.get(metric, 0)
    
    def _is_significant_change(self, key: str, value: any) -> bool:
        """Determina si un cambio en una métrica es significativo"""
        significant_changes = {
            'precio': 10,  # cambio de precio > 10%
            'stock': 50,   # cambio de stock > 50 unidades
            'rating': 0.5  # cambio en calificación > 0.5 puntos
        }
        return abs(float(value)) > significant_changes.get(key, 0) if isinstance(value, (int, float)) else False
    
    def _format_alerts(self, alerts: List[Dict]) -> List[Dict]:
        """Formatea las alertas para su presentación"""
        formatted_alerts = []
        
        for alert in alerts:
            alert_type = alert.get('type')
            formatted_alert = {
                'title': self.notification_types.get(alert_type, 'Alerta'),
                'message': self._generate_alert_message(alert),
                'timestamp': alert.get('timestamp'),
                'priority': self._get_alert_priority(alert),
                'actions': self._get_alert_actions(alert)
            }
            formatted_alerts.append(formatted_alert)
        
        return formatted_alerts
    
    def _generate_alert_message(self, alert: Dict) -> str:
        """Genera un mensaje descriptivo para la alerta"""
        alert_type = alert.get('type')
        
        if alert_type == 'metric_alert':
            return f"La métrica {alert['metric']} ha superado el umbral de {alert['threshold']} con un valor de {alert['value']}"
        
        elif alert_type == 'competitor_alert':
            return f"Se detectó un cambio importante en {alert['change_type']} de un competidor: {alert['details']}"
        
        elif alert_type == 'trend_alert':
            direction = 'aumento' if alert['direction'] == 'up' else 'disminución'
            return f"Se detectó un {direction} del {abs(alert['change']):.1f}% en {alert['trend_type']}"
        
        elif alert_type == 'performance_alert':
            return f"El rendimiento de {alert['metric']} está por encima del umbral: {alert['value']} (máx. {alert['threshold']})"
        
        return "Alerta sin mensaje específico"
    
    def _get_alert_priority(self, alert: Dict) -> str:
        """Determina la prioridad de la alerta"""
        if alert.get('type') == 'performance_alert':
            return 'alta' if alert.get('value', 0) > alert.get('threshold', 0) * 1.5 else 'media'
        
        elif alert.get('type') == 'trend_alert':
            return 'alta' if abs(alert.get('change', 0)) > 25 else 'media'
        
        return 'baja'
    
    def _get_alert_actions(self, alert: Dict) -> List[Dict]:
        """Define las acciones disponibles para cada tipo de alerta"""
        actions = [{
            'name': 'ver_detalles',
            'label': 'Ver Detalles',
            'url': f"/alertas/{alert.get('type')}/{alert.get('timestamp')}"
        }]
        
        if alert.get('type') == 'performance_alert':
            actions.append({
                'name': 'optimizar',
                'label': 'Optimizar Ahora',
                'url': f"/optimizacion/{alert.get('metric')}"
            })
        
        elif alert.get('type') == 'competitor_alert':
            actions.append({
                'name': 'analizar_competencia',
                'label': 'Analizar Competencia',
                'url': '/analisis-competencia'
            })
        
        return actions