import streamlit as st
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

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
                st.info("Generando contenido... (Función en desarrollo)")

        elif option == "Análisis de Competencia":
            st.header("📊 Analizador de Competencia")
            if st.button("Analizar Competencia"):
                st.info("Analizando competencia... (Función en desarrollo)")

        elif option == "Plantillas de Campañas":
            st.header("📧 Plantillas de Campañas")
            tipo_plantilla = st.selectbox(
                "Selecciona el tipo de plantilla",
                ["Cupón de lanzamiento", "Email marketing", "Historia de Instagram"]
            )
            if st.button("Generar Plantilla"):
                st.info("Generando plantilla... (Función en desarrollo)")

        elif option == "Buscador de Influencers":
            st.header("🔍 Identificador de Micro-Influencers")
            nicho = st.text_input("Ingresa el nicho de tu tienda (ejemplo: moda, tecnología, etc.):")
            ubicacion = st.text_input("Ubicación (ciudad/provincia en Argentina):")
            if st.button("Buscar Influencers"):
                st.info("Buscando influencers... (Función en desarrollo)")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Desarrollado con ❤️ para emprendedores de Tiendanube</p>
        <p>Versión Beta 1.0</p>
    </div>
""", unsafe_allow_html=True)