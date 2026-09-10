from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from ..models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("seller.dashboard"))
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username", "").strip()).first()
        if user and user.is_active and user.check_password(request.form.get("password", "")):
            login_user(user)
            return redirect(url_for("admin.dashboard" if user.is_admin else "seller.dashboard"))
        flash("Неверный логин или пароль.", "error")
    return render_template("auth/login.html")

@auth_bp.post("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
