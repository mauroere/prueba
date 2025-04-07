import os
from typing import List, Dict
from huggingface_hub import InferenceClient
from bs4 import BeautifulSoup
import requests
from .content_analyzer import ContentAnalyzer

class ContentGenerator:
    def __init__(self):
        self.client = InferenceClient()
        self.content_analyzer = ContentAnalyzer()
        self.valid_platforms = ['Instagram', 'TikTok', 'Facebook']
        self.keywords_cache = {}

    def _get_product_info(self, tienda_url: str) -> Dict:
        """Obtiene información del producto desde la URL de Tiendanube"""
        try:
            response = requests.get(tienda_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            product_info = {
                'nombre': soup.find('h1', {'class': 'product-name'}).text.strip() if soup.find('h1', {'class': 'product-name'}) else '',
                'precio': soup.find('span', {'class': 'price'}).text.strip() if soup.find('span', {'class': 'price'}) else '',
                'descripcion': soup.find('div', {'class': 'product-description'}).text.strip() if soup.find('div', {'class': 'product-description'}) else ''
            }
            return product_info
        except Exception as e:
            return {'error': str(e)}

    def _validate_url(self, url: str) -> bool:
        """Valida si una URL es accesible"""
        try:
            response = requests.get(url)
            return response.status_code == 200
        except:
            return False

    def _analyze_keywords(self, text: str) -> List[str]:
        """Extrae palabras clave del texto"""
        words = text.lower().split()
        # Eliminar palabras comunes y cortas
        keywords = [word for word in words if len(word) > 3]
        return list(set(keywords))[:5]

    def generate_social_post(self, tienda_url: str, platform: str) -> Dict:
        """Genera contenido para redes sociales"""
        if not self._validate_url(tienda_url):
            return {'error': 'URL inválida o no accesible'}
            
        if platform not in self.valid_platforms:
            return {'error': f'Plataforma no soportada. Usar: {", ".join(self.valid_platforms)}'}

        product_info = self._get_product_info(tienda_url)
        if 'error' in product_info:
            return {'error': 'No se pudo obtener la información del producto'}

        prompts = {
            'Instagram': f"Crea un post atractivo para Instagram sobre este producto:\nProducto: {product_info['nombre']}\nPrecio: {product_info['precio']}\nDescripción: {product_info['descripcion']}\nIncluye: texto principal, hashtags relevantes y call-to-action",
            'TikTok': f"Crea un guión para TikTok sobre este producto:\nProducto: {product_info['nombre']}\nPrecio: {product_info['precio']}\nDescripción: {product_info['descripcion']}\nIncluye: concepto del video, texto en pantalla y música sugerida",
            'Facebook': f"Crea un post para Facebook sobre este producto:\nProducto: {product_info['nombre']}\nPrecio: {product_info['precio']}\nDescripción: {product_info['descripcion']}\nIncluye: texto principal, emojis relevantes y call-to-action"
        }

        try:
            # Generar contenido base
            response = self.client.text_generation(
                prompts[platform],
                model="meta-llama/Llama-2-7b-chat-hf",
                max_new_tokens=250
            )
            content = response[0]['generated_text']
            
            # Analizar el contenido generado
            metrics = {
                'likes': 0,  # Métricas iniciales para análisis
                'comments': 0,
                'shares': 0,
                'saves': 0
            }
            analysis = self.content_analyzer.analyze_post(content, metrics)
            
            # Si el análisis sugiere mejoras, regenerar el contenido
            if analysis['sentiment']['classification'] == 'Negativo' or analysis['engagement']['score'] < 50:
                response = self.client.text_generation(
                    f"Mejora este contenido para hacerlo más positivo y engaging: {content}",
                    model="meta-llama/Llama-2-7b-chat-hf",
                    max_new_tokens=250
                )
                content = response[0]['generated_text']
                analysis = self.content_analyzer.analyze_post(content, metrics)
            
            return {
                'content': content,
                'analysis': analysis
            }
        except Exception as e:
            return {'error': str(e)}

    def generate_seo_description(self, tienda_url: str) -> Dict:
        """Genera meta-descripción y título SEO optimizados con palabras clave"""
        product_info = self._get_product_info(tienda_url)
        
        if 'error' in product_info:
            return {'error': 'No se pudo obtener la información del producto'}

        # Analizar palabras clave
        keywords = self._analyze_keywords(product_info['descripcion'])
        self.keywords_cache[tienda_url] = keywords

        prompt = f"""Genera una meta-descripción SEO y título optimizado para este producto:
        Producto: {product_info['nombre']}
        Descripción: {product_info['descripcion']}
        Palabras clave principales: {', '.join(keywords)}
        
        Requisitos:
        1. Título SEO (máximo 60 caracteres)
        2. Meta-descripción (máximo 155 caracteres)
        3. Incluir al menos 2 palabras clave naturalmente
        4. Optimizar para CTR con call-to-action"""

        try:
            response = self.client.text_generation(
                prompt,
                model="meta-llama/Llama-2-7b-chat-hf",
                max_new_tokens=200
            )
            return {
                'content': response[0]['generated_text'],
                'keywords': keywords
            }
        except Exception as e:
            return {'error': str(e)}

    def generate_story(self, tienda_url: str) -> Dict:
        """Genera contenido para historias de Instagram"""
        product_info = self._get_product_info(tienda_url)
        
        if 'error' in product_info:
            return {'error': 'No se pudo obtener la información del producto'}

        prompt = f"""Crea contenido para una historia de Instagram sobre este producto:
        Producto: {product_info['nombre']}
        Precio: {product_info['precio']}
        Descripción: {product_info['descripcion']}
        
        Incluye:
        1. Texto principal (corto y llamativo)
        2. Stickers sugeridos
        3. Call-to-action
        4. Hashtags relevantes (máximo 5)
        5. Sugerencia de música de tendencia
        6. Efectos visuales recomendados"""

        try:
            response = self.client.text_generation(
                prompt,
                model="meta-llama/Llama-2-7b-chat-hf",
                max_new_tokens=200
            )
            return {'content': response[0]['generated_text']}
        except Exception as e:
            return {'error': str(e)}

    def generate_blog_post(self, tienda_url: str) -> Dict:
        """Genera un artículo de blog optimizado para SEO"""
        product_info = self._get_product_info(tienda_url)
        
        if 'error' in product_info:
            return {'error': 'No se pudo obtener la información del producto'}

        # Usar palabras clave almacenadas o generar nuevas
        keywords = self.keywords_cache.get(tienda_url) or self._analyze_keywords(product_info['descripcion'])

        prompt = f"""Genera un artículo de blog completo sobre este producto:
        Producto: {product_info['nombre']}
        Descripción: {product_info['descripcion']}
        Palabras clave: {', '.join(keywords)}
        
        Estructura del artículo:
        1. Título atractivo y optimizado para SEO
        2. Introducción (2-3 párrafos)
        3. Características principales (con subtítulos)
        4. Beneficios y casos de uso
        5. Comparación con alternativas
        6. Conclusión con call-to-action
        7. Meta-descripción para el blog
        
        Requisitos:
        - Longitud: 800-1000 palabras
        - Incluir palabras clave naturalmente
        - Optimizar para lectura y SEO
        - Incluir sugerencias de imágenes"""

        try:
            response = self.client.text_generation(
                prompt,
                model="meta-llama/Llama-2-7b-chat-hf",
                max_new_tokens=1000
            )
            return {
                'content': response[0]['generated_text'],
                'keywords': keywords
            }
        except Exception as e:
            return {'error': str(e)}