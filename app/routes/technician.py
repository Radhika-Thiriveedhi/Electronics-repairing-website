from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.services.repair_service import (
    get_repairs_for_technician,
    get_repair_by_id,
    update_repair_status,
    update_technician_notes_and_parts,
    STATUS_WORKFLOW
)
from app.services.quote_service import get_quote_for_repair
from app.storage.json_store import read_json

technician_bp = Blueprint("technician", __name__, url_prefix="/technician")

def technician_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "technician":
            flash("Access restricted to Technicians.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@technician_bp.route("/dashboard")
@login_required
@technician_required
def dashboard():
    repairs = get_repairs_for_technician(current_user.id)
    # Also fetch unassigned jobs for their shop
    all_shop_repairs = [r for r in read_json("repairs.json") if r.get("shop_id") == current_user.shop_id and not r.get("technician_id")]
    
    return render_template(
        "technician/dashboard.html",
        assigned_jobs=repairs,
        unassigned_jobs=all_shop_repairs
    )

@technician_bp.route("/job/<repair_id>")
@login_required
@technician_required
def job_detail(repair_id):
    repair = get_repair_by_id(repair_id)
    if not repair or (repair.get("shop_id") != current_user.shop_id):
        flash("Job not found or access denied.", "danger")
        return redirect(url_for("technician.dashboard"))

    quote = get_quote_for_repair(repair_id)
    shop_parts = [p for p in read_json("parts.json") if p.get("shop_id") == current_user.shop_id]

    return render_template(
        "technician/job_detail.html",
        repair=repair,
        quote=quote,
        workflow=STATUS_WORKFLOW,
        shop_parts=shop_parts
    )

@technician_bp.route("/update-status/<repair_id>", methods=["POST"])
@login_required
@technician_required
def update_status(repair_id):
    new_status = request.form.get("new_status")
    repair = get_repair_by_id(repair_id)
    if not repair or (repair.get("shop_id") != current_user.shop_id):
        flash("Job not found.", "danger")
        return redirect(url_for("technician.dashboard"))

    if new_status in STATUS_WORKFLOW:
        success, msg = update_repair_status(repair_id, new_status, current_user.id)
        if success:
            flash(msg, "success")
        else:
            flash(msg, "danger")
    else:
        flash("Invalid status selected.", "warning")

    return redirect(url_for("technician.job_detail", repair_id=repair_id))

@technician_bp.route("/update-notes/<repair_id>", methods=["POST"])
@login_required
@technician_required
def update_notes(repair_id):
    notes = request.form.get("diagnosis_notes", "")
    part_names = request.form.getlist("parts_used")

    success, msg = update_technician_notes_and_parts(repair_id, notes, part_names)
    if success:
        flash("Work notes and parts updated.", "success")
    else:
        flash(msg, "danger")

    return redirect(url_for("technician.job_detail", repair_id=repair_id))
