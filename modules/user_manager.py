from typing import Dict, List, Optional
from datetime import datetime
import bcrypt
from dataclasses import dataclass

@dataclass
class UserProfile:
    user_id: str
    username: str
    email: str
    full_name: str
    role: str  # 'user' o 'admin'
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    preferences: Dict = None
    created_at: datetime = None
    last_login: datetime = None
    store_url: Optional[str] = None
    notification_settings: Dict = None
    social_links: Dict = None
    analytics: Dict = None

class UserManager:
    def __init__(self):
        self.users: Dict[str, UserProfile] = {}
        self._init_default_admin()

    def _init_default_admin(self) -> None:
        """Inicializa el administrador por defecto si no existe"""
        if 'admin' not in self.users:
            self.users['admin'] = UserProfile(
                user_id='admin',
                username='admin',
                email='admin@example.com',
                full_name='Administrator',
                role='admin',
                created_at=datetime.now(),
                preferences={'theme': 'light', 'language': 'es'},
                notification_settings={'email': True, 'push': True}
            )

    def create_user(self, user_data: Dict) -> Dict:
        """Crea un nuevo usuario"""
        try:
            if user_data['email'] in [u.email for u in self.users.values()]:
                return {'error': 'El email ya está registrado'}

            user_id = str(len(self.users) + 1)
            new_user = UserProfile(
                user_id=user_id,
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data['full_name'],
                role='user',
                created_at=datetime.now(),
                store_url=user_data.get('store_url'),
                preferences={'theme': 'light', 'language': 'es'},
                notification_settings={'email': True, 'push': True},
                social_links={},
                analytics={}
            )
            self.users[user_id] = new_user
            return {'success': True, 'user_id': user_id}
        except Exception as e:
            return {'error': f'Error al crear usuario: {str(e)}'}

    def update_user(self, user_id: str, update_data: Dict) -> Dict:
        """Actualiza los datos de un usuario"""
        try:
            if user_id not in self.users:
                return {'error': 'Usuario no encontrado'}

            user = self.users[user_id]
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            return {'success': True, 'user': self.get_user_data(user_id)}
        except Exception as e:
            return {'error': f'Error al actualizar usuario: {str(e)}'}

    def delete_user(self, user_id: str) -> Dict:
        """Elimina un usuario"""
        try:
            if user_id not in self.users:
                return {'error': 'Usuario no encontrado'}
            if user_id == 'admin':
                return {'error': 'No se puede eliminar al administrador'}

            del self.users[user_id]
            return {'success': True}
        except Exception as e:
            return {'error': f'Error al eliminar usuario: {str(e)}'}

    def get_user_data(self, user_id: str) -> Dict:
        """Obtiene los datos de un usuario"""
        try:
            if user_id not in self.users:
                return {'error': 'Usuario no encontrado'}

            user = self.users[user_id]
            return {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'role': user.role,
                'profile_picture': user.profile_picture,
                'bio': user.bio,
                'location': user.location,
                'store_url': user.store_url,
                'preferences': user.preferences,
                'notification_settings': user.notification_settings,
                'social_links': user.social_links,
                'analytics': user.analytics,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        except Exception as e:
            return {'error': f'Error al obtener datos: {str(e)}'}

    def list_users(self, role: Optional[str] = None) -> List[Dict]:
        """Lista todos los usuarios, opcionalmente filtrados por rol"""
        try:
            users_list = []
            for user in self.users.values():
                if role is None or user.role == role:
                    users_list.append(self.get_user_data(user.user_id))
            return users_list
        except Exception as e:
            return [{'error': f'Error al listar usuarios: {str(e)}'}]

    def update_analytics(self, user_id: str, analytics_data: Dict) -> Dict:
        """Actualiza las analíticas del usuario"""
        try:
            if user_id not in self.users:
                return {'error': 'Usuario no encontrado'}

            user = self.users[user_id]
            user.analytics.update(analytics_data)
            return {'success': True, 'analytics': user.analytics}
        except Exception as e:
            return {'error': f'Error al actualizar analíticas: {str(e)}'}

    def update_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """Actualiza las preferencias del usuario"""
        try:
            if user_id not in self.users:
                return {'error': 'Usuario no encontrado'}

            user = self.users[user_id]
            user.preferences.update(preferences)
            return {'success': True, 'preferences': user.preferences}
        except Exception as e:
            return {'error': f'Error al actualizar preferencias: {str(e)}'}