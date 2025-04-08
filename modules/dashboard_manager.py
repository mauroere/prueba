import streamlit as st
from typing import Dict, Optional
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from .user_manager import UserManager

class DashboardManager:
    def __init__(self):
        self.user_manager = UserManager()

    def render_user_dashboard(self, user_id: str):
        """Renderiza el dashboard del usuario"""
        user_data = self.user_manager.get_user_data(user_id)
        if 'error' in user_data:
            st.error(user_data['error'])
            return

        # Menú lateral
        st.sidebar.title(f"Bienvenido, {user_data['username']}")
        dashboard_option = st.sidebar.selectbox(
            "Panel de Control",
            ["Resumen", "Perfil", "Preferencias", "Analíticas", "Notificaciones"]
        )

        if dashboard_option == "Resumen":
            self._render_user_summary(user_data)
        elif dashboard_option == "Perfil":
            self._render_profile_editor(user_id, user_data)
        elif dashboard_option == "Preferencias":
            self._render_preferences_editor(user_id, user_data)
        elif dashboard_option == "Analíticas":
            self._render_user_analytics(user_data)
        elif dashboard_option == "Notificaciones":
            self._render_notification_settings(user_id, user_data)

    def render_admin_dashboard(self, admin_id: str):
        """Renderiza el dashboard del administrador"""
        admin_data = self.user_manager.get_user_data(admin_id)
        if 'error' in admin_data or admin_data['role'] != 'admin':
            st.error("Acceso no autorizado")
            return

        st.sidebar.title("Panel de Administración")
        admin_option = st.sidebar.selectbox(
            "Gestión",
            ["Resumen General", "Gestión de Usuarios", "Métricas", "Configuración"]
        )

        if admin_option == "Resumen General":
            self._render_admin_summary()
        elif admin_option == "Gestión de Usuarios":
            self._render_user_management()
        elif admin_option == "Métricas":
            self._render_admin_metrics()
        elif admin_option == "Configuración":
            self._render_admin_settings(admin_id)

    def _render_user_summary(self, user_data: Dict):
        """Renderiza el resumen del usuario"""
        st.title("📊 Resumen de Actividad")
        
        # Métricas principales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Campañas Activas", "5")
        with col2:
            st.metric("Engagement Rate", "4.2%")
        with col3:
            st.metric("Influencers Contactados", "12")

        # Gráfico de actividad reciente
        st.subheader("Actividad Reciente")
        dates = [datetime.now() - timedelta(days=x) for x in range(7)]
        activity = [4, 6, 3, 7, 5, 8, 4]
        fig = go.Figure(data=go.Scatter(x=dates, y=activity, mode='lines+markers'))
        fig.update_layout(title='Actividad Semanal')
        st.plotly_chart(fig)

    def _render_profile_editor(self, user_id: str, user_data: Dict):
        """Renderiza el editor de perfil"""
        st.title("✏️ Editar Perfil")
        
        with st.form("profile_form"):
            full_name = st.text_input("Nombre completo", user_data['full_name'])
            email = st.text_input("Email", user_data['email'])
            bio = st.text_area("Biografía", user_data.get('bio', ''))
            location = st.text_input("Ubicación", user_data.get('location', ''))
            store_url = st.text_input("URL de la tienda", user_data.get('store_url', ''))
            
            # Enlaces sociales
            st.subheader("Enlaces Sociales")
            social_links = user_data.get('social_links', {})
            instagram = st.text_input("Instagram", social_links.get('instagram', ''))
            facebook = st.text_input("Facebook", social_links.get('facebook', ''))
            tiktok = st.text_input("TikTok", social_links.get('tiktok', ''))
            
            if st.form_submit_button("Guardar Cambios"):
                update_data = {
                    'full_name': full_name,
                    'email': email,
                    'bio': bio,
                    'location': location,
                    'store_url': store_url,
                    'social_links': {
                        'instagram': instagram,
                        'facebook': facebook,
                        'tiktok': tiktok
                    }
                }
                result = self.user_manager.update_user(user_id, update_data)
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.success("Perfil actualizado correctamente")

    def _render_preferences_editor(self, user_id: str, user_data: Dict):
        """Renderiza el editor de preferencias"""
        st.title("⚙️ Preferencias")
        
        preferences = user_data.get('preferences', {})
        with st.form("preferences_form"):
            theme = st.selectbox(
                "Tema",
                ["light", "dark"],
                index=["light", "dark"].index(preferences.get('theme', 'light'))
            )
            language = st.selectbox(
                "Idioma",
                ["es", "en"],
                index=["es", "en"].index(preferences.get('language', 'es'))
            )
            
            if st.form_submit_button("Guardar Preferencias"):
                result = self.user_manager.update_preferences(user_id, {
                    'theme': theme,
                    'language': language
                })
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.success("Preferencias actualizadas correctamente")

    def _render_user_analytics(self, user_data: Dict):
        """Renderiza las analíticas del usuario"""
        st.title("📈 Analíticas")
        
        # Métricas de rendimiento
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Tasa de Conversión", "2.8%", "+0.3%")
            st.metric("Visitas Mensuales", "1,234", "+12%")
        with col2:
            st.metric("Tiempo Promedio", "3:45 min", "-0:30")
            st.metric("Tasa de Rebote", "45%", "-2%")

        # Gráfico de tendencias
        st.subheader("Tendencias de Engagement")
        dates = [datetime.now() - timedelta(days=x) for x in range(30)]
        engagement = [round(4 + x/10, 2) for x in range(30)]
        fig = px.line(x=dates, y=engagement, title='Engagement últimos 30 días')
        st.plotly_chart(fig)

    def _render_notification_settings(self, user_id: str, user_data: Dict):
        """Renderiza la configuración de notificaciones"""
        st.title("🔔 Configuración de Notificaciones")
        
        notification_settings = user_data.get('notification_settings', {})
        with st.form("notification_form"):
            email_notif = st.checkbox(
                "Notificaciones por Email",
                value=notification_settings.get('email', True)
            )
            push_notif = st.checkbox(
                "Notificaciones Push",
                value=notification_settings.get('push', True)
            )
            
            if st.form_submit_button("Guardar Configuración"):
                result = self.user_manager.update_user(user_id, {
                    'notification_settings': {
                        'email': email_notif,
                        'push': push_notif
                    }
                })
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.success("Configuración de notificaciones actualizada")

    def _render_admin_summary(self):
        """Renderiza el resumen general para administradores"""
        st.title("📊 Resumen General")
        
        # Métricas generales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Usuarios Totales", len(self.user_manager.list_users()))
        with col2:
            st.metric("Usuarios Activos", "45")
        with col3:
            st.metric("Nuevos Usuarios", "12", "+3")

        # Gráfico de actividad del sistema
        st.subheader("Actividad del Sistema")
        dates = [datetime.now() - timedelta(days=x) for x in range(30)]
        activity = [round(10 + x/5, 2) for x in range(30)]
        fig = px.line(x=dates, y=activity, title='Actividad últimos 30 días')
        st.plotly_chart(fig)

    def _render_user_management(self):
        """Renderiza la gestión de usuarios para administradores"""
        st.title("👥 Gestión de Usuarios")
        
        # Lista de usuarios
        users = self.user_manager.list_users()
        for user in users:
            with st.expander(f"Usuario: {user['username']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"Email: {user['email']}")
                    st.write(f"Rol: {user['role']}")
                    st.write(f"Creado: {user['created_at']}")
                with col2:
                    if user['role'] != 'admin':
                        if st.button(f"Eliminar {user['username']}"):
                            result = self.user_manager.delete_user(user['user_id'])
                            if 'error' in result:
                                st.error(result['error'])
                            else:
                                st.success(f"Usuario {user['username']} eliminado")
                                st.rerun()

    def _render_admin_metrics(self):
        """Renderiza las métricas del sistema para administradores"""
        st.title("📈 Métricas del Sistema")
        
        # Métricas de rendimiento
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Tiempo de Respuesta", "120ms", "-10ms")
            st.metric("Usuarios Concurrentes", "25", "+5")
        with col2:
            st.metric("Tasa de Error", "0.5%", "-0.2%")
            st.metric("Uso de CPU", "45%", "+10%")

        # Gráfico de uso del sistema
        st.subheader("Uso del Sistema")
        metrics = {
            'CPU': [45, 48, 42, 47, 43, 45, 44],
            'Memoria': [60, 62, 58, 65, 63, 61, 59],
            'Disco': [30, 32, 29, 31, 33, 30, 31]
        }
        fig = go.Figure()
        for metric, values in metrics.items():
            fig.add_trace(go.Scatter(name=metric, y=values, mode='lines+markers'))
        st.plotly_chart(fig)

    def _render_admin_settings(self, admin_id: str):
        """Renderiza la configuración del sistema para administradores"""
        st.title("⚙️ Configuración del Sistema")
        
        with st.form("admin_settings"):
            st.subheader("Configuración General")
            max_users = st.number_input("Máximo de usuarios", min_value=10, value=100)
            backup_frequency = st.selectbox(
                "Frecuencia de respaldo",
                ["Diario", "Semanal", "Mensual"]
            )
            
            st.subheader("Límites del Sistema")
            rate_limit = st.number_input("Límite de peticiones por minuto", min_value=10, value=60)
            storage_limit = st.number_input("Límite de almacenamiento (GB)", min_value=1, value=10)
            
            if st.form_submit_button("Guardar Configuración"):
                # Aquí se implementaría la lógica para guardar la configuración
                st.success("Configuración actualizada correctamente")