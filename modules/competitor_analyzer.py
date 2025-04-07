from typing import Dict, List
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import json
import re

class CompetitorAnalyzer:
    def __init__(self):
        self.ua = UserAgent()
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.client = InferenceClient()

    def _get_store_info(self, url: str) -> Dict:
        """Obtiene información básica de una tienda"""
        try:
            headers = {'User-Agent': self.ua.random}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
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
            return info
        except Exception as e:
            return {'error': str(e)}

<<<<<<< HEAD
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
=======
    def _get_price_range(self, soup) -> Dict:
        """Obtiene el rango de precios de los productos"""
        prices = []
        price_elements = soup.find_all('span', {'class': 'price'})
        for price in price_elements:
            try:
                # Limpia y convierte el precio a número
                price_text = price.text.strip().replace('$', '').replace('.', '').replace(',', '.')
                prices.append(float(price_text))
            except:
                continue
        
        if prices:
            return {
                'min': min(prices),
                'max': max(prices),
                'avg': sum(prices) / len(prices)
            }
        return {'min': 0, 'max': 0, 'avg': 0}

    def _generate_recommendations(self, competitor_features: List[Dict], own_features: Dict) -> str:
        """Genera recomendaciones detalladas basadas en el análisis comparativo"""
        prompt = f"Analiza estas características de tiendas competidoras y genera recomendaciones estratégicas detalladas:\n"
        prompt += f"Características de tu tienda:\n{str(own_features)}\n"
        prompt += f"Características de competidores:\n{str(competitor_features)}\n"
        prompt += """Genera recomendaciones específicas y accionables en las siguientes áreas:
        1. Estrategia de precios y promociones
        2. Características y funcionalidades de la tienda
        3. Experiencia del usuario y servicio al cliente
        4. Estrategia de contenido y SEO
        5. Ventajas competitivas a desarrollar"""
>>>>>>> 18f8dc7e79c292e1fb3cab334f99a7f41d7fcbc9

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
            # Analizar tienda propia
            own_features = self._get_store_info(tienda_url)
            if 'error' in own_features:
                return {'error': 'No se pudo analizar tu tienda'}

            # Encontrar y analizar competidores
            competitor_urls = self._find_competitors(nicho)
            competitor_features = []
            for url in competitor_urls:
                info = self._get_store_info(url)
                if 'error' not in info:
                    competitor_features.append(info)

            # Generar recomendaciones
            recommendations = self._generate_recommendations(own_features, competitor_features)

            return {
                'own_features': own_features,
                'competitor_features': competitor_features,
                'recommendations': recommendations
            }
        except Exception as e:
            return {'error': str(e)}

    def _generate_recommendations(self, own_features: Dict, competitor_features: List[Dict]) -> List[str]:
        """Genera recomendaciones basadas en el análisis comparativo"""
        if not own_features or not isinstance(own_features, dict):
            raise ValueError('Características propias inválidas o no proporcionadas')
            
        if not competitor_features or not isinstance(competitor_features, list):
            raise ValueError('Características de competidores inválidas o no proporcionadas')
            
        required_fields = ['productos', 'redes_sociales', 'medios_pago', 'envios']
        
        # Validar campos requeridos en own_features
        missing_own = [field for field in required_fields if field not in own_features]
        if missing_own:
            raise ValueError(f'Campos faltantes en características propias: {", ".join(missing_own)}')
            
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