import os
import json
import tempfile
from werkzeug.security import generate_password_hash

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

FILES = [
    "users.json",
    "shops.json",
    "repairs.json",
    "quotes.json",
    "payments.json",
    "notifications.json",
    "reviews.json",
    "parts.json"
]

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

def _get_file_path(filename: str) -> str:
    ensure_data_dir()
    return os.path.join(DATA_DIR, filename)

def read_json(filename: str) -> list:
    """Reads a JSON file safely. Initializes with seed data if file is missing or empty."""
    filepath = _get_file_path(filename)
    if not os.path.exists(filepath):
        seed_data = get_initial_seed_data().get(filename, [])
        write_json(filename, seed_data)
        return seed_data

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                seed_data = get_initial_seed_data().get(filename, [])
                write_json(filename, seed_data)
                return seed_data
            return json.loads(content)
    except (json.JSONDecodeError, OSError):
        seed_data = get_initial_seed_data().get(filename, [])
        write_json(filename, seed_data)
        return seed_data

def write_json(filename: str, data: list) -> bool:
    """Atomically writes data to a JSON file to prevent partial file corruption."""
    ensure_data_dir()
    filepath = _get_file_path(filename)
    dir_name = os.path.dirname(filepath)
    
    try:
        fd, temp_path = tempfile.mkstemp(dir=dir_name, prefix="tmp_fixloop_", suffix=".json")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(temp_path, filepath)
        return True
    except Exception as e:
        print(f"Error writing to {filename}: {e}")
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        return False

def get_initial_seed_data() -> dict:
    """Returns initial realistic seed data for FixLoop marketplace."""
    default_password_hash = generate_password_hash("password123")

    return {
        "users.json": [
            {
                "id": "usr_customer_1",
                "email": "customer@fixloop.org",
                "password_hash": default_password_hash,
                "name": "Aarav Sharma",
                "role": "customer",
                "phone": "+91 98765 43210",
                "created_at": "2026-09-15T10:00:00Z"
            },
            {
                "id": "usr_customer_2",
                "email": "priya@fixloop.org",
                "password_hash": default_password_hash,
                "name": "Priya Patel",
                "role": "customer",
                "phone": "+91 98123 45678",
                "created_at": "2026-09-18T11:30:00Z"
            },
            {
                "id": "usr_shop_1",
                "email": "shop@fixloop.org",
                "password_hash": default_password_hash,
                "name": "Rajesh Kumar (Apex Electronics)",
                "role": "shop",
                "shop_id": "shp_apex_101",
                "phone": "+91 99887 76655",
                "created_at": "2026-08-01T09:00:00Z"
            },
            {
                "id": "usr_shop_2",
                "email": "protech@fixloop.org",
                "password_hash": default_password_hash,
                "name": "Vikram Singh (ProTech Clinic)",
                "role": "shop",
                "shop_id": "shp_protech_102",
                "phone": "+91 97766 55443",
                "created_at": "2026-08-05T09:30:00Z"
            },
            {
                "id": "usr_tech_1",
                "email": "technician@fixloop.org",
                "password_hash": default_password_hash,
                "name": "Sanjay Verma",
                "role": "technician",
                "shop_id": "shp_apex_101",
                "phone": "+91 96543 21098",
                "created_at": "2026-08-10T10:00:00Z"
            },
            {
                "id": "usr_owner_1",
                "email": "owner@fixloop.org",
                "password_hash": default_password_hash,
                "name": "Elena Vance (Platform Owner)",
                "role": "owner",
                "phone": "+91 90000 11111",
                "created_at": "2026-01-01T08:00:00Z"
            }
        ],
        "shops.json": [
            {
                "id": "shp_apex_101",
                "name": "Apex Micro-Electronics Lab",
                "owner_id": "usr_shop_1",
                "categories": ["Laptops & Computers", "Smartphones & Tablets", "Home Audio & Appliances"],
                "rating": 4.8,
                "address": "104 MG Road, Sector 14, Bengaluru",
                "contact": "+91 99887 76655",
                "description": "Certified micro-soldering, motherboard level repair, and battery conditioning hub."
            },
            {
                "id": "shp_protech_102",
                "name": "ProTech Gear & Gadget Clinic",
                "owner_id": "usr_shop_2",
                "categories": ["Smartphones & Tablets", "Gaming Consoles", "Smart Wearables"],
                "rating": 4.7,
                "address": "22 Tech Park Ave, Whitefield, Bengaluru",
                "contact": "+91 97766 55443",
                "description": "Fast turnaround screen replacements, port fixes, and thermal repasting."
            },
            {
                "id": "shp_greenwheel_103",
                "name": "GreenWheel E-Mobility & Bike Hub",
                "owner_id": "usr_shop_3",
                "categories": ["E-Bikes & Scooters", "Bicycles & Mobility"],
                "rating": 4.9,
                "address": "58 Eco Hub Plaza, Indiranagar, Bengaluru",
                "contact": "+91 94455 66778",
                "description": "Lithium battery diagnostics, motor rewinding, hydraulic brake tuning."
            }
        ],
        "repairs.json": [
            {
                "id": "REP-2026-001",
                "customer_id": "usr_customer_1",
                "customer_name": "Aarav Sharma",
                "shop_id": "shp_apex_101",
                "shop_name": "Apex Micro-Electronics Lab",
                "technician_id": "usr_tech_1",
                "technician_name": "Sanjay Verma",
                "item_name": "Dell XPS 13 (2022)",
                "category": "Laptops & Computers",
                "fault_description": "Laptop charging problem - Type-C charging port works intermittently and stops charging when moved.",
                "delivery_type": "Pickup Required",
                "status": "Waiting for Approval",
                "quote_id": "QTE-101",
                "photo_filename": None,
                "created_at": "2026-10-01T14:20:00Z",
                "updated_at": "2026-10-02T10:15:00Z"
            },
            {
                "id": "REP-2026-002",
                "customer_id": "usr_customer_2",
                "customer_name": "Priya Patel",
                "shop_id": "shp_protech_102",
                "shop_name": "ProTech Gear & Gadget Clinic",
                "technician_id": None,
                "technician_name": None,
                "item_name": "iPhone 13 Pro",
                "category": "Smartphones & Tablets",
                "fault_description": "Cracked front glass digitizer after accidental drop. Touch input works fine.",
                "delivery_type": "Drop-off at Shop",
                "status": "Received",
                "quote_id": None,
                "photo_filename": None,
                "created_at": "2026-10-08T09:00:00Z",
                "updated_at": "2026-10-08T09:00:00Z"
            },
            {
                "id": "REP-2026-003",
                "customer_id": "usr_customer_1",
                "customer_name": "Aarav Sharma",
                "shop_id": "shp_apex_101",
                "shop_name": "Apex Micro-Electronics Lab",
                "technician_id": "usr_tech_1",
                "technician_name": "Sanjay Verma",
                "item_name": "Sony WH-1000XM4 Headphones",
                "category": "Home Audio & Appliances",
                "fault_description": "Right ear channel cuts out when active noise cancellation is switched on.",
                "delivery_type": "Drop-off at Shop",
                "status": "Completed",
                "quote_id": "QTE-102",
                "photo_filename": None,
                "created_at": "2026-09-20T11:00:00Z",
                "updated_at": "2026-09-22T16:30:00Z"
            }
        ],
        "quotes.json": [
            {
                "id": "QTE-101",
                "repair_id": "REP-2026-001",
                "min_estimated_cost": 800,
                "max_estimated_cost": 1200,
                "final_quoted_amount": 950,
                "estimated_completion_time": "2 Business Days",
                "technician_notes": "DC-in Type-C jack daughterboard replacement and internal thermal re-pasting.",
                "status": "Pending Customer Approval",
                "created_at": "2026-10-02T10:15:00Z"
            },
            {
                "id": "QTE-102",
                "repair_id": "REP-2026-003",
                "min_estimated_cost": 1500,
                "max_estimated_cost": 1800,
                "final_quoted_amount": 1500,
                "estimated_completion_time": "1 Business Day",
                "technician_notes": "Flex cable ribbon replacement and headband wiring re-soldering.",
                "status": "Approved",
                "created_at": "2026-09-21T09:30:00Z"
            }
        ],
        "payments.json": [
            {
                "id": "PAY-901",
                "repair_id": "REP-2026-003",
                "quote_id": "QTE-102",
                "customer_id": "usr_customer_1",
                "shop_id": "shp_apex_101",
                "amount": 1500,
                "payment_method": "UPI / Online Transfer",
                "status": "Completed",
                "transaction_reference": "TXN-FL-889012",
                "created_at": "2026-09-22T16:30:00Z"
            }
        ],
        "notifications.json": [
            {
                "id": "NOT-301",
                "user_id": "usr_customer_1",
                "title": "Quote Received",
                "message": "Apex Micro-Electronics Lab sent a repair estimate of ₹800–₹1,200 for your Dell XPS 13 (2022).",
                "read": False,
                "created_at": "2026-10-02T10:15:00Z"
            }
        ],
        "reviews.json": [
            {
                "id": "REV-801",
                "repair_id": "REP-2026-003",
                "shop_id": "shp_apex_101",
                "customer_name": "Aarav Sharma",
                "rating": 5,
                "comment": "Flawless repair! Fixed my Sony noise-canceling headphones in just 1 day instead of buying a replacement. Saved ₹20,000!",
                "created_at": "2026-09-23T10:00:00Z"
            }
        ],
        "parts.json": [
            {
                "id": "PRT-401",
                "shop_id": "shp_apex_101",
                "name": "USB-C Charging Port Daughterboard (Dell XPS)",
                "sku": "PRT-DELL-USBC",
                "stock_quantity": 4,
                "cost_price": 350,
                "selling_price": 600
            },
            {
                "id": "PRT-402",
                "shop_id": "shp_apex_101",
                "name": "Thermal Paste Kryonaut (1g)",
                "sku": "PRT-THM-KRYO",
                "stock_quantity": 12,
                "cost_price": 150,
                "selling_price": 300
            }
        ]
    }

def init_all_json_files():
    """Initializes missing JSON files with seed data."""
    ensure_data_dir()
    seed_data = get_initial_seed_data()
    for filename, default_content in seed_data.items():
        filepath = _get_file_path(filename)
        if not os.path.exists(filepath):
            write_json(filename, default_content)
