import os

from flask import Flask, send_from_directory


def create_app():
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

    app = Flask(__name__, static_folder=static_dir, static_url_path="")

    from app.routes.auth import auth_bp
    from app.routes.employees import employees_bp
    from app.routes.attendance import attendance_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(dashboard_bp)

    @app.route("/")
    def index():
        return send_from_directory(static_dir, "index.html")

    # SPA-friendly fallback: any unknown non-API path -> index.html
    @app.errorhandler(404)
    def not_found(e):
        from flask import request
        if request.path.startswith("/api/"):
            return {"error": "Not found"}, 404
        return send_from_directory(static_dir, "index.html")

    return app
