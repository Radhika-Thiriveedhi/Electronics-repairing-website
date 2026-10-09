import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.services.repair_service import (
    create_repair_request,
    get_repairs_for_customer,
    get_repair_by_id
)
from app.services.quote_service import (
    get_quote_for_repair,
    respond_to_quote,
    record_payment
)
from app.services.notification_service import get_notifications_for_user, mark_notification_as_read
from app.storage.json_store import read_json, write_json
from app.storage.id_generator import generate_id

customer_bp = Blueprint("customer", __name__, url_prefix="/customer")

def customer_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "customer":
            flash("Access restricted to customers.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@customer_bp.route("/dashboard")
@login_required
@customer_required
def dashboard():
    repairs = get_repairs_for_customer(current_user.id)
    notifications = get_notifications_for_user(current_user.id)
    quotes_map = {}
    for r in repairs:
        if r.get("quote_id"):
            quotes_map[r["id"]] = get_quote_for_repair(r["id"])

    return render_template(
        "customer/dashboard.html",
        repairs=repairs,
        notifications=notifications[:5],
        quotes_map=quotes_map
    )

@customer_bp.route("/repair/new", methods=["GET", "POST"])
@login_required
@customer_required
def new_repair():
    shops = read_json("shops.json")

    if request.method == "POST":
        item_name = request.form.get("item_name", "").strip()
        category = request.form.get("category", "").strip()
        shop_id = request.form.get("shop_id", "").strip()
        fault_description = request.form.get("fault_description", "").strip()
        delivery_type = request.form.get("delivery_type", "Drop-off at Shop")

        if not item_name or not shop_id or not fault_description:
            flash("Please fill in all required fields.", "warning")
            return render_template("customer/new_repair.html", shops=shops)

        photo_filename = None
        if "photo" in request.files:
            file = request.files["photo"]
            if file and file.filename != "":
                filename = secure_filename(file.filename)
                save_filename = f"repair_{generate_id('IMG')}_{filename}"
                from flask import current_app
                file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], save_filename))
                photo_filename = save_filename

        new_req = create_repair_request(
            customer_id=current_user.id,
            customer_name=current_user.name,
            shop_id=shop_id,
            item_name=item_name,
            category=category,
            fault_description=fault_description,
            delivery_type=delivery_type,
            photo_filename=photo_filename
        )

        flash(f"Repair request for '{item_name}' submitted successfully! Ticket ID: {new_req['id']}", "success")
        return redirect(url_for("customer.repair_detail", repair_id=new_req["id"]))

    return render_template("customer/new_repair.html", shops=shops)

@customer_bp.route("/repair/<repair_id>")
@login_required
@customer_required
def repair_detail(repair_id):
    repair = get_repair_by_id(repair_id)
    if not repair or repair["customer_id"] != current_user.id:
        flash("Repair record not found.", "danger")
        return redirect(url_for("customer.dashboard"))

    quote = get_quote_for_repair(repair_id)
    payments = read_json("payments.json")
    payment = next((p for p in payments if p["repair_id"] == repair_id and p["customer_id"] == current_user.id), None)
    
    reviews = read_json("reviews.json")
    existing_review = next((rev for rev in reviews if rev["repair_id"] == repair_id), None)

    return render_template(
        "customer/repair_detail.html",
        repair=repair,
        quote=quote,
        payment=payment,
        existing_review=existing_review
    )

@customer_bp.route("/repair/<repair_id>/respond-quote", methods=["POST"])
@login_required
@customer_required
def quote_action(repair_id):
    decision = request.form.get("decision")
    quote = get_quote_for_repair(repair_id)
    if not quote:
        flash("Quote not found.", "danger")
        return redirect(url_for("customer.repair_detail", repair_id=repair_id))

    success, msg = respond_to_quote(quote["id"], current_user.id, decision)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "danger")

    return redirect(url_for("customer.repair_detail", repair_id=repair_id))

@customer_bp.route("/repair/<repair_id>/pay", methods=["POST"])
@login_required
@customer_required
def process_payment(repair_id):
    repair = get_repair_by_id(repair_id)
    quote = get_quote_for_repair(repair_id)
    payment_method = request.form.get("payment_method", "UPI / Card")

    if not repair or not quote:
        flash("Unable to process payment.", "danger")
        return redirect(url_for("customer.repair_detail", repair_id=repair_id))

    payment = record_payment(
        repair_id=repair_id,
        quote_id=quote["id"],
        customer_id=current_user.id,
        shop_id=repair["shop_id"],
        amount=quote["final_quoted_amount"],
        payment_method=payment_method
    )

    flash(f"Payment of ₹{payment['amount']:,.0f} processed successfully! Transaction Ref: {payment['transaction_reference']}", "success")
    return redirect(url_for("customer.repair_detail", repair_id=repair_id))

@customer_bp.route("/repair/<repair_id>/review", methods=["POST"])
@login_required
@customer_required
def submit_review(repair_id):
    repair = get_repair_by_id(repair_id)
    if not repair or repair["customer_id"] != current_user.id:
        flash("Invalid repair request.", "danger")
        return redirect(url_for("customer.dashboard"))

    rating = int(request.form.get("rating", 5))
    comment = request.form.get("comment", "").strip()

    reviews = read_json("reviews.json")
    new_rev = {
        "id": generate_id("REV"),
        "repair_id": repair_id,
        "shop_id": repair["shop_id"],
        "customer_name": current_user.name,
        "rating": rating,
        "comment": comment,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    reviews.append(new_rev)
    write_json("reviews.json", reviews)

    flash("Thank you for your feedback!", "success")
    return redirect(url_for("customer.repair_detail", repair_id=repair_id))

@customer_bp.route("/notification/read/<notif_id>")
@login_required
@customer_required
def read_notif(notif_id):
    mark_notification_as_read(notif_id, current_user.id)
    return redirect(url_for("customer.dashboard"))
