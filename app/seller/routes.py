import os, uuid
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from ..extensions import db
from ..models import Category, Product, Store

seller_bp = Blueprint("seller", __name__, url_prefix="/seller")

def seller_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.is_admin:
            return redirect(url_for("admin.dashboard"))
        return fn(*args, **kwargs)
    return wrapper

@seller_bp.route("/")
@seller_required
def dashboard():
    return render_template("seller/dashboard.html", store=current_user.store)

@seller_bp.route("/settings", methods=["GET", "POST"])
@seller_required
def settings():
    if request.method == "POST":
        name = request.form.get("name", "").strip() or "Мой каталог"
        current_user.store.name = name
        current_user.store.slug = Store.make_unique_slug(name, current_user.store.id)
        current_user.store.whatsapp_number = request.form.get("whatsapp_number", "").strip()
        db.session.commit()
        flash("Настройки сохранены.", "success")
    return render_template("seller/store_settings.html", store=current_user.store)

@seller_bp.route("/categories", methods=["GET", "POST"])
@seller_required
def categories():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name:
            db.session.add(Category(name=name, store=current_user.store))
            db.session.commit()
    return render_template("seller/categories.html", categories=current_user.store.categories)

@seller_bp.post("/categories/<int:category_id>/delete")
@seller_required
def delete_category(category_id):
    category = db.session.get(Category, category_id)
    if category and category.store_id == current_user.store.id:
        db.session.delete(category)
        db.session.commit()
    return redirect(url_for("seller.categories"))

@seller_bp.route("/products/new", methods=["GET", "POST"])
@seller_required
def new_product():
    categories = current_user.store.categories
    if request.method == "POST":
        category = db.session.get(Category, int(request.form["category_id"]))
        if not category or category.store_id != current_user.store.id:
            flash("Некорректная категория.", "error")
            return redirect(url_for("seller.new_product"))
        image = request.files.get("image")
        filename = None
        if image and image.filename:
            ext = image.filename.rsplit(".", 1)[-1].lower()
            if ext not in current_app.config["ALLOWED_EXTENSIONS"]:
                flash("Недопустимый формат изображения.", "error")
                return redirect(url_for("seller.new_product"))
            filename = f"{uuid.uuid4().hex}.{ext}"
            image.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        product = Product(
            name=request.form.get("name", "").strip(),
            short_description=request.form.get("short_description", "").strip(),
            description=request.form.get("description", "").strip(),
            price=request.form.get("price", "0"),
            image_filename=filename,
            category=category,
        )
        db.session.add(product)
        db.session.commit()
        return redirect(url_for("seller.products"))
    return render_template("seller/product_form.html", categories=categories, product=None)

@seller_bp.route("/products")
@seller_required
def products():
    products = Product.query.join(Category).filter(Category.store_id == current_user.store.id).all()
    return render_template("seller/products.html", products=products)

@seller_bp.post("/products/<int:product_id>/delete")
@seller_required
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if product and product.category.store_id == current_user.store.id:
        if product.image_filename:
            try:
                os.remove(os.path.join(current_app.config["UPLOAD_FOLDER"], product.image_filename))
            except FileNotFoundError:
                pass
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for("seller.products"))
