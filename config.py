import os
from dotenv import load_dotenv
load_dotenv(override=False)
def _bool(name,default="false"):return os.getenv(name,default).strip().lower() in ("1","true","yes","on")
def _int(name,default):return int(os.getenv(name,str(default)))
class BaseConfig:
    TESTING=False;DEBUG=False;SECRET_KEY=os.getenv("SECRET_KEY","dev-secret-change-me");JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY","dev-jwt-secret-change-me");JWT_EXPIRES_HOURS=_int("JWT_EXPIRES_HOURS",24);JWT_COOKIE_SECURE=True;JWT_COOKIE_CSRF_PROTECT=True
    SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL","mysql+pymysql://root:Kavi%40123@localhost/quiz_portal");SQLALCHEMY_TRACK_MODIFICATIONS=False
    SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping":True,"pool_size":_int("DB_POOL_SIZE",10),"max_overflow":_int("DB_MAX_OVERFLOW",20),"pool_timeout":_int("DB_POOL_TIMEOUT",30),"pool_recycle":_int("DB_POOL_RECYCLE",1800),"connect_args":{"connect_timeout":_int("DB_CONNECT_TIMEOUT",10)}}
    CORS_ORIGINS=os.getenv("CORS_ORIGINS","http://localhost:5173");SESSION_COOKIE_SAMESITE="Lax";SESSION_COOKIE_SECURE=_bool("SESSION_COOKIE_SECURE","true");UPLOAD_FOLDER=os.path.join(os.path.dirname(os.path.abspath(__file__)),"uploads");MAX_CONTENT_LENGTH=_int("MAX_UPLOAD_MB",5)*1024*1024
    REDIS_URL=os.getenv("REDIS_URL","redis://localhost:6379/0");RATELIMIT_ENABLED=_bool("RATELIMIT_ENABLED","true");RATELIMIT_STORAGE_URI=os.getenv("RATELIMIT_STORAGE_URI",REDIS_URL);HEARTBEAT_INTERVAL_SECONDS=_int("HEARTBEAT_INTERVAL_SECONDS",30);PRESENCE_TTL_SECONDS=_int("PRESENCE_TTL_SECONDS",75);MONITORING_CACHE_SECONDS=_int("MONITORING_CACHE_SECONDS",3)
    MAIL_SERVER=os.getenv("MAIL_SERVER");MAIL_PORT=_int("MAIL_PORT",587);MAIL_USE_TLS=_bool("MAIL_USE_TLS","true");MAIL_USERNAME=os.getenv("MAIL_USERNAME");MAIL_PASSWORD=os.getenv("MAIL_PASSWORD");MAIL_FROM=os.getenv("MAIL_FROM") or MAIL_USERNAME;MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME","Quiz");ADMIN_ALERT_EMAIL=os.getenv("ADMIN_ALERT_EMAIL") or MAIL_USERNAME
    CELERY_BROKER_URL=os.getenv("CELERY_BROKER_URL",REDIS_URL);CELERY_RESULT_BACKEND=os.getenv("CELERY_RESULT_BACKEND",REDIS_URL);SITE_URL=os.getenv("SITE_URL","http://localhost:5173");LOG_LEVEL=os.getenv("LOG_LEVEL","INFO")
class DevelopmentConfig(BaseConfig):DEBUG=_bool("FLASK_DEBUG","true");SESSION_COOKIE_SECURE=False
class TestingConfig(BaseConfig):TESTING=True;RATELIMIT_ENABLED=False;SQLALCHEMY_ENGINE_OPTIONS={}
class ProductionConfig(BaseConfig):
    @classmethod
    def validate(cls):
        missing=[n for n in ("DATABASE_URL","JWT_SECRET_KEY","SECRET_KEY","CORS_ORIGINS","REDIS_URL") if not os.getenv(n)];weak=[n for n in ("JWT_SECRET_KEY","SECRET_KEY") if len(os.getenv(n,""))<32]
        if missing or weak:raise RuntimeError(f"Unsafe production configuration; missing={missing}, weak={weak}")
CONFIGS={"development":DevelopmentConfig,"testing":TestingConfig,"production":ProductionConfig};Config=CONFIGS.get(os.getenv("FLASK_ENV","development").lower(),DevelopmentConfig)
