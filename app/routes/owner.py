from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services.analytics_service import get_platform_analytics
from app.storage.json_store import read_json, write_json
from app.storage.id_generator import generate_id

owner_bp = Blueprint("owner", __name__, url_prefix="/owner")

def owner_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "owner":
            flash("Access restricted to Platform Owner.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@owner_bp.route("/dashboard")
@login_required
@owner_required
def dashboard():
    analytics = get_platform_analytics()
    shops = read_json("shops.json")
    recent_repairs = read_json("repairs.json")[-5:]
    recent_reviews = read_json("reviews.json")[-5:]

    return render_template(
        "owner/dashboard.html",
        analytics=analytics,
        shops=shops,
        recent_repairs=reversed(recent_repairs),
        recent_reviews=reversed(recent_reviews)
    )

@owner_bp.route("/shops", methods=["GET", "POST"])
@login_required
@owner_required
def shops_management():
    shops = read_json("shops.json")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        address = request.form.get("address", "").strip()
        contact = request.form.get("contact", "").strip()
        categories_str = request.form.get("categories", "")
        description = request.form.get("description", "").strip()

        if name and address:
            cat_list = [c.strip() for c in categories_str.split(",") if c.strip()]
            new_shop = {
                "id": generate_id("SHP"),
                "name": name,
                "owner_id": f"usr_owner_{generate_id('MGR')}",
                "categories": cat_list if cat_list else ["General Electronics"],
                "rating": 5.0,
                "address": address,
                "contact": contact,
                "description": description
            }
            shops.append(new_shop)
            write_json("shops.json", shops)
            flash(f"Repair shop '{name}' successfully registered on platform.", "success")
            return redirect(url_for("owner.shops_management"))

    return render_template("owner/shops.html", shops=shops)

@owner_bp.route("/api/chart-data")
@login_required
@owner_required
def chart_data_api():
    analytics = get_platform_analytics()
    return jsonify({
        "labels": analytics["chart_labels"],
        "revenue": analytics["chart_revenue"],
        "jobs": analytics["chart_jobs"],
        "categories": analytics["category_counts"]
    })
