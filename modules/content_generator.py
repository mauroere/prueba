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

    def generate_social_post(self, tienda_url: str, platform: str) -> Dict:
        """Genera contenido para redes sociales"""
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
        """Genera meta-descripción y título SEO optimizados"""
        product_info = self._get_product_info(tienda_url)
        
        if 'error' in product_info:
            return {'error': 'No se pudo obtener la información del producto'}

        prompt = f"Genera una meta-descripción SEO y título optimizado para este producto:\nProducto: {product_info['nombre']}\nDescripción: {product_info['descripcion']}\nIncluye: título SEO (máximo 60 caracteres) y meta-descripción (máximo 155 caracteres)"

        try:
            response = self.client.text_generation(
                prompt,
                model="meta-llama/Llama-2-7b-chat-hf",
                max_new_tokens=200
            )
            return {'content': response[0]['generated_text']}
        except Exception as e:
            return {'error': str(e)}

    def generate_story(self, tienda_url: str) -> Dict:
        """Genera contenido para historias de Instagram"""
        product_info = self._get_product_info(tienda_url)
        
        if 'error' in product_info:
            return {'error': 'No se pudo obtener la información del producto'}

        prompt = f"Crea contenido para una historia de Instagram sobre este producto:\nProducto: {product_info['nombre']}\nPrecio: {product_info['precio']}\nDescripción: {product_info['descripcion']}\nIncluye: texto principal (corto y llamativo), stickers sugeridos y call-to-action"

        try:
            response = self.client.text_generation(
                prompt,
                model="meta-llama/Llama-2-7b-chat-hf",
                max_new_tokens=150
            )
            return {'content': response[0]['generated_text']}
        except Exception as e:
            return {'error': str(e)}