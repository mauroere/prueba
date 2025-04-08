import os
import streamlit as st
from dotenv import load_dotenv
from modules.content_generator import ContentGenerator
from modules.campaign_manager import CampaignManager
from modules.competitor_analyzer import CompetitorAnalyzer
from modules.influencer_finder import InfluencerFinder
from modules.user_manager import UserManager
from modules.dashboard_manager import DashboardManager
from modules.logger_config import LoggerConfig
from modules.trend_analyzer import TrendAnalyzer
from modules.notification_manager import NotificationManager

# Cargar variables de entorno
load_dotenv()

# Configurar logger
logger = LoggerConfig().get_logger('main')
logger.info('Iniciando aplicación')

# Configurar modo de depuración
debug_mode = os.getenv('DEBUG', 'False').lower() == 'true'

# Inicialización de módulos
try:
    content_gen = ContentGenerator()
    campaign_mgr = CampaignManager()
    competitor_analyzer = CompetitorAnalyzer()
    influencer_finder = InfluencerFinder()
    user_manager = UserManager()
    dashboard_manager = DashboardManager()
    trend_analyzer = TrendAnalyzer()
    notification_manager = NotificationManager()
    logger.info('Módulos inicializados correctamente')
except Exception as e:
    logger.error(f'Error al inicializar módulos: {str(e)}')
    st.error('Error al inicializar la aplicación. Por favor, contacte al administrador.')
    st.stop()

# Configuración de la página
st.set_page_config(
    page_title="Asistente IA para Tiendas Nuevas en Tiendanube",
    page_icon="🛍️",
    layout="wide"
)

# Título y descripción
st.title("🛍️ Asistente IA para Tiendas Nuevas en Tiendanube")
st.markdown("""
    Optimiza tu tienda en Tiendanube con la ayuda de la Inteligencia Artificial.
    Genera contenido, analiza la competencia y gestiona tus campañas de marketing.
""")

# Gestión de sesión
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# Login/Registro
if not st.session_state.user_id:
    st.sidebar.title("Acceso")
    login_option = st.sidebar.radio("Seleccione una opción", ["Iniciar Sesión", "Registrarse"])
    
    if login_option == "Iniciar Sesión":
        with st.sidebar.form("login_form"):
            email = st.text_input("Email")
            username = st.text_input("Usuario")
            if st.form_submit_button("Iniciar Sesión"):
                # Simulamos login básico
                user = next((u for u in user_manager.list_users() if u['email'] == email and u['username'] == username), None)
                if user:
                    st.session_state.user_id = user['user_id']
                    st.rerun()
                else:
                    st.error("Credenciales inválidas")
    else:
        with st.sidebar.form("register_form"):
            new_username = st.text_input("Usuario")
            new_email = st.text_input("Email")
            new_full_name = st.text_input("Nombre completo")
            if st.form_submit_button("Registrarse"):
                result = user_manager.create_user({
                    'username': new_username,
                    'email': new_email,
                    'full_name': new_full_name
                })
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.session_state.user_id = result['user_id']
                    st.success("Registro exitoso")
                    st.rerun()

# Si el usuario está autenticado
if st.session_state.user_id:
    user_data = user_manager.get_user_data(st.session_state.user_id)
    
    # Renderizar dashboard según el rol
    if user_data['role'] == 'admin':
        dashboard_manager.render_admin_dashboard(st.session_state.user_id)
    else:
        # Sidebar para navegación de usuario
        st.sidebar.title("Menú")
        option = st.sidebar.selectbox(
            "Selecciona una función",
            ["Dashboard", "Generador de Contenido", "Análisis de Competencia", "Plantillas de Campañas", "Buscador de Influencers", "Análisis de Tendencias", "Centro de Notificaciones"]
        )
        
        # Botón de cerrar sesión
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state.user_id = None
            st.rerun()

# URL de la tienda
tienda_url = st.text_input("Ingresa la URL de tu tienda en Tiendanube:")

# Contenedor principal
main_container = st.container()

with main_container:
    if not tienda_url:
        st.warning("Por favor, ingresa la URL de tu tienda para comenzar.")
    else:
        if option == "Generador de Contenido":
            st.header("📱 Generador de Contenido para Redes + SEO")
            plataforma = st.selectbox(
                "Selecciona la plataforma",
                ["Instagram", "TikTok", "Facebook"]
            )
            tipo_contenido = st.selectbox(
                "¿Qué tipo de contenido necesitas?",
                ["Post de producto", "Historia", "Descripción SEO"]
            )
            if st.button("Generar Contenido"):
                with st.spinner("Generando contenido..."):
                    if tipo_contenido == "Post de producto":
                        result = content_gen.generate_social_post(tienda_url, plataforma)
                    elif tipo_contenido == "Historia":
                        result = content_gen.generate_story(tienda_url)
                    else:  # Descripción SEO
                        result = content_gen.generate_seo_description(tienda_url)
                    
                    if 'error' not in result:
                        st.success("¡Contenido generado!")
                        st.text_area("Contenido sugerido", result['content'], height=200)
                    else:
                        st.error(result['error'])

        elif option == "Análisis de Competencia":
            st.header("📊 Analizador de Competencia")
            nicho = st.text_input("Nicho de mercado (ej: ropa, accesorios, etc.)")
            if st.button("Analizar Competencia"):
                with st.spinner("Analizando competencia..."):
                    result = competitor_analyzer.analyze_competition(tienda_url, nicho)
                    if 'error' not in result:
                        st.success("¡Análisis completado!")
                        
                        # Mostrar características propias
                        st.subheader("Tu tienda")
                        st.json(result['own_features'])
                        
                        # Mostrar características de competidores
                        st.subheader("Competidores")
                        for i, comp in enumerate(result['competitor_features'], 1):
                            st.write(f"Competidor {i}")
                            st.json(comp)
                        
                        # Mostrar recomendaciones
                        st.subheader("Recomendaciones")
                        st.write(result['recommendations'])
                    else:
                        st.error(result['error'])

        elif option == "Plantillas de Campañas":
            st.header("📧 Plantillas de Campañas")
            tipo_plantilla = st.selectbox(
                "Selecciona el tipo de plantilla",
                ["Cupón de lanzamiento", "Email marketing", "Historia de Instagram"]
            )
            tienda_data = {
                'nombre': st.text_input("Nombre de la tienda"),
                'descuento': st.number_input("Porcentaje de descuento", min_value=5, max_value=70, value=10),
                'codigo': st.text_input("Código de descuento (sin el prefijo)"),
                'url_tienda': tienda_url
            }
            
            if st.button("Generar Plantilla"):
                with st.spinner("Generando plantilla..."):
                    if tipo_plantilla == "Cupón de lanzamiento":
                        result = campaign_mgr.generate_coupon(tienda_data)
                        if 'error' not in result:
                            st.success("¡Cupón generado!")
                            st.code(result['imagen'], language='svg')
                        else:
                            st.error(result['error'])
                    
                    elif tipo_plantilla == "Email marketing":
                        result = campaign_mgr.generate_email('bienvenida', tienda_data)
                        if 'error' not in result:
                            st.success("¡Email generado!")
                            st.code(result['contenido'], language='html')
                        else:
                            st.error(result['error'])
                    
                    else:  # Historia de Instagram
                        result = campaign_mgr.generate_story('producto', tienda_data)
                        if 'error' not in result:
                            st.success("¡Historia generada!")
                            st.code(result['imagen'], language='svg')
                        else:
                            st.error(result['error'])

        elif option == "Buscador de Influencers":
            st.header("🔍 Identificador de Micro-Influencers")
            nicho = st.text_input("Ingresa el nicho de tu tienda (ejemplo: moda, tecnología, etc.):")
            ubicacion = st.text_input("Ubicación (ciudad/provincia en Argentina):")
            if st.button("Buscar Influencers"):
                with st.spinner("Buscando influencers..."):
                    result = influencer_finder.find_influencers(nicho, ubicacion)
                    if 'error' not in result:
                        st.success(f"¡Se encontraron {result['total_found']} influencers!")
                        
                        for inf in result['influencers']:
                            with st.expander(f"@{inf['username']} - {inf['engagement_rate']}% engagement"):
                                st.write(f"Seguidores: {inf['followers']}")
                                st.write(f"Posts: {inf['posts']}")
                                st.write(f"Likes promedio: {inf['avg_likes']}")
                                st.write(f"Bio: {inf['bio']}")
                    else:
                        st.error(result['error'])

        elif option == "Análisis de Tendencias":
            st.header("📈 Análisis Predictivo de Tendencias")
            if st.button("Analizar Tendencias"):
                with st.spinner("Analizando tendencias..."):
                    result = trend_analyzer.analyze_trends(tienda_url)
                    if 'error' not in result:
                        st.success("¡Análisis completado!")
                        
                        # Mostrar predicciones
                        st.subheader("Predicciones para las próximas semanas")
                        predictions = result['predictions']
                        for fecha, valor in zip(predictions['fechas'], predictions['valores']):
                            st.metric(fecha, f"{valor:.2f}%")
                        
                        # Mostrar tendencias identificadas
                        st.subheader("Tendencias Identificadas")
                        for trend in result['trends']:
                            icon = "📈" if trend['direction'] == 'up' else "📉"
                            st.write(f"{icon} {trend['metric'].title()}: {abs(trend['change']):.1f}% de {trend['direction'] == 'up' and 'aumento' or 'disminución'}")
                        
                        # Mostrar recomendaciones
                        st.subheader("Recomendaciones")
                        for rec in result['recommendations']:
                            st.info(rec)
                    else:
                        st.error(result['error'])

        elif option == "Centro de Notificaciones":
            st.header("🔔 Centro de Notificaciones")
            
            # Verificar alertas
            alerts = notification_manager.check_alerts(tienda_url)
            
            if alerts:
                for alert in alerts:
                    with st.expander(f"{alert['title']} - {alert['timestamp']}"):
                        st.write(alert['message'])
                        st.write(f"Prioridad: {alert['priority'].upper()}")
                        
                        # Mostrar acciones disponibles
                        cols = st.columns(len(alert['actions']))
                        for i, action in enumerate(alert['actions']):
                            if cols[i].button(action['label'], key=f"{alert['timestamp']}_{action['name']}"):
                                st.write(f"Redirigiendo a {action['url']}...")
            else:
                st.info("No hay notificaciones nuevas en este momento.")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Desarrollado con ❤️ para emprendedores de Tiendanube</p>
        <p>Versión Beta 1.0</p>
    </div>
""", unsafe_allow_html=True)