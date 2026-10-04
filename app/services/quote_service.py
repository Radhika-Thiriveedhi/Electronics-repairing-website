from datetime import datetime
from app.storage.json_store import read_json, write_json
from app.storage.id_generator import generate_id
from app.services.notification_service import create_notification
from app.services.repair_service import update_repair_status, get_repair_by_id

def create_quote(repair_id, min_estimated_cost, max_estimated_cost, final_quoted_amount, estimated_completion_time, technician_notes=""):
    repairs = read_json("repairs.json")
    repair = next((r for r in repairs if r["id"] == repair_id), None)
    if not repair:
        return None, "Repair request not found."

    quotes = read_json("quotes.json")
    quote_id = generate_id("QTE")
    now_str = datetime.utcnow().isoformat() + "Z"

    new_quote = {
        "id": quote_id,
        "repair_id": repair_id,
        "min_estimated_cost": float(min_estimated_cost),
        "max_estimated_cost": float(max_estimated_cost),
        "final_quoted_amount": float(final_quoted_amount),
        "estimated_completion_time": estimated_completion_time.strip(),
        "technician_notes": technician_notes.strip(),
        "status": "Pending Customer Approval",
        "created_at": now_str
    }

    quotes.append(new_quote)
    write_json("quotes.json", quotes)

    # Attach quote_id to repair record and update status to "Waiting for Approval"
    for r in repairs:
        if r["id"] == repair_id:
            r["quote_id"] = quote_id
            r["status"] = "Waiting for Approval"
            r["updated_at"] = now_str
            break
    write_json("repairs.json", repairs)

    # Notify customer
    create_notification(
        user_id=repair["customer_id"],
        title="Quote Estimate Received",
        message=f"Shop estimated ₹{min_estimated_cost:,.0f}–₹{max_estimated_cost:,.0f} for your {repair['item_name']}. Please review and approve."
    )

    return new_quote, "Quote successfully created and sent to customer."

def get_quote_by_id(quote_id):
    quotes = read_json("quotes.json")
    return next((q for q in quotes if q["id"] == quote_id), None)

def get_quote_for_repair(repair_id):
    quotes = read_json("quotes.json")
    return next((q for q in quotes if q["repair_id"] == repair_id), None)

def respond_to_quote(quote_id, customer_id, decision):
    quotes = read_json("quotes.json")
    quote = next((q for q in quotes if q["id"] == quote_id), None)
    if not quote:
        return False, "Quote not found."

    repair = get_repair_by_id(quote["repair_id"])
    if not repair or repair["customer_id"] != customer_id:
        return False, "Unauthorized decision on this quote."

    if decision == "Approved":
        quote["status"] = "Approved"
        write_json("quotes.json", quotes)
        update_repair_status(repair["id"], "Repairing")

        # Notify shop owner
        users = read_json("users.json")
        shop_owner = next((u for u in users if u.get("shop_id") == repair["shop_id"] and u.get("role") == "shop"), None)
        if shop_owner:
            create_notification(
                user_id=shop_owner["id"],
                title="Quote Approved by Customer",
                message=f"Customer {repair['customer_name']} approved quote {quote_id} for {repair['item_name']}."
            )
        return True, "Quote approved! The repair is now in progress."

    elif decision == "Declined":
        quote["status"] = "Declined"
        write_json("quotes.json", quotes)
        update_repair_status(repair["id"], "Declined")

        users = read_json("users.json")
        shop_owner = next((u for u in users if u.get("shop_id") == repair["shop_id"] and u.get("role") == "shop"), None)
        if shop_owner:
            create_notification(
                user_id=shop_owner["id"],
                title="Quote Declined",
                message=f"Customer {repair['customer_name']} declined quote {quote_id} for {repair['item_name']}."
            )
        return True, "Quote declined."

    return False, "Invalid decision."

def record_payment(repair_id, quote_id, customer_id, shop_id, amount, payment_method="UPI / Card"):
    payments = read_json("payments.json")
    pay_id = generate_id("PAY")
    txn_ref = generate_id("TXN")
    now_str = datetime.utcnow().isoformat() + "Z"

    new_payment = {
        "id": pay_id,
        "repair_id": repair_id,
        "quote_id": quote_id,
        "customer_id": customer_id,
        "shop_id": shop_id,
        "amount": float(amount),
        "payment_method": payment_method,
        "status": "Completed",
        "transaction_reference": txn_ref,
        "created_at": now_str
    }

    payments.append(new_payment)
    write_json("payments.json", payments)

    update_repair_status(repair_id, "Completed")
    return new_payment
