import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from huggingface_hub import InferenceClient

class CompetitorAnalyzer:
    def __init__(self):
        self.client = InferenceClient()

    def _get_competitor_urls(self, nicho: str) -> List[str]:
        """Simula la búsqueda de competidores en Tiendanube basado en el nicho"""
        # En una implementación real, esto utilizaría una API o web scraping más sofisticado
        # Por ahora, retornamos una lista de ejemplo
        return [
            f"https://tienda1-{nicho}.mitiendanube.com",
            f"https://tienda2-{nicho}.mitiendanube.com",
            f"https://tienda3-{nicho}.mitiendanube.com"
        ]

    def _analyze_competitor_site(self, url: str) -> Dict:
        """Analiza una tienda competidora de forma detallada"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Análisis básico de características
            features = {
                'envio_gratis': bool(soup.find(text=lambda t: 'envío gratis' in t.lower() if t else False)),
                'medios_pago': len(soup.find_all('img', {'class': 'payment-logo'})) if soup.find_all('img', {'class': 'payment-logo'}) else 0,
                'redes_sociales': len(soup.find_all('a', {'class': 'social'})) if soup.find_all('a', {'class': 'social'}) else 0,
                'productos': len(soup.find_all('div', {'class': 'product-box'})) if soup.find_all('div', {'class': 'product-box'}) else 0,
                
                # Análisis de precios
                'rango_precios': self._get_price_range(soup),
                'tiene_descuentos': bool(soup.find(text=lambda t: 'descuento' in t.lower() if t else False)),
                
                # Características adicionales
                'tiene_chat': bool(soup.find(text=lambda t: 'chat' in t.lower() if t else False)),
                'tiene_blog': bool(soup.find('a', href=lambda h: 'blog' in h.lower() if h else False)),
                'tiene_wishlist': bool(soup.find(text=lambda t: 'wishlist' in t.lower() or 'favoritos' in t.lower() if t else False)),
                'tiene_reviews': bool(soup.find(text=lambda t: 'review' in t.lower() or 'opiniones' in t.lower() if t else False)),
                
                # SEO básico
                'tiene_meta_desc': bool(soup.find('meta', {'name': 'description'})),
                'tiene_alt_imgs': bool(soup.find('img', alt=True))
            }
            return features
        except Exception as e:
            return {'error': str(e)}

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

        try:
            response = self.client.text_generation(
                prompt,
                model="meta-llama/Llama-2-7b-chat-hf",
                max_new_tokens=300
            )
            return response[0]['generated_text']
        except Exception as e:
            return f"Error generando recomendaciones: {str(e)}"

    def analyze_competition(self, tienda_url: str, nicho: str) -> Dict:
        """Realiza un análisis completo de la competencia"""
        try:
            # Analizar la tienda propia
            own_features = self._analyze_competitor_site(tienda_url)
            if 'error' in own_features:
                return {'error': 'No se pudo analizar tu tienda'}

            # Obtener y analizar competidores
            competitor_urls = self._get_competitor_urls(nicho)
            competitor_features = []
            for url in competitor_urls:
                features = self._analyze_competitor_site(url)
                if 'error' not in features:
                    competitor_features.append(features)

            if not competitor_features:
                return {'error': 'No se pudieron analizar los competidores'}

            # Generar recomendaciones
            recommendations = self._generate_recommendations(competitor_features, own_features)

            return {
                'own_features': own_features,
                'competitor_features': competitor_features,
                'recommendations': recommendations
            }

        except Exception as e:
            return {'error': str(e)}