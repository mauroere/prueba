import streamlit as st
from modules.content_generator import ContentGenerator
from modules.campaign_manager import CampaignManager
from modules.competitor_analyzer import CompetitorAnalyzer
from modules.influencer_finder import InfluencerFinder

# Inicialización de módulos
content_gen = ContentGenerator()
campaign_mgr = CampaignManager()
competitor_analyzer = CompetitorAnalyzer()
influencer_finder = InfluencerFinder()

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

# Sidebar para navegación
st.sidebar.title("Menú")
option = st.sidebar.selectbox(
    "Selecciona una función",
    ["Generador de Contenido", "Análisis de Competencia", "Plantillas de Campañas", "Buscador de Influencers"]
)

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

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Desarrollado con ❤️ para emprendedores de Tiendanube</p>
        <p>Versión Beta 1.0</p>
    </div>
""", unsafe_allow_html=True)