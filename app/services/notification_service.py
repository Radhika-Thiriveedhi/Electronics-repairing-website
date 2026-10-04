from datetime import datetime
from app.storage.json_store import read_json, write_json
from app.storage.id_generator import generate_id

def create_notification(user_id, title, message):
    notifications = read_json("notifications.json")
    notif_id = generate_id("NOT")
    now_str = datetime.utcnow().isoformat() + "Z"

    new_notif = {
        "id": notif_id,
        "user_id": user_id,
        "title": title.strip(),
        "message": message.strip(),
        "read": False,
        "created_at": now_str
    }

    notifications.insert(0, new_notif)
    write_json("notifications.json", notifications)
    return new_notif

def get_notifications_for_user(user_id):
    notifications = read_json("notifications.json")
    return [n for n in notifications if n.get("user_id") == user_id]

def mark_notification_as_read(notif_id, user_id):
    notifications = read_json("notifications.json")
    for n in notifications:
        if n["id"] == notif_id and n.get("user_id") == user_id:
            n["read"] = True
            write_json("notifications.json", notifications)
            return True
    return False
