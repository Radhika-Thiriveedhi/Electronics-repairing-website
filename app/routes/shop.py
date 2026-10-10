from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.repair_service import (
    get_repairs_for_shop,
    get_repair_by_id,
    update_repair_status,
    assign_technician
)
from app.services.quote_service import create_quote, get_quote_for_repair
from app.services.auth_service import get_technicians_for_shop
from app.services.analytics_service import get_shop_analytics
from app.storage.json_store import read_json, write_json
from app.storage.id_generator import generate_id

shop_bp = Blueprint("shop", __name__, url_prefix="/shop")

def shop_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "shop":
            flash("Access restricted to Repair Shop owners.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@shop_bp.route("/dashboard")
@login_required
@shop_required
def dashboard():
    shop_id = current_user.shop_id
    repairs = get_repairs_for_shop(shop_id)
    technicians = get_technicians_for_shop(shop_id)
    stats = get_shop_analytics(shop_id)

    incoming = [r for r in repairs if r["status"] == "Received"]
    awaiting_quote = [r for r in repairs if r["status"] == "Diagnosing" and not r.get("quote_id")]
    awaiting_approval = [r for r in repairs if r["status"] == "Waiting for Approval"]
    active = [r for r in repairs if r["status"] in ["Repairing", "Ready for Collection"]]
    completed = [r for r in repairs if r["status"] == "Completed"]

    return render_template(
        "shop/dashboard.html",
        incoming=incoming,
        awaiting_quote=awaiting_quote,
        awaiting_approval=awaiting_approval,
        active=active,
        completed=completed,
        technicians=technicians,
        stats=stats
    )

@shop_bp.route("/requests")
@login_required
@shop_required
def requests_list():
    shop_id = current_user.shop_id
    repairs = get_repairs_for_shop(shop_id)
    technicians = get_technicians_for_shop(shop_id)
    return render_template("shop/requests.html", repairs=repairs, technicians=technicians)

@shop_bp.route("/repair/<repair_id>/action", methods=["POST"])
@login_required
@shop_required
def repair_action(repair_id):
    action = request.form.get("action")
    repair = get_repair_by_id(repair_id)
    if not repair or repair["shop_id"] != current_user.shop_id:
        flash("Repair request not found.", "danger")
        return redirect(url_for("shop.dashboard"))

    if action == "accept":
        update_repair_status(repair_id, "Diagnosing")
        flash(f"Accepted repair request '{repair['item_name']}'. Now in Diagnosis.", "success")
    elif action == "reject":
        update_repair_status(repair_id, "Declined")
        flash(f"Rejected repair request '{repair['item_name']}'.", "info")

    return redirect(url_for("shop.dashboard"))

@shop_bp.route("/quote/<repair_id>", methods=["GET", "POST"])
@login_required
@shop_required
def quote_form(repair_id):
    repair = get_repair_by_id(repair_id)
    if not repair or repair["shop_id"] != current_user.shop_id:
        flash("Repair record not found.", "danger")
        return redirect(url_for("shop.dashboard"))

    existing_quote = get_quote_for_repair(repair_id)

    if request.method == "POST":
        min_cost = request.form.get("min_cost", 0)
        max_cost = request.form.get("max_cost", 0)
        final_cost = request.form.get("final_cost", 0)
        ready_time = request.form.get("ready_time", "2 Business Days")
        notes = request.form.get("notes", "")

        quote, msg = create_quote(
            repair_id=repair_id,
            min_estimated_cost=min_cost,
            max_estimated_cost=max_cost,
            final_quoted_amount=final_cost,
            estimated_completion_time=ready_time,
            technician_notes=notes
        )

        if quote:
            flash(msg, "success")
            return redirect(url_for("shop.dashboard"))
        else:
            flash(msg, "danger")

    return render_template("shop/quote_form.html", repair=repair, quote=existing_quote)

@shop_bp.route("/assign-tech/<repair_id>", methods=["POST"])
@login_required
@shop_required
def assign_tech(repair_id):
    technician_id = request.form.get("technician_id")
    success, msg = assign_technician(repair_id, technician_id)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")
    return redirect(url_for("shop.dashboard"))

@shop_bp.route("/parts", methods=["GET", "POST"])
@login_required
@shop_required
def parts_inventory():
    shop_id = current_user.shop_id
    parts = [p for p in read_json("parts.json") if p.get("shop_id") == shop_id]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        sku = request.form.get("sku", "").strip()
        qty = int(request.form.get("qty", 0))
        cost = float(request.form.get("cost", 0))
        price = float(request.form.get("price", 0))

        if name and sku:
            all_parts = read_json("parts.json")
            new_part = {
                "id": generate_id("PRT"),
                "shop_id": shop_id,
                "name": name,
                "sku": sku,
                "stock_quantity": qty,
                "cost_price": cost,
                "selling_price": price
            }
            all_parts.append(new_part)
            write_json("parts.json", all_parts)
            flash(f"Spare part '{name}' added to inventory.", "success")
            return redirect(url_for("shop.parts_inventory"))

    return render_template("shop/parts.html", parts=parts)
