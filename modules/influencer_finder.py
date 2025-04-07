import instaloader
from typing import List, Dict
import time

class InfluencerFinder:
    def __init__(self):
        self.loader = instaloader.Instaloader()
        self.min_followers = 1000
        self.max_followers = 10000

    def _get_hashtag_posts(self, hashtag: str, max_posts: int = 100) -> List[Dict]:
        """Obtiene posts recientes de un hashtag específico"""
        try:
            posts = []
            hashtag_obj = instaloader.Hashtag.from_name(self.loader.context, hashtag)
            
            for post in hashtag_obj.get_posts():
                if len(posts) >= max_posts:
                    break
                    
                posts.append({
                    'username': post.owner_username,
                    'likes': post.likes,
                    'comments': post.comments,
                    'caption': post.caption,
                    'hashtags': post.caption_hashtags,
                    'location': post.location
                })
                
                # Respetar límites de la API
                time.sleep(2)
                
            return posts
        except Exception as e:
            return [{'error': str(e)}]

    def _analyze_profile(self, username: str) -> Dict:
        """Analiza un perfil de Instagram"""
        try:
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            # Verificar si cumple con los criterios de micro-influencer
            if self.min_followers <= profile.followers <= self.max_followers:
                engagement_rate = ((profile.mediacount * profile.avglike) / 
                                 profile.followers) * 100
                
                return {
                    'username': username,
                    'followers': profile.followers,
                    'posts': profile.mediacount,
                    'avg_likes': profile.avglike,
                    'engagement_rate': round(engagement_rate, 2),
                    'bio': profile.biography,
                    'is_business': profile.is_business_account
                }
            return None
        except Exception as e:
            return {'error': str(e)}

    def find_influencers(self, nicho: str, ubicacion: str) -> Dict:
        """Encuentra micro-influencers basados en nicho y ubicación"""
        try:
            # Crear hashtags relevantes
            hashtags = [
                f"{nicho}{ubicacion}",
                f"{nicho}argentina",
                f"emprendedores{ubicacion}",
                f"tiendas{ubicacion}"
            ]
            
            # Recolectar posts de hashtags
            all_posts = []
            for hashtag in hashtags:
                posts = self._get_hashtag_posts(hashtag)
                if not any('error' in post for post in posts):
                    all_posts.extend(posts)

            # Analizar perfiles únicos
            influencers = []
            analyzed_usernames = set()
            
            for post in all_posts:
                username = post['username']
                if username not in analyzed_usernames:
                    profile_data = self._analyze_profile(username)
                    if profile_data and 'error' not in profile_data:
                        influencers.append(profile_data)
                    analyzed_usernames.add(username)
                    time.sleep(2)  # Respetar límites de la API

            # Ordenar por tasa de engagement
            influencers.sort(key=lambda x: x['engagement_rate'], reverse=True)

            return {
                'total_found': len(influencers),
                'influencers': influencers[:10]  # Retornar los 10 mejores
            }

        except Exception as e:
            return {'error': str(e)}

    def get_contact_suggestions(self, influencer_data: Dict) -> str:
        """Genera sugerencias para contactar al influencer"""
        engagement = influencer_data['engagement_rate']
        followers = influencer_data['followers']
        
        if engagement > 5:
            return "Alto engagement. Sugerir colaboración con productos gratuitos + comisión por ventas."
        elif engagement > 3:
            return "Buen engagement. Ofrecer productos gratuitos para review."
        else:
            return "Engagement moderado. Considerar pequeño pago + producto gratuito."