from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.services.auth_service import User, register_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect_role_dashboard(current_user.role)

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = User.get_by_email(email)
        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.name}!", "success")
            return redirect_role_dashboard(user.role)
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect_role_dashboard(current_user.role)

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        name = request.form.get("name", "").strip()
        role = request.form.get("role", "customer")
        phone = request.form.get("phone", "").strip()

        if not email or not password or not name:
            flash("Please fill in all required fields.", "warning")
            return render_template("register.html")

        user, message = register_user(email, password, name, role, phone)
        if user:
            login_user(user)
            flash(f"Account created successfully! Welcome to FixLoop, {user.name}.", "success")
            return redirect_role_dashboard(user.role)
        else:
            flash(message, "danger")

    return render_template("register.html")

@auth_bp.route("/demo-login/<role>")
def demo_login(role):
    """Quick demo login route for rapid testing across roles."""
    role_email_map = {
        "customer": "customer@fixloop.org",
        "shop": "shop@fixloop.org",
        "technician": "technician@fixloop.org",
        "owner": "owner@fixloop.org"
    }

    target_email = role_email_map.get(role)
    if not target_email:
        flash("Invalid demo role.", "danger")
        return redirect(url_for("auth.login"))

    user = User.get_by_email(target_email)
    if user:
        login_user(user)
        flash(f"Logged in as Demo {role.title()} ({user.name}).", "info")
        return redirect_role_dashboard(user.role)
    else:
        flash("Demo account not found.", "danger")
        return redirect(url_for("auth.login"))

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("public.home"))

def redirect_role_dashboard(role):
    if role == "customer":
        return redirect(url_for("customer.dashboard"))
    elif role == "shop":
        return redirect(url_for("shop.dashboard"))
    elif role == "technician":
        return redirect(url_for("technician.dashboard"))
    elif role == "owner":
        return redirect(url_for("owner.dashboard"))
    return redirect(url_for("public.home"))
