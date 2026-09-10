from urllib.parse import quote
from flask import Blueprint, session, redirect, url_for, render_template, request, abort
from ..models import Store, Product

cart_bp = Blueprint("cart", __name__)

def get_cart():
    return session.get("cart", {})

def save_cart(cart):
    session["cart"] = cart
    session.modified = True

@cart_bp.app_context_processor
def cart_context():
    cart = get_cart()
    return {"cart_count": sum(int(q) for q in cart.values())}

@cart_bp.post("/store/<slug>/cart/add/<int:product_id>")
def add(slug, product_id):
    store = Store.query.filter_by(slug=slug).first_or_404()
    product = Product.query.get_or_404(product_id)
    if product.category.store_id != store.id:
        abort(404)
    cart = get_cart()
    key = str(product.id)
    cart[key] = int(cart.get(key, 0)) + 1
    save_cart(cart)
    session["cart_store"] = store.id
    return redirect(request.referrer or url_for("catalog.store", slug=slug))

@cart_bp.post("/store/<slug>/cart/update/<int:product_id>")
def update(slug, product_id):
    store = Store.query.filter_by(slug=slug).first_or_404()
    product = Product.query.get_or_404(product_id)
    if product.category.store_id != store.id:
        abort(404)
    action = request.form.get("action")
    cart = get_cart()
    key = str(product.id)
    current = int(cart.get(key, 0))
    if action == "increase":
        cart[key] = current + 1
    elif action == "decrease":
        if current <= 1:
            cart.pop(key, None)
        else:
            cart[key] = current - 1
    save_cart(cart)
    return redirect(url_for("cart.view", slug=slug))

@cart_bp.post("/store/<slug>/cart/remove/<int:product_id>")
def remove(slug, product_id):
    Store.query.filter_by(slug=slug).first_or_404()
    cart = get_cart()
    cart.pop(str(product_id), None)
    save_cart(cart)
    return redirect(url_for("cart.view", slug=slug))

@cart_bp.post("/store/<slug>/cart/select/<int:product_id>")
def select(slug, product_id):
    store = Store.query.filter_by(slug=slug).first_or_404()
    product = Product.query.get_or_404(product_id)
    if product.category.store_id != store.id:
        abort(404)
    selected = set(session.get("cart_selected", []))
    key = str(product.id)
    if key in selected:
        selected.remove(key)
    else:
        selected.add(key)
    session["cart_selected"] = list(selected)
    return redirect(url_for("cart.view", slug=slug))

@cart_bp.route("/store/<slug>/cart")
def view(slug):
    store = Store.query.filter_by(slug=slug).first_or_404()
    products = []
    total = 0
    selected = set(session.get("cart_selected", []))
    for pid, qty in get_cart().items():
        product = Product.query.get(int(pid))
        if product and product.category.store_id == store.id:
            subtotal = float(product.price) * int(qty)
            products.append((product, int(qty), str(pid) in selected, subtotal))
            if str(pid) in selected:
                total += subtotal
    return render_template("cart/cart.html", store=store, products=products, total=total)

@cart_bp.post("/store/<slug>/cart/clear")
def clear(slug):
    Store.query.filter_by(slug=slug).first_or_404()
    session.pop("cart", None)
    session.pop("cart_selected", None)
    return redirect(url_for("cart.view", slug=slug))

@cart_bp.post("/store/<slug>/cart/order")
def order(slug):
    store = Store.query.filter_by(slug=slug).first_or_404()
    if not store.whatsapp_number:
        return redirect(url_for("cart.view", slug=slug))
    selected = set(session.get("cart_selected", []))
    lines = ["Здравствуйте! Хочу заказать:", ""]
    total = 0
    for pid, qty in get_cart().items():
        if str(pid) not in selected:
            continue
        product = Product.query.get(int(pid))
        if product and product.category.store_id == store.id:
            subtotal = float(product.price) * int(qty)
            total += subtotal
            lines.append(f"{product.name} × {qty} — {subtotal:.2f}")
            if product.short_description:
                lines.append(f"Описание: {product.short_description}")
            lines.append(url_for("catalog.product", slug=store.slug, product_id=product.id, _external=True))
            lines.append("")
    if total == 0:
        return redirect(url_for("cart.view", slug=slug))
    lines.append(f"Итого: {total:.2f}")
    message = quote("\n".join(lines))
    phone = "".join(ch for ch in store.whatsapp_number if ch.isdigit())
    session.pop("cart_selected", None)
    return redirect(f"https://wa.me/{phone}?text={message}")
