from flask import Blueprint, render_template
from app.storage.json_store import read_json

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
def home():
    shops = read_json("shops.json")
    reviews = read_json("reviews.json")
    repairs = read_json("repairs.json")
    
    completed_count = sum(1 for r in repairs if r.get("status") == "Completed")
    shops_count = len(shops)

    return render_template(
        "home.html",
        shops=shops[:3],
        reviews=reviews[:3],
        completed_count=completed_count,
        shops_count=shops_count
    )

@public_bp.route("/services")
def services():
    shops = read_json("shops.json")
    categories = [
        {"name": "Laptops & Computers", "icon": "laptop", "desc": "Motherboard micro-soldering, charging port repairs, screen replacements, thermal repasting."},
        {"name": "Smartphones & Tablets", "icon": "mobile-alt", "desc": "Display digitizers, battery replacements, camera module fixes, water damage recovery."},
        {"name": "E-Bikes & Scooters", "icon": "biking", "desc": "Lithium battery pack conditioning, motor controller rewinding, hydraulic brake tuning."},
        {"name": "Home Audio & Appliances", "icon": "headphones", "desc": "Amplifier repair, headphone driver/ribbon wire replacements, PCB diagnostics."},
        {"name": "Gaming Consoles", "icon": "gamepad", "desc": "HDMI port replacements, cooling fan swaps, optical drive laser alignment."},
        {"name": "Smart Wearables", "icon": "watch", "desc": "Smartwatch screen replacements, battery swaps, sensor glass repairs."}
    ]
    return render_template("services.html", shops=shops, categories=categories)
