from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.storage.json_store import read_json, write_json
from app.storage.id_generator import generate_id
from datetime import datetime

class User(UserMixin):
    def __init__(self, user_dict):
        self.id = user_dict.get("id")
        self.email = user_dict.get("email")
        self.password_hash = user_dict.get("password_hash")
        self.name = user_dict.get("name")
        self.role = user_dict.get("role")
        self.shop_id = user_dict.get("shop_id")
        self.phone = user_dict.get("phone", "")
        self.created_at = user_dict.get("created_at")

    @classmethod
    def get_by_id(cls, user_id):
        users = read_json("users.json")
        for u in users:
            if u.get("id") == user_id:
                return cls(u)
        return None

    @classmethod
    def get_by_email(cls, email):
        users = read_json("users.json")
        email_clean = email.strip().lower()
        for u in users:
            if u.get("email", "").strip().lower() == email_clean:
                return cls(u)
        return None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

def register_user(email, password, name, role, phone="", shop_id=None):
    if User.get_by_email(email):
        return None, "Email address is already registered."

    valid_roles = ["customer", "shop", "technician", "owner"]
    if role not in valid_roles:
        return None, "Invalid user role specified."

    users = read_json("users.json")
    new_user_id = generate_id("USR")
    
    # If shop user registration and no shop_id provided, create shop entry
    if role == "shop" and not shop_id:
        shops = read_json("shops.json")
        new_shop_id = generate_id("SHP")
        new_shop = {
            "id": new_shop_id,
            "name": f"{name}'s Repair Workshop",
            "owner_id": new_user_id,
            "categories": ["Laptops & Computers", "Smartphones & Tablets"],
            "rating": 5.0,
            "address": "Local Workshop Location",
            "contact": phone,
            "description": "General electronics, device repair and reuse specialist."
        }
        shops.append(new_shop)
        write_json("shops.json", shops)
        shop_id = new_shop_id

    new_user = {
        "id": new_user_id,
        "email": email.strip().lower(),
        "password_hash": generate_password_hash(password),
        "name": name.strip(),
        "role": role,
        "shop_id": shop_id,
        "phone": phone.strip(),
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    users.append(new_user)
    write_json("users.json", users)
    return User(new_user), "Registration successful."

def get_technicians_for_shop(shop_id):
    users = read_json("users.json")
    return [u for u in users if u.get("role") == "technician" and u.get("shop_id") == shop_id]
