import os
from typing import List, Dict
from huggingface_hub import InferenceClient
from bs4 import BeautifulSoup
import requests
from .content_analyzer import ContentAnalyzer

class ContentGenerator:
    def __init__(self):
        try:
            self.client = InferenceClient()
            self.content_analyzer = ContentAnalyzer()
            self.valid_platforms = ['Instagram', 'TikTok', 'Facebook']
            self.keywords_cache = {}
            self.max_retries = 3
            self.timeout = 10
        except Exception as e:
            raise Exception(f"Error al inicializar ContentGenerator: {str(e)}")

    def _get_product_info(self, tienda_url: str) -> Dict:
        """Obtiene información del producto desde la URL de Tiendanube"""
        if not tienda_url or not tienda_url.startswith('http'):
            return {'error': 'URL inválida'}

        for attempt in range(self.max_retries):
            try:
                response = requests.get(tienda_url, timeout=self.timeout)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                product_info = {
                    'nombre': soup.find('h1', {'class': 'product-name'}).text.strip() if soup.find('h1', {'class': 'product-name'}) else '',
                    'precio': soup.find('span', {'class': 'price'}).text.strip() if soup.find('span', {'class': 'price'}) else '',
                    'descripcion': soup.find('div', {'class': 'product-description'}).text.strip() if soup.find('div', {'class': 'product-description'}) else ''
                }

                if not product_info['nombre'] or not product_info['precio']:
                    return {'error': 'Información del producto incompleta'}

                return product_info
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    return {'error': f'Error de conexión: {str(e)}'}
                time.sleep(2 ** attempt)  # Backoff exponencial
            except Exception as e:
                return {'error': f'Error al procesar la información: {str(e)}'}

    def _validate_url(self, url: str) -> bool:
        """Valida si una URL es accesible y tiene el formato correcto"""
        if not url or not isinstance(url, str):
            return False
            
        if not url.startswith(('http://', 'https://')):
            return False
            
        for attempt in range(self.max_retries):
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
                response.raise_for_status()
                return True
            except requests.exceptions.ConnectionError:
                if attempt == self.max_retries - 1:
                    return False
                time.sleep(2 ** attempt)
            except requests.exceptions.Timeout:
                if attempt == self.max_retries - 1:
                    return False
                time.sleep(2 ** attempt)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    return False
                if attempt == self.max_retries - 1:
                    return False
                time.sleep(2 ** attempt)
            except Exception:
                if attempt == self.max_retries - 1:
                    return False
                time.sleep(2 ** attempt)
        return False

    def _analyze_keywords(self, text: str) -> List[str]:
        """Extrae y analiza palabras clave relevantes del texto"""
        if not text or not isinstance(text, str):
            return []
            
        # Palabras comunes en español que debemos excluir
        stop_words = {'para', 'como', 'este', 'esta', 'pero', 'por', 'los', 'las', 'que', 'con', 'del'}
        
        # Limpiar y normalizar el texto
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Filtrar palabras relevantes
        keywords = [word for word in words 
                   if len(word) > 3 
                   and word not in stop_words 
                   and not word.isdigit()]
        
        # Ordenar por frecuencia y retornar las más comunes
        from collections import Counter
        keyword_freq = Counter(keywords)
        return [word for word, _ in keyword_freq.most_common(5)]

    def generate_social_post(self, tienda_url: str, platform: str) -> Dict:
        """Genera contenido optimizado para redes sociales"""
        # Validación de parámetros de entrada
        if not tienda_url or not isinstance(tienda_url, str):
            return {'error': 'URL inválida: la URL es requerida y debe ser una cadena de texto'}
            
        if not platform or not isinstance(platform, str):
            return {'error': 'Plataforma inválida: la plataforma es requerida y debe ser una cadena de texto'}
            
        platform = platform.strip().title()
        if platform not in self.valid_platforms:
            return {'error': f'Plataforma no soportada. Plataformas válidas: {", ".join(self.valid_platforms)}'}

        # Validar URL y obtener información del producto
        if not self._validate_url(tienda_url):
            return {'error': 'URL no accesible: verifica que la URL sea correcta y esté disponible'}

        product_info = self._get_product_info(tienda_url)
        if 'error' in product_info:
            return product_info

        # Verificar que tengamos toda la información necesaria
        required_fields = ['nombre', 'precio', 'descripcion']
        missing_fields = [field for field in required_fields if not product_info.get(field)]
        if missing_fields:
            return {'error': f'Información incompleta del producto. Campos faltantes: {", ".join(missing_fields)}'}

        # Plantillas optimizadas por plataforma
        prompts = {
            'Instagram': f"""Crea un post atractivo para Instagram sobre este producto:
                Producto: {product_info['nombre']}
                Precio: {product_info['precio']}
                Descripción: {product_info['descripcion']}
                
                Requisitos:
                - Texto principal cautivador (máximo 2200 caracteres)
                - 5-10 hashtags relevantes y específicos
                - Call-to-action claro y persuasivo
                - Emojis relevantes y moderados""",
            'TikTok': f"""Crea un guión para TikTok sobre este producto:
                Producto: {product_info['nombre']}
                Precio: {product_info['precio']}
                Descripción: {product_info['descripcion']}
                
                Requisitos:
                - Concepto creativo y tendencia actual
                - Texto en pantalla (máximo 150 caracteres)
                - Música sugerida de tendencia
                - Estructura: gancho + demostración + call-to-action""",
            'Facebook': f"""Crea un post para Facebook sobre este producto:
                Producto: {product_info['nombre']}
                Precio: {product_info['precio']}
                Descripción: {product_info['descripcion']}
                
                Requisitos:
                - Texto principal informativo y persuasivo
                - Emojis relevantes y profesionales
                - Call-to-action específico
                - Enlaces y menciones relevantes"""
        }

        try:
            content = None
            analysis = None
            max_attempts = 3

            for attempt in range(max_attempts):
                try:
                    # Generar contenido base
                    response = self.client.text_generation(
                        prompts[platform],
                        model="meta-llama/Llama-2-7b-chat-hf",
                        max_new_tokens=250,
                        temperature=0.7,  # Ajustar creatividad
                        top_p=0.9  # Mantener coherencia
                    )

                    if not response or not response[0].get('generated_text'):
                        if attempt == max_attempts - 1:
                            return {'error': 'No se pudo generar contenido válido'}
                        continue

                    content = response[0]['generated_text'].strip()
                    
                    # Validar longitud del contenido
                    if len(content) < 50:
                        if attempt == max_attempts - 1:
                            return {'error': 'Contenido generado demasiado corto'}
                        continue

                    # Analizar el contenido generado
                    metrics = {
                        'likes': 0,
                        'comments': 0,
                        'shares': 0,
                        'saves': 0
                    }
                    analysis = self.content_analyzer.analyze_post(content, metrics)
                    
                    # Verificar calidad del contenido
                    if analysis['sentiment']['classification'] == 'Negativo' or analysis['engagement']['score'] < 50:
                        if attempt < max_attempts - 1:
                            continue
                        
                        # Último intento: mejorar el contenido existente
                        response = self.client.text_generation(
                            f"Mejora este contenido para hacerlo más positivo y engaging, manteniendo el mensaje principal: {content}",
                            model="meta-llama/Llama-2-7b-chat-hf",
                            max_new_tokens=250,
                            temperature=0.8
                        )
                        content = response[0]['generated_text'].strip()
                        analysis = self.content_analyzer.analyze_post(content, metrics)
                    
                    # Si llegamos aquí, tenemos contenido válido
                    break

                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    time.sleep(2 ** attempt)  # Backoff exponencial

            if not content or not analysis:
                return {'error': 'No se pudo generar contenido después de múltiples intentos'}

            return {
                'content': content,
                'analysis': analysis,
                'platform': platform,
                'generated_at': datetime.now().isoformat()
            }

        except Exception as e:
            return {'error': f'Error al generar contenido: {str(e)}'}

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