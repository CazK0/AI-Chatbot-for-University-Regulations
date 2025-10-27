import os
from datetime import timedelta


class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'university-chatbot-secret-key-2024'

    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

    CHATBOT_NAME = "University Regulations Assistant"
    CHATBOT_VERSION = "1.0.0"
    MAX_MESSAGE_LENGTH = 500
    MAX_CONVERSATION_HISTORY = 50
    DEBUG_MODE = os.environ.get('DEBUG', 'True').lower() == 'true'
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'knowledge_base.json')
    ENABLE_LEARNING = False
    RATE_LIMIT_ENABLED = False
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_PERIOD = 3600

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    LOG_LEVEL = 'DEBUG'

    # Development database (REMEMBER ME, MIGHT USE)
    # DATABASE_URL = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///dev_chatbot.db'

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = 'WARNING'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    DATABASE_URL = 'sqlite:///test_chatbot.db'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    config_name = os.environ.get('FLASK_ENV', 'development')
    return config.get(config_name, config['default'])