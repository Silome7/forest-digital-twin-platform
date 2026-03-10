from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

# ----------------------------
# Extensions (instances globales)
# ----------------------------
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")


# ----------------------------
# Application Factory
# ----------------------------
def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.config["JWT_SECRET_KEY"] = (
        "426a44482873e932a4b0fe2ccffa94db4ca30742f9a1466f92e1545002a4e39a"
    )

    # ----------------------------
    # Init Extensions
    # ----------------------------
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # ----------------------------
    # CORS
    # ----------------------------
    CORS(app, 
     origins="http://localhost:5173",
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])

    # ----------------------------
    # Flask-Login settings
    # ----------------------------
    login_manager.login_view = "auth.login"
    login_manager.login_message = (
        "Veuillez vous connecter pour accéder à cette page."
    )
    login_manager.login_message_category = "warning"

    # ----------------------------
    # Register Blueprints
    # ----------------------------
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.dashboarduser import dashboarduser_bp
    from app.routes.sensors import sensors_bp
    from app.routes.alerts import alerts_bp
    from app.routes.zones import zones_bp
        
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(dashboarduser_bp)
    app.register_blueprint(sensors_bp, url_prefix="/api/sensors")
    app.register_blueprint(alerts_bp, url_prefix="/api/alerts")
    app.register_blueprint(zones_bp)
    # ----------------------------
    # Import Models
    # ----------------------------
    from app.models.user import User
    from app.models.roles import Role
    from app.models.associations import user_roles
    from app.models.sensor import Sensor
    from app.models.sensor_data import SensorData
    from app.models.alert import Alert

    # ----------------------------
    # Import Services
    # ----------------------------
    from app.services.sensor_service import start_sensor_thread
    from app.services.role_service import RoleService

    # ----------------------------
    # User loader for Flask-Login
    # ----------------------------
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ----------------------------
    # Database initialization
    # ----------------------------
    with app.app_context():
        db.create_all()

        # Seed default users (si DB vide)
        #if User.query.count() == 0:
        #    admin = User(
        #        email="admin@forest.com", role="admin", telephone="+123456789"
        #    )
        #    admin.set_password("admin123")

        #    agent = User(
        #        email="agent@forest.com",
        #       role="agent forestier",
        #        telephone="+123456725",
        #   )
        #     agent.set_password("agent123")

        #    chercheur = User(
        #        email="chercheur@forest.com",
        #        role="chercheur",
        #        telephone="+123256789",
        #    )
        #    chercheur.set_password("chercheur123")

        #    db.session.add_all([admin, agent, chercheur])
         #   db.session.commit()

        RoleService.initialize_default_roles()
        start_sensor_thread(app)

    # ----------------------------
    # Default route
    # ----------------------------
    @app.route("/")
    def home():
        return "Welcome to Forest Digital Twin API"

    return app
