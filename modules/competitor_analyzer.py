import json
import re
import os
from typing import Dict, List
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from .cache_manager import CacheManager
from .metrics_analyzer import MetricsAnalyzer
from .logger_config import LoggerConfig

# Cargar variables de entorno
load_dotenv()

class CompetitorAnalyzer:
    def __init__(self):
        try:
            # Configurar logger
            self.logger = LoggerConfig.get_logger('competitor_analyzer')
            self.logger.info('Inicializando CompetitorAnalyzer')
            
            # Configurar servicios y opciones
            self.ua = UserAgent()
            self.chrome_options = Options()
            self.chrome_options.add_argument('--headless')
            self.chrome_options.add_argument('--no-sandbox')
            self.chrome_options.add_argument('--disable-dev-shm-usage')
            self.chrome_options.add_argument('--disable-gpu')
            self.chrome_options.add_argument('--window-size=1920x1080')
            
            # Configurar cliente y parámetros
            self.client = InferenceClient(token=os.getenv('HUGGINGFACE_API_KEY'))
            self.max_retries = int(os.getenv('MAX_RETRIES', 3))
            self.request_timeout = int(os.getenv('SELENIUM_TIMEOUT', 15))
            self.cache = CacheManager(expiration_minutes=int(os.getenv('CACHE_EXPIRATION_MINUTES', 120)))
            self.metrics_analyzer = MetricsAnalyzer()
            
            # Configurar API de Tiendanube
            self.tiendanube_api_url = os.getenv('TIENDANUBE_API_URL')
            self.tiendanube_app_id = os.getenv('TIENDANUBE_APP_ID')
            self.tiendanube_client_secret = os.getenv('TIENDANUBE_CLIENT_SECRET')
            
            self.logger.info('CompetitorAnalyzer inicializado correctamente')
        except Exception as e:
            self.logger.error(f"Error al inicializar CompetitorAnalyzer: {str(e)}")
            raise Exception(f"Error al inicializar CompetitorAnalyzer: {str(e)}")

    def _get_tiendanube_store_info(self, store_id: str) -> Dict:
        """Obtiene información detallada de una tienda usando la API de Tiendanube"""
        try:
            headers = {
                'Authentication': f'Bearer {self.tiendanube_client_secret}',
                'User-Agent': self.ua.random
            }
            
            # Obtener información básica de la tienda
            store_url = f"{self.tiendanube_api_url}/store/{store_id}"
            response = requests.get(store_url, headers=headers)
            store_data = response.json()
            
            # Obtener productos y precios históricos
            products_url = f"{self.tiendanube_api_url}/store/{store_id}/products"
            products_response = requests.get(products_url, headers=headers)
            products_data = products_response.json()
            
            # Analizar tendencias de precios
            price_trends = self._analyze_price_trends(products_data)
            
            return {
                'store_info': store_data,
                'price_trends': price_trends,
                'competitive_score': self._calculate_competitive_score(store_data, products_data)
            }
        except Exception as e:
            self.logger.error(f"Error al obtener información de Tiendanube: {str(e)}")
            return {'error': str(e)}

    def _analyze_price_trends(self, products_data: List[Dict]) -> Dict:
        """Analiza tendencias históricas de precios y genera predicciones"""
        try:
            price_data = {
                'current_avg': 0,
                'historical_trend': [],
                'price_prediction': None,
                'price_volatility': 0
            }
            
            if not products_data:
                return price_data
                
            # Calcular promedio actual y tendencias
            prices = [float(p['price']) for p in products_data if 'price' in p]
            if prices:
                price_data['current_avg'] = sum(prices) / len(prices)
                price_data['price_volatility'] = self._calculate_price_volatility(prices)
                
                # Analizar tendencia histórica (últimos 30 días)
                historical_prices = self._get_historical_prices(products_data)
                price_data['historical_trend'] = historical_prices
                
                # Generar predicción simple para próximos 7 días
                if len(historical_prices) >= 7:
                    price_data['price_prediction'] = self._predict_future_prices(historical_prices)
            
            return price_data
        except Exception as e:
            self.logger.error(f"Error al analizar tendencias de precios: {str(e)}")
            return price_data

    def _calculate_competitive_score(self, store_data: Dict, products_data: List[Dict]) -> Dict:
        """Calcula una puntuación competitiva basada en múltiples factores"""
        try:
            scores = {
                'overall_score': 0,
                'categories': {
                    'product_variety': 0,
                    'pricing_strategy': 0,
                    'social_presence': 0,
                    'customer_service': 0
                },
                'strengths': [],
                'weaknesses': []
            }
            
            # Evaluar variedad de productos
            product_score = min(len(products_data) / 100, 1) * 100
            scores['categories']['product_variety'] = product_score
            
            # Evaluar estrategia de precios
            price_score = self._evaluate_pricing_strategy(products_data)
            scores['categories']['pricing_strategy'] = price_score
            
            # Evaluar presencia en redes sociales
            social_score = self._evaluate_social_presence(store_data)
            scores['categories']['social_presence'] = social_score
            
            # Evaluar servicio al cliente
            service_score = self._evaluate_customer_service(store_data)
            scores['categories']['customer_service'] = service_score
            
            # Calcular puntuación general
            scores['overall_score'] = sum(scores['categories'].values()) / len(scores['categories'])
            
            # Identificar fortalezas y debilidades
            for category, score in scores['categories'].items():
                if score >= 75:
                    scores['strengths'].append(category)
                elif score <= 40:
                    scores['weaknesses'].append(category)
            
            return scores
        except Exception as e:
            self.logger.error(f"Error al calcular puntuación competitiva: {str(e)}")
            return {'overall_score': 0, 'categories': {}, 'strengths': [], 'weaknesses': []}

    def _calculate_price_volatility(self, prices: List[float]) -> float:
        """Calcula la volatilidad de precios usando desviación estándar"""
        try:
            if len(prices) < 2:
                return 0
                
            import numpy as np
            return float(np.std(prices) / np.mean(prices) * 100)
        except Exception as e:
            self.logger.error(f"Error al calcular volatilidad de precios: {str(e)}")
            return 0
    
    def _get_historical_prices(self, products_data: List[Dict]) -> List[Dict]:
        """Obtiene el historial de precios de los últimos 30 días"""
        try:
            historical_prices = []
            for product in products_data:
                if 'price_history' in product:
                    for date, price in product['price_history'].items():
                        historical_prices.append({
                            'date': date,
                            'price': float(price)
                        })
            
            # Ordenar por fecha y limitar a 30 días
            from datetime import datetime, timedelta
            cutoff_date = datetime.now() - timedelta(days=30)
            return sorted(
                [p for p in historical_prices if datetime.strptime(p['date'], '%Y-%m-%d') >= cutoff_date],
                key=lambda x: x['date']
            )
        except Exception as e:
            self.logger.error(f"Error al obtener historial de precios: {str(e)}")
            return []
    
    def _predict_future_prices(self, historical_prices: List[Dict]) -> List[Dict]:
        """Predice precios futuros usando regresión lineal simple"""
        try:
            from sklearn.linear_model import LinearRegression
            import numpy as np
            from datetime import datetime, timedelta
            
            # Preparar datos para la regresión
            X = np.array(range(len(historical_prices))).reshape(-1, 1)
            y = np.array([p['price'] for p in historical_prices])
            
            # Entrenar modelo
            model = LinearRegression()
            model.fit(X, y)
            
            # Predecir próximos 7 días
            future_dates = []
            last_date = datetime.strptime(historical_prices[-1]['date'], '%Y-%m-%d')
            for i in range(1, 8):
                future_date = last_date + timedelta(days=i)
                prediction = model.predict([[len(historical_prices) + i - 1]])[0]
                future_dates.append({
                    'date': future_date.strftime('%Y-%m-%d'),
                    'predicted_price': max(0, float(prediction))
                })
            
            return future_dates
        except Exception as e:
            self.logger.error(f"Error al predecir precios futuros: {str(e)}")
            return []
    
    def _evaluate_pricing_strategy(self, products_data: List[Dict]) -> float:
        """Evalúa la estrategia de precios considerando múltiples factores"""
        try:
            if not products_data:
                return 0
                
            score = 0
            total_factors = 4
            
            # Factor 1: Variabilidad de precios
            prices = [float(p['price']) for p in products_data if 'price' in p]
            price_volatility = self._calculate_price_volatility(prices)
            if price_volatility < 20:  # Precios estables
                score += 25
            
            # Factor 2: Rango de precios competitivo
            if prices:
                avg_price = sum(prices) / len(prices)
                if 100 <= avg_price <= 1000:  # Rango medio
                    score += 25
            
            # Factor 3: Descuentos y promociones
            discount_count = sum(1 for p in products_data if p.get('discount_price'))
            if 0.1 <= discount_count / len(products_data) <= 0.3:  # 10-30% productos con descuento
                score += 25
            
            # Factor 4: Consistencia en precios similares
            categories = {}
            for product in products_data:
                cat = product.get('category', 'other')
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(float(product['price']))
            
            category_consistency = 0
            for prices in categories.values():
                if len(prices) > 1:
                    volatility = self._calculate_price_volatility(prices)
                    if volatility < 15:  # Precios consistentes dentro de categoría
                        category_consistency += 1
            
            if categories and category_consistency / len(categories) >= 0.7:
                score += 25
            
            return score
        except Exception as e:
            self.logger.error(f"Error al evaluar estrategia de precios: {str(e)}")
            return 0
    
    def _evaluate_social_presence(self, store_data: Dict) -> float:
        """Evalúa la presencia en redes sociales"""
        try:
            score = 0
            social_networks = store_data.get('social_networks', {})
            
            # Evaluar presencia en cada red social principal
            platforms = ['facebook', 'instagram', 'twitter', 'tiktok']
            for platform in platforms:
                if platform in social_networks:
                    score += 15  # Puntos base por presencia
                    
                    # Puntos adicionales por actividad
                    if social_networks[platform].get('followers', 0) > 1000:
                        score += 5
                    if social_networks[platform].get('posts_last_month', 0) > 4:
                        score += 5
            
            return min(score, 100)
        except Exception as e:
            self.logger.error(f"Error al evaluar presencia social: {str(e)}")
            return 0
    
    def _evaluate_customer_service(self, store_data: Dict) -> float:
        """Evalúa la calidad del servicio al cliente"""
        try:
            score = 0
            service_data = store_data.get('customer_service', {})
            
            # Factor 1: Tiempo de respuesta
            response_time = service_data.get('avg_response_time', 0)
            if response_time <= 1:  # 1 hora o menos
                score += 25
            elif response_time <= 4:
                score += 15
            
            # Factor 2: Calificación de clientes
            rating = service_data.get('customer_rating', 0)
            if rating >= 4.5:
                score += 25
            elif rating >= 4.0:
                score += 15
            
            # Factor 3: Canales de atención
            channels = service_data.get('support_channels', [])
            if len(channels) >= 3:
                score += 25
            elif len(channels) >= 2:
                score += 15
            
            # Factor 4: Políticas de devolución
            if service_data.get('has_return_policy', False):
                score += 25
            
            return score
        except Exception as e:
            self.logger.error(f"Error al evaluar servicio al cliente: {str(e)}")
            return 0
    
    def _get_store_info(self, url: str) -> Dict:
        """Obtiene información básica de una tienda"""
        if not url or not isinstance(url, str):
            return {'error': 'URL inválida'}
            
        if not url.startswith(('http://', 'https://')):
            return {'error': 'URL debe comenzar con http:// o https://'}

        # Intentar obtener del caché primero
        cached_info = self.cache.get(url)
        if cached_info:
            return cached_info
            
        for attempt in range(self.max_retries):
            try:
                headers = {'User-Agent': self.ua.random}
                response = requests.get(url, headers=headers, timeout=self.request_timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                try:
                    info = {
                        'nombre': soup.find('meta', property='og:site_name')['content'] if soup.find('meta', property='og:site_name') else '',
                        'descripcion': soup.find('meta', property='og:description')['content'] if soup.find('meta', property='og:description') else '',
                        'productos': len(soup.find_all('div', class_='item-product')) if soup.find_all('div', class_='item-product') else 0,
                        'categorias': len(soup.find_all('a', class_='item-category')) if soup.find_all('a', class_='item-category') else 0,
                        'redes_sociales': self._get_social_links(soup),
                        'medios_pago': self._get_payment_methods(soup),
                        'envios': self._get_shipping_methods(soup),
                        'envio_gratis': bool(soup.find(text=lambda t: 'envío gratis' in t.lower() if t else False)),
                        'rango_precios': self._get_price_range(soup),
                        'tiene_descuentos': bool(soup.find(text=lambda t: 'descuento' in t.lower() if t else False)),
                        'tiene_chat': bool(soup.find(text=lambda t: 'chat' in t.lower() if t else False)),
                        'tiene_blog': bool(soup.find('a', href=lambda h: 'blog' in h.lower() if h else False)),
                        'tiene_wishlist': bool(soup.find(text=lambda t: 'wishlist' in t.lower() or 'favoritos' in t.lower() if t else False)),
                        'tiene_reviews': bool(soup.find(text=lambda t: 'review' in t.lower() or 'opiniones' in t.lower() if t else False)),
                        'tiene_meta_desc': bool(soup.find('meta', {'name': 'description'})),
                        'tiene_alt_imgs': bool(soup.find('img', alt=True))
                    }
                    # Almacenar en caché antes de retornar
                    self.cache.set(url, info)
                    return info
                except Exception as e:
                    return {'error': f'Error al procesar el HTML: {str(e)}'}
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    return {'error': f'Error al obtener información de la tienda: {str(e)}'}
                time.sleep(2 ** attempt)  # Backoff exponencial
        return {'error': 'Máximo número de intentos alcanzado'}

    def _get_social_links(self, soup: BeautifulSoup) -> List[str]:
        """Extrae enlaces a redes sociales"""
        social_patterns = {
            'facebook': r'facebook\.com',
            'instagram': r'instagram\.com',
            'twitter': r'twitter\.com',
            'tiktok': r'tiktok\.com'
        }
        
        social_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            for platform, pattern in social_patterns.items():
                if re.search(pattern, href, re.I):
                    social_links.append(platform)
        return list(set(social_links))

    def _get_payment_methods(self, soup: BeautifulSoup) -> List[str]:
        """Extrae métodos de pago disponibles"""
        payment_methods = []
        payment_section = soup.find('div', class_=re.compile(r'payment-methods|medios-pago'))
        if payment_section:
            payment_methods = [img['alt'] for img in payment_section.find_all('img', alt=True)]
        return payment_methods

    def _get_price_range(self, soup) -> Dict:
        """Obtiene el rango de precios de los productos"""
        prices = []
        price_elements = soup.find_all('span', {'class': 'price'})
        for price in price_elements:
            try:
                # Limpia y convierte el precio a número
                price_text = price.text.strip().replace('$', '').replace('.', '').replace(',', '.')
                prices.append(float(price_text))
            except ValueError:
                continue
        
        if prices:
            return {
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices)
            }
        return {'min': 0, 'max': 0, 'avg': 0}

    def _get_shipping_methods(self, soup: BeautifulSoup) -> List[str]:
        """Extrae métodos de envío disponibles"""
        shipping_methods = []
        shipping_section = soup.find('div', class_=re.compile(r'shipping-methods|metodos-envio'))
        if shipping_section:
            shipping_methods = [method.text.strip() for method in shipping_section.find_all(['span', 'p'])]
        return shipping_methods

    def _find_competitors(self, nicho: str) -> List[str]:
        """Encuentra URLs de tiendas competidoras en Tiendanube"""
        try:
            search_url = f"https://www.tiendanube.com/tiendas/{nicho}"
            headers = {'User-Agent': self.ua.random}
            response = requests.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            competitor_urls = []
            for store in soup.find_all('div', class_='store-card')[:5]:  # Limitamos a 5 competidores
                if link := store.find('a', href=True):
                    competitor_urls.append(link['href'])
            return competitor_urls
        except Exception:
            return []

    def analyze_competition(self, tienda_url: str, nicho: str) -> Dict:
        """Analiza la competencia y genera recomendaciones"""
        try:
            # Validar parámetros de entrada
            if not tienda_url or not isinstance(tienda_url, str):
                return {'error': 'URL de tienda inválida'}
            if not nicho or not isinstance(nicho, str):
                return {'error': 'Nicho inválido'}

            # Analizar tienda propia
            own_features = self._get_store_info(tienda_url)
            if 'error' in own_features:
                return {'error': f'No se pudo analizar tu tienda: {own_features["error"]}'}

            # Encontrar y analizar competidores
            competitor_urls = self._find_competitors(nicho)
            if not competitor_urls:
                return {'error': 'No se encontraron competidores para analizar'}

            competitor_features = []
            for url in competitor_urls:
                info = self._get_store_info(url)
                if 'error' not in info:
                    competitor_features.append(info)

            if not competitor_features:
                return {'error': 'No se pudo obtener información de los competidores'}

            # Generar recomendaciones
            recommendations = self._generate_recommendations(own_features, competitor_features)
            if isinstance(recommendations, dict) and 'error' in recommendations:
                return recommendations

            return {
                'own_features': own_features,
                'competitor_features': competitor_features,
                'recommendations': recommendations
            }
        except Exception as e:
            return {'error': f'Error al analizar la competencia: {str(e)}'}

    def _generate_recommendations(self, own_features: Dict, competitor_features: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en el análisis comparativo"""
        try:
            # Validación de tipos de datos
            if not own_features or not isinstance(own_features, dict):
                return {'error': 'Características propias inválidas o no proporcionadas'}
                
            if not competitor_features or not isinstance(competitor_features, list):
                return {'error': 'Características de competidores inválidas o no proporcionadas'}
            
            # Campos requeridos y sus tipos esperados
            required_fields = {
                'productos': (int, float),
                'redes_sociales': list,
                'medios_pago': list,
                'envios': list
            }
            
            # Validar campos y tipos en own_features
            for field, expected_type in required_fields.items():
                if field not in own_features:
                    return {'error': f'Campo requerido faltante en características propias: {field}'}
                if not isinstance(own_features[field], expected_type):
                    return {'error': f'Tipo de dato inválido en características propias para {field}'}
            
            # Validar campos y tipos en competitor_features
            for i, comp in enumerate(competitor_features):
                if not isinstance(comp, dict):
                    return {'error': f'Competidor {i+1} no es un diccionario válido'}
                
                for field, expected_type in required_fields.items():
                    if field not in comp:
                        return {'error': f'Campo requerido faltante en competidor {i+1}: {field}'}
                    if not isinstance(comp[field], expected_type):
                        return {'error': f'Tipo de dato inválido en competidor {i+1} para {field}'}
            
            recommendations = []

            # Análisis de productos con validación
            try:
                valid_products = [comp['productos'] for comp in competitor_features 
                                if isinstance(comp['productos'], (int, float)) and comp['productos'] > 0]
                
                if not valid_products:
                    return {'error': 'No hay datos válidos de productos para analizar'}
                    
                avg_products = sum(valid_products) / len(valid_products)
                if own_features['productos'] < avg_products:
                    recommendations.append(
                        f"Considera ampliar tu catálogo. El promedio de productos de la "
                        f"competencia es {avg_products:.0f}"
                    )
            except Exception as e:
                return {'error': f'Error en análisis de productos: {str(e)}'}

            # Análisis de redes sociales con validación
            try:
                competitor_socials = set()
                for comp in competitor_features:
                    if isinstance(comp['redes_sociales'], list):
                        competitor_socials.update(comp['redes_sociales'])
                
                if competitor_socials and isinstance(own_features['redes_sociales'], list):
                    missing_socials = competitor_socials - set(own_features['redes_sociales'])
                    if missing_socials:
                        recommendations.append(
                            f"Considera crear presencia en las siguientes redes sociales: "
                            f"{', '.join(sorted(missing_socials))}"
                        )
            except Exception as e:
                return {'error': f'Error en análisis de redes sociales: {str(e)}'}

            # Análisis de medios de pago con validación
            try:
                competitor_payments = set()
                for comp in competitor_features:
                    if isinstance(comp['medios_pago'], list):
                        competitor_payments.update(comp['medios_pago'])
                
                if competitor_payments and isinstance(own_features['medios_pago'], list):
                    missing_payments = competitor_payments - set(own_features['medios_pago'])
                    if missing_payments:
                        recommendations.append(
                            f"Evalúa agregar estos medios de pago para mejorar la experiencia "
                            f"de compra: {', '.join(sorted(missing_payments))}"
                        )
            except Exception as e:
                return {'error': f'Error en análisis de medios de pago: {str(e)}'}

            # Análisis de envíos con validación
            try:
                competitor_shipping = set()
                for comp in competitor_features:
                    if isinstance(comp['envios'], list):
                        competitor_shipping.update(comp['envios'])
                
                if competitor_shipping and isinstance(own_features['envios'], list):
                    missing_shipping = competitor_shipping - set(own_features['envios'])
                    if missing_shipping:
                        recommendations.append(
                            f"Considera ofrecer estos métodos de envío para mejorar tu "
                            f"servicio: {', '.join(sorted(missing_shipping))}"
                        )
            except Exception as e:
                return {'error': f'Error en análisis de envíos: {str(e)}'}

            # Si no hay recomendaciones, agregar mensaje por defecto
            if not recommendations:
                recommendations.append(
                    "Tu negocio está bien posicionado en comparación con la competencia. "
                    "Continúa monitoreando el mercado para mantener tu ventaja competitiva."
                )

            return recommendations
            
        except Exception as e:
            return {'error': f'Error general al generar recomendaciones: {str(e)}'}
            
        # Validar campos requeridos en competitor_features
        for i, comp in enumerate(competitor_features):
            if not isinstance(comp, dict):
                raise ValueError(f'Competidor {i+1} no es un diccionario válido')
            missing_comp = [field for field in required_fields if field not in comp]
            if missing_comp:
                raise ValueError(f'Campos faltantes en competidor {i+1}: {", ".join(missing_comp)}')
        
        recommendations = []

        try:
            # Análisis de productos
            valid_products = [comp['productos'] for comp in competitor_features 
                            if isinstance(comp['productos'], (int, float)) and comp['productos'] > 0]
            
            if valid_products:
                avg_products = sum(valid_products) / len(valid_products)
                if own_features['productos'] < avg_products:
                    recommendations.append(
                        f"Considera ampliar tu catálogo. El promedio de productos de la "
                        f"competencia es {avg_products:.0f}"
                    )

            # Análisis de redes sociales
            competitor_socials = set()
            for comp in competitor_features:
                if isinstance(comp['redes_sociales'], (list, set)):
                    competitor_socials.update(comp['redes_sociales'])
            
            if competitor_socials:
                missing_socials = competitor_socials - set(own_features['redes_sociales'])
                if missing_socials:
                    recommendations.append(
                        f"Considera crear presencia en las siguientes redes sociales: "
                        f"{', '.join(sorted(missing_socials))}"
                    )

            # Análisis de medios de pago
            competitor_payments = set()
            for comp in competitor_features:
                if isinstance(comp['medios_pago'], (list, set)):
                    competitor_payments.update(comp['medios_pago'])
            
            if competitor_payments:
                missing_payments = competitor_payments - set(own_features['medios_pago'])
                if missing_payments:
                    recommendations.append(
                        f"Evalúa agregar estos medios de pago para mejorar la experiencia "
                        f"de compra: {', '.join(sorted(missing_payments))}"
                    )

            # Análisis de envíos
            competitor_shipping = set()
            for comp in competitor_features:
                if isinstance(comp['envios'], (list, set)):
                    competitor_shipping.update(comp['envios'])
            
            if competitor_shipping:
                missing_shipping = competitor_shipping - set(own_features['envios'])
                if missing_shipping:
                    recommendations.append(
                        f"Considera ofrecer estos métodos de envío para mejorar tu "
                        f"servicio: {', '.join(sorted(missing_shipping))}"
                    )

            # Si no hay recomendaciones, agregar mensaje por defecto
            if not recommendations:
                recommendations.append(
                    "Tu negocio está bien posicionado en comparación con la competencia. "
                    "Continúa monitoreando el mercado para mantener tu ventaja competitiva."
                )

            return recommendations
            
        except Exception as e:
            raise Exception(f'Error al generar recomendaciones: {str(e)}')