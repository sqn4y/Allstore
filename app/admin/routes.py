from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from sqlalchemy import func
from ..extensions import db
from ..models import User, Store, Category, Product

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for("seller.dashboard"))
        return fn(*args, **kwargs)
    return wrapper

@admin_bp.route("/")
@admin_required
def dashboard():
    sellers = (
        db.session.query(
            User,
            func.count(Product.id).label("product_count"),
            func.count(Category.id).label("category_count"),
        )
        .outerjoin(Store, Store.owner_id == User.id)
        .outerjoin(Category, Category.store_id == Store.id)
        .outerjoin(Product, Product.category_id == Category.id)
        .filter(User.is_admin.is_(False))
        .group_by(User.id)
        .order_by(User.id.desc())
        .all()
    )
    return render_template("admin/dashboard.html", sellers=sellers)

@admin_bp.route("/users", methods=["GET", "POST"])
@admin_required
def users():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        store_name = request.form.get("store_name", "").strip() or "Мой каталог"
        if not username or not password:
            flash("Логин и пароль обязательны.", "error")
        elif User.query.filter_by(username=username).first():
            flash("Такой логин уже существует.", "error")
        else:
            user = User(username=username)
            user.set_password(password)
            user.store = Store(name=store_name, slug=Store.make_unique_slug(store_name))
            db.session.add(user)
            db.session.commit()
            flash("Продавец создан.", "success")
            return redirect(url_for("admin.dashboard"))
    return render_template("admin/users.html", users=User.query.filter_by(is_admin=False).all())

@admin_bp.post("/users/<int:user_id>/delete")
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for("admin.dashboard"))
