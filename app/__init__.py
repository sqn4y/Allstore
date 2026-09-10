import os
from flask import Flask
from .config import Config
from .extensions import db, login_manager

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from .models import User
    from .auth.routes import auth_bp
    from .admin.routes import admin_bp
    from .seller.routes import seller_bp
    from .catalog.routes import catalog_bp
    from .cart.routes import cart_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(seller_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(cart_bp)

    with app.app_context():
        db.create_all()
        _ensure_admin(app)
        _normalize_store_slugs()

    return app

def _ensure_admin(app):
    from .models import User
    if not User.query.filter_by(is_admin=True).first():
        admin = User(
            username=app.config["ADMIN_USERNAME"],
            is_admin=True,
            is_active=True,
        )
        admin.set_password(app.config["ADMIN_PASSWORD"])
        db.session.add(admin)
        db.session.commit()

def _normalize_store_slugs():
    from .models import Store
    for store in Store.query.all():
        desired = Store.make_unique_slug(store.name, store.id)
        if store.slug != desired:
            store.slug = desired
    db.session.commit()
