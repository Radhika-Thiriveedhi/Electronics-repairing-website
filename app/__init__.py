import os
from flask import Flask, render_template
from flask_login import LoginManager
from app.services.auth_service import User
from app.storage.json_store import init_all_json_files

login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "fixloop_secret_key_987654321_prototype"
    app.config["UPLOAD_FOLDER"] = os.path.join(app.static_folder, "uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize data store
    init_all_json_files()

    # Flask-Login setup
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please sign in to access this page."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # Register Route Blueprints
    from app.routes.public import public_bp
    from app.routes.auth import auth_bp
    from app.routes.customer import customer_bp
    from app.routes.shop import shop_bp
    from app.routes.technician import technician_bp
    from app.routes.owner import owner_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(technician_bp)
    app.register_blueprint(owner_bp)

    # Error handlers
    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    return app
