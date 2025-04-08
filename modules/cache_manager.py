from typing import Dict, Any
from datetime import datetime, timedelta

class CacheManager:
    def __init__(self, expiration_minutes: int = 60):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.expiration_minutes = expiration_minutes

    def get(self, key: str) -> Any:
        """Obtiene un valor del caché si existe y no ha expirado"""
        if key in self._cache:
            cache_entry = self._cache[key]
            if datetime.now() < cache_entry['expiration']:
                return cache_entry['value']
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Almacena un valor en el caché con tiempo de expiración"""
        expiration = datetime.now() + timedelta(minutes=self.expiration_minutes)
        self._cache[key] = {
            'value': value,
            'expiration': expiration
        }

    def clear(self) -> None:
        """Limpia todo el caché"""
        self._cache.clear()

    def remove(self, key: str) -> None:
        """Elimina una entrada específica del caché"""
        if key in self._cache:
            del self._cache[key]

    def cleanup_expired(self) -> None:
        """Elimina todas las entradas expiradas del caché"""
        now = datetime.now()
        expired_keys = [key for key, entry in self._cache.items() 
                       if now >= entry['expiration']]
        for key in expired_keys:
            del self._cache[key]