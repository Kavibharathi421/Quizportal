from datetime import timedelta
import json, logging, time, uuid
from flask import Flask, jsonify, g, request
from sqlalchemy import text
try:from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
except ImportError:
    class _Metric:
        def labels(self,*_):return self
        def inc(self):pass
        def observe(self,*_):pass
    Counter=Histogram=lambda *_a,**_k:_Metric();generate_latest=lambda:b"# prometheus-client not installed\n";CONTENT_TYPE_LATEST="text/plain"
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from config import Config

db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
mail = Mail()
REQUESTS=Counter("exam_portal_http_requests_total","HTTP requests",["method","endpoint","status"])
LATENCY=Histogram("exam_portal_http_request_seconds","HTTP latency",["method","endpoint"])


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    if app.config.get("TESTING"):app.config["SQLALCHEMY_ENGINE_OPTIONS"]={}
    if config.__name__=="ProductionConfig":config.validate()
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=config.JWT_EXPIRES_HOURS)
    origins = config.CORS_ORIGINS.split(",") if config.CORS_ORIGINS != "*" else "*"
    CORS(app, resources={r"/api/*": {"origins": origins}})
    db.init_app(app); jwt.init_app(app); mail.init_app(app); Migrate(app, db); limiter.init_app(app)
    from .routes import api
    app.register_blueprint(api, url_prefix="/api")

    logging.basicConfig(level=getattr(logging,app.config["LOG_LEVEL"],logging.INFO),format="%(message)s")
    @app.before_request
    def begin_request():g.request_id=request.headers.get("X-Request-ID") or str(uuid.uuid4());g.request_started=time.perf_counter()
    @app.after_request
    def finish_request(response):
        elapsed=time.perf_counter()-g.get("request_started",time.perf_counter());endpoint=request.endpoint or "unknown";REQUESTS.labels(request.method,endpoint,response.status_code).inc();LATENCY.labels(request.method,endpoint).observe(elapsed);response.headers["X-Request-ID"]=g.get("request_id","");app.logger.info(json.dumps({"event":"http_request","request_id":g.get("request_id"),"method":request.method,"path":request.path,"status":response.status_code,"duration_ms":round(elapsed*1000,2)}));return response

    @app.get("/api/health")
    def health(): return jsonify({"success": True, "data": {"status": "ok"}})
    @app.get("/api/health/live")
    def live():return jsonify({"success":True,"data":{"status":"alive"}})
    @app.get("/api/health/ready")
    def ready():
        from .redis_service import available
        try:db.session.execute(text("SELECT 1"));database=True
        except Exception:database=False
        redis_ok=available();status=200 if database and redis_ok else 503;return jsonify({"success":status==200,"data":{"status":"ready" if status==200 else "not_ready","database":database,"redis":redis_ok}}),status
    @app.get("/internal/metrics")
    def metrics():return app.response_class(generate_latest(),mimetype=CONTENT_TYPE_LATEST)

    @app.errorhandler(404)
    def missing(_): return jsonify({"success": False, "message": "Resource not found"}), 404
    @app.errorhandler(500)
    def failed(_): return jsonify({"success": False, "message": "Unexpected server error"}), 500
    return app
