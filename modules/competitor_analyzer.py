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
        """Analiza una tienda competidora"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            features = {
                'envio_gratis': bool(soup.find(text=lambda t: 'envío gratis' in t.lower() if t else False)),
                'medios_pago': len(soup.find_all('img', {'class': 'payment-logo'})) if soup.find_all('img', {'class': 'payment-logo'}) else 0,
                'redes_sociales': len(soup.find_all('a', {'class': 'social'})) if soup.find_all('a', {'class': 'social'}) else 0,
                'productos': len(soup.find_all('div', {'class': 'product-box'})) if soup.find_all('div', {'class': 'product-box'}) else 0
            }
            return features
        except Exception as e:
            return {'error': str(e)}

    def _generate_recommendations(self, competitor_features: List[Dict], own_features: Dict) -> str:
        """Genera recomendaciones basadas en el análisis comparativo"""
        prompt = f"Analiza estas características de tiendas competidoras y genera recomendaciones estratégicas:\n"
        prompt += f"Características de tu tienda:\n{str(own_features)}\n"
        prompt += f"Características de competidores:\n{str(competitor_features)}\n"
        prompt += "Genera 3-5 recomendaciones específicas y accionables para mejorar la competitividad de la tienda."

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