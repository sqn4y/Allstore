from flask import Blueprint, render_template, abort, current_app
from ..models import Store, Product

catalog_bp = Blueprint("catalog", __name__)

@catalog_bp.route("/store/<slug>")
def store(slug):
    store = Store.query.filter_by(slug=slug).first_or_404()
    return render_template("catalog/catalog.html", store=store)

@catalog_bp.route("/store/<slug>/product/<int:product_id>")
def product(slug, product_id):
    store = Store.query.filter_by(slug=slug).first_or_404()
    product = Product.query.get_or_404(product_id)
    if product.category.store_id != store.id:
        abort(404)
    return render_template("catalog/product.html", store=store, product=product)

@catalog_bp.app_template_global()
def product_image_url(filename):
    if not filename:
        return None
    return f"/uploads/products/{filename}"
