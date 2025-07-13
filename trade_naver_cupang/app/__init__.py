from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config
from app.constants import LOG_FILE_NAME, LOG_FILE_MAX_BYTES, LOG_FILE_BACKUP_COUNT
import logging
from logging.handlers import RotatingFileHandler
import os

db = SQLAlchemy()


def create_app(config_name='default'):
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # 로깅 설정
    if not app.debug and not app.testing:
        log_dir = os.path.dirname(LOG_FILE_NAME)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        file_handler = RotatingFileHandler(
            LOG_FILE_NAME, 
            maxBytes=LOG_FILE_MAX_BYTES, 
            backupCount=LOG_FILE_BACKUP_COUNT
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('LogiFlow startup')
    
    # SQL 쿼리 로깅 설정 (개발 환경에서만)
    if app.config.get('SQLALCHEMY_ECHO'):
        logging.basicConfig()
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    
    # Register blueprints
    from app.routes import main, api
    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp, url_prefix='/api')
    
    # Register naver api blueprint
    from app.routes import naver_api
    app.register_blueprint(naver_api.bp)
    
    # Register coupang api blueprint
    from app.routes import coupang_api
    app.register_blueprint(coupang_api.bp)
    
    # Register integrated api blueprint
    from app.routes import integrated_api
    app.register_blueprint(integrated_api.bp)
    
    # Database initialization is handled separately by database/init_db.py
    
    return app