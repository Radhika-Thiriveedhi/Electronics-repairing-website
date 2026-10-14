import pytest
from app import create_app
from app.services.repair_service import (
    create_repair_request,
    get_repair_by_id,
    update_repair_status,
    assign_technician
)

@pytest.fixture
def app_ctx():
    app = create_app()
    app.config["TESTING"] = True
    return app

def test_create_and_update_repair(app_ctx):
    with app_ctx.app_context():
        repair = create_repair_request(
            customer_id="usr_customer_1",
            customer_name="Aarav Sharma",
            shop_id="shp_apex_101",
            item_name="MacBook Pro 16",
            category="Laptops & Computers",
            fault_description="Screen backlight flickering",
            delivery_type="Drop-off at Shop"
        )
        assert repair is not None
        assert repair["status"] == "Received"

        # Update status
        success, msg = update_repair_status(repair["id"], "Diagnosing")
        assert success is True
        
        fetched = get_repair_by_id(repair["id"])
        assert fetched["status"] == "Diagnosing"

def test_assign_technician_to_job(app_ctx):
    with app_ctx.app_context():
        repair = create_repair_request(
            customer_id="usr_customer_1",
            customer_name="Aarav Sharma",
            shop_id="shp_apex_101",
            item_name="iPad Air",
            category="Smartphones & Tablets",
            fault_description="Battery draining fast",
            delivery_type="Drop-off at Shop"
        )
        success, msg = assign_technician(repair["id"], "usr_tech_1")
        assert success is True
        fetched = get_repair_by_id(repair["id"])
        assert fetched["technician_name"] == "Sanjay Verma"
