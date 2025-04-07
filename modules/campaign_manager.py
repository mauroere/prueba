from typing import Dict
from PIL import Image, ImageDraw, ImageFont
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import json

class CampaignManager:
    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict:
        """Carga las plantillas predefinidas"""
        return {
            'cupon': {
                'lanzamiento': {
                    'titulo': '¡Bienvenido a {tienda}!',
                    'descripcion': 'Disfruta de un {descuento}% de descuento en tu primera compra',
                    'codigo': 'BIENVENIDO{codigo}',
                    'validez': '7 días'
                }
            },
            'email': {
                'bienvenida': {
                    'asunto': '¡Bienvenido a {tienda}! 🎉',
                    'contenido': '''
                    <h1>¡Hola! 👋</h1>
                    <p>Gracias por unirte a {tienda}. Como agradecimiento, te regalamos un {descuento}% de descuento en tu primera compra.</p>
                    <p>Usa el código: <strong>{codigo}</strong></p>
                    <p>Descubre nuestra colección en {url_tienda}</p>
                    <p>¡Esperamos que encuentres algo especial!</p>
                    '''
                },
                'promocion': {
                    'asunto': '¡Oferta especial en {tienda}! 🎯',
                    'contenido': '''
                    <h1>¡Oferta especial! 🎯</h1>
                    <p>No te pierdas esta oportunidad única:</p>
                    <p>{descripcion_oferta}</p>
                    <p>Visítanos en {url_tienda}</p>
                    <p>¡Te esperamos!</p>
                    '''
                }
            },
            'historia': {
                'producto': {
                    'titulo': '¡NUEVO EN {tienda}!',
                    'descripcion': '{nombre_producto}\n{precio}',
                    'cta': '¡Desliza hacia arriba para comprar!'
                },
                'oferta': {
                    'titulo': '¡OFERTA ESPECIAL!',
                    'descripcion': '{descripcion_oferta}\nVálido por: {validez}',
                    'cta': '¡Compra ahora con {codigo}!'
                }
            }
        }

    def generate_coupon(self, tienda_data: Dict) -> Dict:
        """Genera un cupón de descuento personalizado"""
        try:
            template = self.templates['cupon']['lanzamiento']
            
            # Personalizar el cupón
            cupon = {
                'titulo': template['titulo'].format(tienda=tienda_data['nombre']),
                'descripcion': template['descripcion'].format(descuento=tienda_data['descuento']),
                'codigo': template['codigo'].format(codigo=tienda_data['codigo']),
                'validez': template['validez']
            }

            # Crear imagen del cupón (usando SVG para mejor calidad)
            cupon['imagen'] = self._create_coupon_image(cupon)
            
            return cupon
        except Exception as e:
            return {'error': str(e)}

    def _create_coupon_image(self, cupon_data: Dict) -> str:
        """Crea una imagen SVG para el cupón"""
        svg_template = f'''
        <svg width="600" height="300" xmlns="http://www.w3.org/2000/svg">
            <style>
                .title {{ font: bold 24px sans-serif; fill: #333; }}
                .description {{ font: 18px sans-serif; fill: #666; }}
                .code {{ font: bold 36px monospace; fill: #ff6b6b; }}
                .validity {{ font: 14px sans-serif; fill: #999; }}
            </style>
            <rect width="100%" height="100%" fill="white" rx="10"/>
            <text x="50" y="80" class="title">{cupon_data['titulo']}</text>
            <text x="50" y="120" class="description">{cupon_data['descripcion']}</text>
            <text x="50" y="180" class="code">{cupon_data['codigo']}</text>
            <text x="50" y="220" class="validity">Válido por: {cupon_data['validez']}</text>
        </svg>
        '''
        return svg_template

    def generate_email(self, tipo: str, tienda_data: Dict) -> Dict:
        """Genera una plantilla de email marketing"""
        try:
            template = self.templates['email'][tipo]
            
            email = {
                'asunto': template['asunto'].format(**tienda_data),
                'contenido': template['contenido'].format(**tienda_data)
            }
            
            return email
        except Exception as e:
            return {'error': str(e)}

    def generate_story(self, tipo: str, tienda_data: Dict) -> Dict:
        """Genera una plantilla para historia de Instagram"""
        try:
            template = self.templates['historia'][tipo]
            
            # Personalizar la historia
            historia = {
                'titulo': template['titulo'].format(**tienda_data),
                'descripcion': template['descripcion'].format(**tienda_data),
                'cta': template['cta'].format(**tienda_data)
            }

            # Crear imagen de la historia (usando SVG para mejor calidad)
            historia['imagen'] = self._create_story_image(historia)
            
            return historia
        except Exception as e:
            return {'error': str(e)}

    def _create_story_image(self, historia_data: Dict) -> str:
        """Crea una imagen SVG para la historia de Instagram"""
        svg_template = f'''
        <svg width="1080" height="1920" xmlns="http://www.w3.org/2000/svg">
            <style>
                .title {{ font: bold 72px sans-serif; fill: white; }}
                .description {{ font: 48px sans-serif; fill: white; }}
                .cta {{ font: bold 36px sans-serif; fill: #ff6b6b; }}
            </style>
            <rect width="100%" height="100%" fill="#333" rx="0"/>
            <text x="50%" y="40%" text-anchor="middle" class="title">{historia_data['titulo']}</text>
            <text x="50%" y="50%" text-anchor="middle" class="description">{historia_data['descripcion']}</text>
            <text x="50%" y="85%" text-anchor="middle" class="cta">{historia_data['cta']}</text>
        </svg>
        '''
        return svg_template