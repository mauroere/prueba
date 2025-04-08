import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

class LoggerConfig:
    def __init__(self):
        self.log_dir = 'logs'
        self.ensure_log_directory()
        self.setup_logger()

    def ensure_log_directory(self):
        """Asegura que el directorio de logs existe"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def setup_logger(self):
        """Configura el logger principal de la aplicación"""
        logger = logging.getLogger('tiendanube_assistant')
        logger.setLevel(logging.INFO)

        # Formato del log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Handler para archivo
        log_file = os.path.join(
            self.log_dir,
            f'app_{datetime.now().strftime("%Y%m%d")}.log'
        )
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    @staticmethod
    def get_logger(name):
        """Obtiene un logger configurado para un módulo específico"""
        return logging.getLogger(f'tiendanube_assistant.{name}')