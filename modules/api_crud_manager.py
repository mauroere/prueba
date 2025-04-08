import os
from typing import Dict, List, Optional, Union
import requests
from datetime import datetime
from dotenv import load_dotenv
from .logger_config import LoggerConfig
from .cache_manager import CacheManager

# Cargar variables de entorno
load_dotenv()

class ApiCrudManager:
    def __init__(self):
        try:
            # Configurar logger
            self.logger = LoggerConfig.get_logger('api_crud_manager')
            self.logger.info('Inicializando ApiCrudManager')
            
            # Configurar API de Tiendanube
            self.api_url = os.getenv('TIENDANUBE_API_URL')
            self.app_id = os.getenv('TIENDANUBE_APP_ID')
            self.client_secret = os.getenv('TIENDANUBE_CLIENT_SECRET')
            
            # Configurar caché
            self.cache = CacheManager(expiration_minutes=int(os.getenv('CACHE_EXPIRATION_MINUTES', 120)))
            
            # Configurar headers comunes
            self.headers = {
                'Authentication': f'Bearer {self.client_secret}',
                'Content-Type': 'application/json'
            }
            
            self.logger.info('ApiCrudManager inicializado correctamente')
        except Exception as e:
            self.logger.error(f"Error al inicializar ApiCrudManager: {str(e)}")
            raise Exception(f"Error al inicializar ApiCrudManager: {str(e)}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Realiza una petición a la API de Tiendanube"""
        try:
            url = f"{self.api_url}/{endpoint}"
            response = requests.request(method, url, headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error en la petición a la API: {str(e)}")
            return {'error': str(e)}
    
    def get_stores(self, page: int = 1, limit: int = 10) -> Dict:
        """Obtiene la lista de tiendas"""
        try:
            cache_key = f"stores_page_{page}_limit_{limit}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data
            
            endpoint = f"stores?page={page}&per_page={limit}"
            data = self._make_request('GET', endpoint)
            
            if 'error' not in data:
                self.cache.set(cache_key, data)
            
            return data
        except Exception as e:
            self.logger.error(f"Error al obtener tiendas: {str(e)}")
            return {'error': str(e)}
    
    def get_store(self, store_id: str) -> Dict:
        """Obtiene información de una tienda específica"""
        try:
            cache_key = f"store_{store_id}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data
            
            endpoint = f"store/{store_id}"
            data = self._make_request('GET', endpoint)
            
            if 'error' not in data:
                self.cache.set(cache_key, data)
            
            return data
        except Exception as e:
            self.logger.error(f"Error al obtener tienda {store_id}: {str(e)}")
            return {'error': str(e)}
    
    def create_store(self, store_data: Dict) -> Dict:
        """Crea una nueva tienda"""
        try:
            endpoint = "stores"
            return self._make_request('POST', endpoint, store_data)
        except Exception as e:
            self.logger.error(f"Error al crear tienda: {str(e)}")
            return {'error': str(e)}
    
    def update_store(self, store_id: str, store_data: Dict) -> Dict:
        """Actualiza una tienda existente"""
        try:
            endpoint = f"store/{store_id}"
            data = self._make_request('PUT', endpoint, store_data)
            
            if 'error' not in data:
                self.cache.delete(f"store_{store_id}")
            
            return data
        except Exception as e:
            self.logger.error(f"Error al actualizar tienda {store_id}: {str(e)}")
            return {'error': str(e)}
    
    def delete_store(self, store_id: str) -> Dict:
        """Elimina una tienda"""
        try:
            endpoint = f"store/{store_id}"
            data = self._make_request('DELETE', endpoint)
            
            if 'error' not in data:
                self.cache.delete(f"store_{store_id}")
            
            return data
        except Exception as e:
            self.logger.error(f"Error al eliminar tienda {store_id}: {str(e)}")
            return {'error': str(e)}
    
    def get_products(self, store_id: str, page: int = 1, limit: int = 10) -> Dict:
        """Obtiene la lista de productos de una tienda"""
        try:
            cache_key = f"products_store_{store_id}_page_{page}_limit_{limit}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data
            
            endpoint = f"store/{store_id}/products?page={page}&per_page={limit}"
            data = self._make_request('GET', endpoint)
            
            if 'error' not in data:
                self.cache.set(cache_key, data)
            
            return data
        except Exception as e:
            self.logger.error(f"Error al obtener productos de tienda {store_id}: {str(e)}")
            return {'error': str(e)}
    
    def get_product(self, store_id: str, product_id: str) -> Dict:
        """Obtiene información de un producto específico"""
        try:
            cache_key = f"product_{store_id}_{product_id}"
            cached_data = self.cache.get(cache_key)
            if cached_data:
                return cached_data
            
            endpoint = f"store/{store_id}/products/{product_id}"
            data = self._make_request('GET', endpoint)
            
            if 'error' not in data:
                self.cache.set(cache_key, data)
            
            return data
        except Exception as e:
            self.logger.error(f"Error al obtener producto {product_id} de tienda {store_id}: {str(e)}")
            return {'error': str(e)}
    
    def create_product(self, store_id: str, product_data: Dict) -> Dict:
        """Crea un nuevo producto en una tienda"""
        try:
            endpoint = f"store/{store_id}/products"
            return self._make_request('POST', endpoint, product_data)
        except Exception as e:
            self.logger.error(f"Error al crear producto en tienda {store_id}: {str(e)}")
            return {'error': str(e)}
    
    def update_product(self, store_id: str, product_id: str, product_data: Dict) -> Dict:
        """Actualiza un producto existente"""
        try:
            endpoint = f"store/{store_id}/products/{product_id}"
            data = self._make_request('PUT', endpoint, product_data)
            
            if 'error' not in data:
                self.cache.delete(f"product_{store_id}_{product_id}")
            
            return data
        except Exception as e:
            self.logger.error(f"Error al actualizar producto {product_id} de tienda {store_id}: {str(e)}")
            return {'error': str(e)}
    
    def delete_product(self, store_id: str, product_id: str) -> Dict:
        """Elimina un producto"""
        try:
            endpoint = f"store/{store_id}/products/{product_id}"
            data = self._make_request('DELETE', endpoint)
            
            if 'error' not in data:
                self.cache.delete(f"product_{store_id}_{product_id}")
            
            return data
        except Exception as e:
            self.logger.error(f"Error al eliminar producto {product_id} de tienda {store_id}: {str(e)}")
            return {'error': str(e)}