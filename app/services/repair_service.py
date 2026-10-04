from datetime import datetime
from app.storage.json_store import read_json, write_json
from app.storage.id_generator import generate_id
from app.services.notification_service import create_notification

STATUS_WORKFLOW = [
    "Received",
    "Diagnosing",
    "Waiting for Approval",
    "Repairing",
    "Ready for Collection",
    "Completed"
]

def create_repair_request(customer_id, customer_name, shop_id, item_name, category, fault_description, delivery_type, photo_filename=None):
    shops = read_json("shops.json")
    shop = next((s for s in shops if s["id"] == shop_id), None)
    shop_name = shop["name"] if shop else "Local Repair Shop"

    repairs = read_json("repairs.json")
    repair_id = generate_id("REP")
    now_str = datetime.utcnow().isoformat() + "Z"

    new_repair = {
        "id": repair_id,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "shop_id": shop_id,
        "shop_name": shop_name,
        "technician_id": None,
        "technician_name": None,
        "item_name": item_name.strip(),
        "category": category.strip(),
        "fault_description": fault_description.strip(),
        "delivery_type": delivery_type,
        "status": "Received",
        "quote_id": None,
        "photo_filename": photo_filename,
        "parts_used": [],
        "diagnosis_notes": "",
        "created_at": now_str,
        "updated_at": now_str
    }

    repairs.append(new_repair)
    write_json("repairs.json", repairs)

    # Notify shop owner if user exists
    users = read_json("users.json")
    shop_owner = next((u for u in users if u.get("shop_id") == shop_id and u.get("role") == "shop"), None)
    if shop_owner:
        create_notification(
            user_id=shop_owner["id"],
            title="New Repair Request",
            message=f"New request '{item_name}' submitted by {customer_name}."
        )

    return new_repair

def get_repairs_for_customer(customer_id):
    repairs = read_json("repairs.json")
    return [r for r in repairs if r.get("customer_id") == customer_id]

def get_repairs_for_shop(shop_id):
    repairs = read_json("repairs.json")
    return [r for r in repairs if r.get("shop_id") == shop_id]

def get_repairs_for_technician(technician_id):
    repairs = read_json("repairs.json")
    return [r for r in repairs if r.get("technician_id") == technician_id]

def get_all_repairs():
    return read_json("repairs.json")

def get_repair_by_id(repair_id):
    repairs = read_json("repairs.json")
    return next((r for r in repairs if r["id"] == repair_id), None)

def update_repair_status(repair_id, new_status, updated_by_user_id=None):
    repairs = read_json("repairs.json")
    for r in repairs:
        if r["id"] == repair_id:
            old_status = r["status"]
            r["status"] = new_status
            r["updated_at"] = datetime.utcnow().isoformat() + "Z"
            write_json("repairs.json", repairs)

            # Notify customer
            create_notification(
                user_id=r["customer_id"],
                title="Repair Status Updated",
                message=f"Your repair for '{r['item_name']}' is now: {new_status}."
            )
            return True, f"Status updated from {old_status} to {new_status}."
    return False, "Repair record not found."

def assign_technician(repair_id, technician_id):
    users = read_json("users.json")
    tech = next((u for u in users if u["id"] == technician_id and u["role"] == "technician"), None)
    if not tech:
        return False, "Technician not found."

    repairs = read_json("repairs.json")
    for r in repairs:
        if r["id"] == repair_id:
            r["technician_id"] = tech["id"]
            r["technician_name"] = tech["name"]
            r["updated_at"] = datetime.utcnow().isoformat() + "Z"
            write_json("repairs.json", repairs)

            create_notification(
                user_id=tech["id"],
                title="Job Assigned",
                message=f"You have been assigned to repair job '{r['item_name']}' ({r['id']})."
            )
            return True, f"Job assigned to technician {tech['name']}."
    return False, "Repair record not found."

def update_technician_notes_and_parts(repair_id, diagnosis_notes, parts_used=None):
    repairs = read_json("repairs.json")
    for r in repairs:
        if r["id"] == repair_id:
            if diagnosis_notes is not None:
                r["diagnosis_notes"] = diagnosis_notes.strip()
            if parts_used is not None:
                r["parts_used"] = parts_used
            r["updated_at"] = datetime.utcnow().isoformat() + "Z"
            write_json("repairs.json", repairs)
            return True, "Technician notes and parts updated."
    return False, "Repair record not found."
