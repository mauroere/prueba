from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import re
from datetime import datetime, timedelta
from functools import lru_cache
import time
from requests.exceptions import RequestException
from .metrics_analyzer import MetricsAnalyzer, EngagementMetrics

class InfluencerFinder:
    def __init__(self):
        self.ua = UserAgent()
        self.base_url = "https://www.instagram.com"
        self.api_url = "https://www.instagram.com/graphql/query"
        self.request_delay = 2  # Delay entre requests en segundos
        self.last_request_time = 0
        self.max_retries = 3
        self.metrics_analyzer = MetricsAnalyzer()

    def _rate_limit_delay(self):
        """Implementa un delay entre requests para evitar rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.request_delay:
            time.sleep(self.request_delay - time_since_last_request)
        self.last_request_time = time.time()

    def _make_request(self, url: str, max_retries: int = None) -> Optional[Dict]:
        """Realiza una petición HTTP con reintentos y manejo de errores"""
        if max_retries is None:
            max_retries = self.max_retries

        for attempt in range(max_retries):
            try:
                self._rate_limit_delay()
                headers = {'User-Agent': self.ua.random}
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return response.json()
            except RequestException as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)  # Exponential backoff
        return None

    @lru_cache(maxsize=100)
    def _get_location_id(self, ubicacion: str) -> str:
        """Obtiene el ID de ubicación de Instagram"""
        try:
            search_url = f"{self.base_url}/web/search/topsearch/?context=place&query={ubicacion}"
            data = self._make_request(search_url)
            
            if data and data.get('places'):
                return data['places'][0]['place']['location']['pk']
            return ''
        except Exception as e:
            print(f"Error al obtener ID de ubicación: {str(e)}")
            return ''

<<<<<<< HEAD
    @lru_cache(maxsize=100)
    def _get_hashtag_id(self, hashtag: str) -> str:
        """Obtiene el ID de un hashtag"""
=======
    def _analyze_profile(self, username: str) -> Dict:
        """Analiza un perfil de Instagram de forma detallada"""
>>>>>>> 18f8dc7e79c292e1fb3cab334f99a7f41d7fcbc9
        try:
            search_url = f"{self.base_url}/web/search/topsearch/?context=hashtag&query={hashtag}"
            data = self._make_request(search_url)
            
<<<<<<< HEAD
            if data and data.get('hashtags'):
                return data['hashtags'][0]['hashtag']['id']
            return ''
=======
            # Verificar si cumple con los criterios de micro-influencer
            if self.min_followers <= profile.followers <= self.max_followers:
                engagement_rate = ((profile.mediacount * profile.avglike) / 
                                 profile.followers) * 100
                
                # Análisis detallado del perfil
                profile_data = {
                    'username': username,
                    'followers': profile.followers,
                    'following': profile.followees,
                    'posts': profile.mediacount,
                    'avg_likes': profile.avglike,
                    'engagement_rate': round(engagement_rate, 2),
                    'bio': profile.biography,
                    'is_business': profile.is_business_account,
                    'external_url': profile.external_url,
                    'is_verified': profile.is_verified,
                    
                    # Análisis de contenido
                    'hashtags': self._extract_common_hashtags(profile),
                    'post_frequency': self._calculate_post_frequency(profile),
                    'content_categories': self._analyze_content_categories(profile),
                    
                    # Métricas adicionales
                    'follower_growth_rate': self._calculate_growth_rate(profile),
                    'audience_quality': self._analyze_audience_quality(profile),
                    'brand_safety_score': self._calculate_brand_safety(profile)
                }
                
                return profile_data
            return None
>>>>>>> 18f8dc7e79c292e1fb3cab334f99a7f41d7fcbc9
        except Exception as e:
            print(f"Error al obtener ID de hashtag: {str(e)}")
            return ''

    def _get_related_hashtags(self, nicho: str) -> List[str]:
        """Obtiene hashtags relacionados con el nicho"""
        hashtags = {
            'moda': ['fashion', 'style', 'outfit', 'moda', 'tendencias', 'modaargentina'],
            'tecnología': ['tech', 'tecnologia', 'gadgets', 'innovation', 'techarg'],
            'belleza': ['beauty', 'makeup', 'skincare', 'belleza', 'maquillaje'],
            'hogar': ['homedecor', 'decoration', 'casa', 'deco', 'diseño'],
            'deportes': ['sports', 'fitness', 'training', 'gym', 'deporte'],
            'alimentos': ['food', 'foodie', 'cooking', 'cocina', 'recetas'],
            'mascotas': ['pets', 'dogs', 'cats', 'mascotas', 'petlovers'],
            'arte': ['art', 'design', 'illustration', 'arte', 'artesanal'],
            'libros': ['books', 'reading', 'libros', 'lectura', 'literatura'],
            'música': ['music', 'musica', 'musician', 'banda', 'concierto']
        }
        
        # Normalizar el nicho y encontrar la mejor coincidencia
        nicho_norm = nicho.lower().strip()
        for key, tags in hashtags.items():
            if nicho_norm in key or any(nicho_norm in tag for tag in tags):
                return tags
        
        # Si no hay coincidencia exacta, devolver hashtags genéricos
        return ['argentina', 'emprendimiento', 'shop', 'tiendaonline', 'compralocal']

    def _calculate_engagement(self, followers: int, likes: int, posts: int) -> float:
        """Calcula la tasa de engagement"""
        if posts > 0 and followers > 0:
            return (likes / posts / followers) * 100
        return 0.0

    def _is_micro_influencer(self, followers: int, engagement_rate: float) -> bool:
        """Determina si un perfil califica como micro-influencer"""
        return 1000 <= followers <= 100000 and engagement_rate >= 2.0

    @lru_cache(maxsize=50)
    def _get_profile_metrics(self, username: str) -> Dict:
        """Obtiene métricas avanzadas de un perfil de Instagram"""
        try:
            self._rate_limit_delay()
            headers = {'User-Agent': self.ua.random}
            response = requests.get(f"{self.base_url}/{username}/", headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer datos del script con la información del perfil
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if data.get('@type') == 'ProfilePage':
                        followers = int(data.get('interactionStatistic', {}).get('userInteractionCount', 0))
                        posts = int(data.get('mainEntityofPage', {}).get('interactionStatistic', {}).get('userInteractionCount', 0))
                        avg_likes = self._estimate_avg_likes(followers)
                        
                        # Estimar métricas adicionales basadas en promedios de la industria
                        avg_comments = int(avg_likes * 0.05)  # ~5% de likes se convierten en comentarios
                        avg_shares = int(avg_likes * 0.02)   # ~2% de likes resultan en compartidos
                        avg_saves = int(avg_likes * 0.03)    # ~3% de likes resultan en guardados
                        
                        # Crear objeto de métricas de engagement
                        metrics = EngagementMetrics(
                            likes=avg_likes,
                            comments=avg_comments,
                            shares=avg_shares,
                            saves=avg_saves,
                            followers=followers,
                            posts=posts
                        )
                        
                        # Actualizar el analizador de métricas
                        self.metrics_analyzer.add_metrics(username, metrics)
                        
                        # Obtener análisis de rendimiento
                        performance = self.metrics_analyzer.analyze_performance(username)
                        
                        return {
                            'followers': followers,
                            'posts': posts,
                            'bio': data.get('description', ''),
                            'engagement_metrics': {
                                'likes': avg_likes,
                                'comments': avg_comments,
                                'shares': avg_shares,
                                'saves': avg_saves,
                                'engagement_rate': metrics.engagement_rate,
                                'quality_score': metrics.quality_score
                            },
                            'performance_analysis': performance,
                            'last_updated': datetime.now().isoformat()
                        }
                except json.JSONDecodeError as e:
                    print(f"Error al parsear JSON del perfil {username}: {str(e)}")
                    continue
            
            # Si no se encuentra la información en el JSON-LD, intentar extraer de la página
            followers = self._extract_number(soup.find('meta', property='og:description'))
            posts = len(soup.find_all('div', class_='_aabd'))
            avg_likes = self._estimate_avg_likes(followers)
            
            # Crear métricas estimadas
            metrics = EngagementMetrics(
                likes=avg_likes,
                comments=int(avg_likes * 0.05),
                shares=int(avg_likes * 0.02),
                saves=int(avg_likes * 0.03),
                followers=followers,
                posts=posts
            )
            
            self.metrics_analyzer.add_metrics(username, metrics)
            performance = self.metrics_analyzer.analyze_performance(username)
            
            return {
                'followers': followers,
                'posts': posts,
                'bio': soup.find('meta', property='og:description')['content'] if soup.find('meta', property='og:description') else '',
                'engagement_metrics': {
                    'likes': avg_likes,
                    'comments': metrics.comments,
                    'shares': metrics.shares,
                    'saves': metrics.saves,
                    'engagement_rate': metrics.engagement_rate,
                    'quality_score': metrics.quality_score
                },
                'performance_analysis': performance,
                'last_updated': datetime.now().isoformat()
            }
        except RequestException as e:
            print(f"Error de red al obtener métricas de {username}: {str(e)}")
            return {'error': f"Error de red: {str(e)}"}
        except Exception as e:
            print(f"Error inesperado al obtener métricas de {username}: {str(e)}")
            return {'error': str(e)}

    def _extract_number(self, text: str) -> int:
        """Extrae números de un texto"""
        if not text:
            return 0
        numbers = re.findall(r'\d+', text)
        return int(numbers[0]) if numbers else 0

    def _estimate_avg_likes(self, followers: int) -> int:
        """Estima el promedio de likes basado en el número de seguidores"""
        # Estimación aproximada: 3-7% de los seguidores dan like
        engagement_rate = 0.05  # 5% promedio
        return int(followers * engagement_rate)

    def find_influencers(self, nicho: str, ubicacion: str) -> Dict:
        """Busca micro-influencers relevantes para el nicho y ubicación"""
        try:
            # Validar parámetros de entrada
            if not nicho or not ubicacion:
                return {'error': 'El nicho y la ubicación son requeridos'}

            # Obtener hashtags relacionados
            hashtags = self._get_related_hashtags(nicho)
            if not hashtags:
                return {'error': 'No se encontraron hashtags para el nicho especificado'}

            location_id = self._get_location_id(ubicacion)
            influencers = []
            processed_usernames = set()
            errors = []

            # Buscar por hashtags
            for hashtag in hashtags:
                try:
                    hashtag_id = self._get_hashtag_id(hashtag)
                    if not hashtag_id:
                        continue

                    # Búsqueda de posts con el hashtag
                    search_url = f"{self.api_url}?query_hash=9b498c08113f1e09617a1703c22b2f32&variables={{\"tag_name\":\"{hashtag}\",\"first\":50}}"
                    data = self._make_request(search_url)
                    
                    if not data:
                        errors.append(f"No se pudieron obtener datos para el hashtag {hashtag}")
                        continue

                    posts = data.get('data', {}).get('hashtag', {}).get('edge_hashtag_to_media', {}).get('edges', [])
                    
                    for post in posts:
                        try:
                            username = post['node']['owner']['username']
                            if username in processed_usernames:
                                continue

                            metrics = self._get_profile_metrics(username)
                            if 'error' in metrics:
                                errors.append(f"Error al obtener métricas para {username}: {metrics['error']}")
                                continue

                            engagement_rate = self._calculate_engagement(
                                metrics['followers'],
                                metrics['avg_likes'],
                                metrics['posts']
                            )

                            if self._is_micro_influencer(metrics['followers'], engagement_rate):
                                influencer_data = {
                                    'username': username,
                                    'followers': metrics['followers'],
                                    'posts': metrics['posts'],
                                    'avg_likes': metrics['avg_likes'],
                                    'engagement_rate': round(engagement_rate, 2),
                                    'bio': metrics['bio'],
                                    'last_updated': metrics.get('last_updated', datetime.now().isoformat())
                                }
                                influencers.append(influencer_data)
                                processed_usernames.add(username)

                            if len(influencers) >= 10:
                                break
                        except Exception as e:
                            errors.append(f"Error al procesar el post de {username}: {str(e)}")
                            continue

                    if len(influencers) >= 10:
                        break
                except Exception as e:
                    errors.append(f"Error al procesar el hashtag {hashtag}: {str(e)}")
                    continue

            result = {
                'total_found': len(influencers),
                'influencers': sorted(influencers, key=lambda x: x['engagement_rate'], reverse=True)
            }

            if errors:
                result['warnings'] = errors

            return result

        except Exception as e:
            print(f"Error general en find_influencers: {str(e)}")
            return {'error': str(e)}