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
                'envios': self._get_shipping_methods(soup)
            }
            return info
        except Exception as e:
            return {'error': str(e)}

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
        recommendations = []

        # Análisis de productos
        avg_products = sum(comp['productos'] for comp in competitor_features) / len(competitor_features) if competitor_features else 0
        if own_features['productos'] < avg_products:
            recommendations.append(f"Considera ampliar tu catálogo. El promedio de productos de la competencia es {avg_products:.0f}")

        # Análisis de redes sociales
        competitor_socials = set()
        for comp in competitor_features:
            competitor_socials.update(comp['redes_sociales'])
        missing_socials = competitor_socials - set(own_features['redes_sociales'])
        if missing_socials:
            recommendations.append(f"Considera crear presencia en: {', '.join(missing_socials)}")

        # Análisis de medios de pago
        competitor_payments = set()
        for comp in competitor_features:
            competitor_payments.update(comp['medios_pago'])
        missing_payments = competitor_payments - set(own_features['medios_pago'])
        if missing_payments:
            recommendations.append(f"Evalúa agregar estos medios de pago: {', '.join(missing_payments)}")

        # Análisis de envíos
        competitor_shipping = set()
        for comp in competitor_features:
            competitor_shipping.update(comp['envios'])
        missing_shipping = competitor_shipping - set(own_features['envios'])
        if missing_shipping:
            recommendations.append(f"Considera ofrecer estos métodos de envío: {', '.join(missing_shipping)}")

        return recommendations