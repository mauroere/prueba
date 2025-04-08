# Asistente IA para Tiendas Nuevas en Tiendanube 🛍️

## Requisitos Previos

1. **Python 3.8 o superior**
   - Descarga Python desde [python.org](https://www.python.org/downloads/)
   - Durante la instalación, asegúrate de marcar la opción "Add Python to PATH"
   - Verifica la instalación abriendo una nueva terminal y ejecutando:
     ```bash
     python --version
     ```

2. **pip (gestor de paquetes de Python)**
   - pip viene incluido con Python, pero asegúrate de tenerlo actualizado:
     ```bash
     python -m pip install --upgrade pip
     ```
   - Verifica la instalación de pip:
     ```bash
     python -m pip --version
     ```

## Instalación

1. Clona o descarga este repositorio

2. Instala las dependencias necesarias:
```bash
pip install -r requirements.txt
```

## Ejecución del Proyecto

1. Abre una terminal en el directorio del proyecto

2. Ejecuta la aplicación con Streamlit:
```bash
streamlit run main.py
```

3. La aplicación se abrirá automáticamente en tu navegador predeterminado. Si no se abre automáticamente, puedes acceder a través de:
   - URL Local: http://localhost:8501

## Funcionalidades Principales

- **Generador de Contenido**: Crea contenido optimizado para redes sociales (Instagram, TikTok, Facebook)
- **Análisis de Competencia**: Analiza y compara tu tienda con la competencia
- **Plantillas de Campañas**: Genera plantillas para diferentes tipos de campañas
- **Buscador de Influencers**: Encuentra influencers relevantes para tu nicho

## Uso

1. Ingresa la URL de tu tienda Tiendanube
2. Selecciona la función que deseas utilizar en el menú lateral
3. Sigue las instrucciones específicas para cada herramienta

## Notas Importantes

- Asegúrate de tener todas las dependencias instaladas correctamente
- La aplicación requiere conexión a internet para funcionar
- Algunas funciones pueden requerir autenticación o tokens de API

## Despliegue en Producción

1. **Configuración del Entorno**
   - Crea un archivo `.env` en la raíz del proyecto
   - Configura las variables de entorno necesarias (API keys, tokens, etc.)

2. **Plataformas de Despliegue Recomendadas**
   - [Heroku](https://heroku.com)
   - [Streamlit Cloud](https://streamlit.io/cloud)
   - [Railway](https://railway.app)

3. **Pasos para el Despliegue**
   - Asegúrate de tener el archivo `requirements.txt` actualizado
   - Configura las variables de entorno en la plataforma de despliegue
   - Conecta tu repositorio de GitHub con la plataforma elegida
   - Sigue las instrucciones específicas de la plataforma para el despliegue

4. **Consideraciones de Seguridad**
   - No incluyas archivos de configuración sensibles en el repositorio
   - Utiliza variables de entorno para las credenciales
   - Mantén actualizadas las dependencias por seguridad